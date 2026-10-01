"use client";

import { useEffect, useMemo, useRef, useState, Suspense, type FormEvent } from "react";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";
import {
  getCurrentUser,
  searchPlaces,
  nearbyPlaces,
  resolveAttraction,
  listAttractions,
  listFavorites,
  addFavorite,
  removeFavorite,
  extractErrorMessage,
  type Attraction,
  type CuratedCategory,
  type Place,
  type Favorite,
  type PlaceBoundary,
} from "@/lib/api";
import { haversineDistanceKm, formatDistanceKm } from "@/lib/geo";
import { CATEGORY_LABELS, CATEGORY_ORDER, categoryLabel, categoryIcon, isFoodCategory, isHotelCategory } from "@/lib/attractionCategories";
import PlaceSheet from "@/components/PlaceSheet";
import { triggerAiHelper, clearPlaceContext } from "@/lib/aiHelper";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const FALLBACK_CENTER: [number, number] = [20.5937, 78.9629]; // India, roughly

type CategoryFilter = "all" | CuratedCategory | "restaurants" | "hotels";

const FILTER_CHIPS: { id: CategoryFilter; label: string; icon: string }[] = [
  { id: "all", label: "All", icon: "🗺️" },
  ...CATEGORY_ORDER.map((c) => ({ id: c as CategoryFilter, label: CATEGORY_LABELS[c], icon: categoryIcon(c) })),
  { id: "restaurants", label: "Restaurants", icon: "🍽️" },
  { id: "hotels", label: "Hotels", icon: "🏨" },
];

type ListItem = { type: "attraction"; data: Attraction } | { type: "place"; data: Place };

function placeKey(a: { name: string; lat: number; lng: number }): string {
  return `${a.name}|${a.lat}|${a.lng}`;
}

function cleanAdminName(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(
      /\b(district|town|city|municipal\s+council|nagar\s+parishad|nagar\s+panchayat|cantonment|taluka|taluk|tehsil|tahsil|sub-district|division|urban|rural)\b/gi,
      ""
    )
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function districtMatches(
  attraction: Attraction,
  district: string,
  scopeKind: "district" | "city" | null
): boolean {
  const scope = cleanAdminName(district);
  if (!scope) return false;

  if (scopeKind === "district") {
    // A district result must use the record's district field, never a text
    // fragment in its street/area. "Nagpur Road" in a Chandrapur address is
    // not a Nagpur-district attraction.
    return cleanAdminName(attraction.district ?? "") === scope;
  }

  // City searches remain narrower than their parent district: Ramtek lives
  // in Nagpur district, but its curated entries are identified by area or name.
  const attractionArea = cleanAdminName(attraction.area ?? "");
  const attractionName = cleanAdminName(attraction.name ?? "");

  // Match if attraction area or name contains the search scope (e.g. "Ramtek")
  // or vice versa (e.g. searching "Ramtek Town" matches "Ramtek city", "Near Ramtek city",
  // "Nagardhan, near Ramtek city", "Ramtek Fort Temple", etc.)
  if (attractionArea && (attractionArea.includes(scope) || scope.includes(attractionArea))) {
    return true;
  }
  if (attractionName && attractionName.includes(scope)) {
    return true;
  }

  // Keyword token fallback for multi-word city names
  const scopeTokens = scope.split(" ").filter((t) => t.length >= 3);
  if (scopeTokens.some((t) => attractionArea.includes(t) || attractionName.includes(t))) {
    return true;
  }

  return false;
}

// Curated restaurants/hotels near a specific place search (as opposed to a
// whole-district browse, which matches by district instead — see below).
// District-matching alone isn't "near Tadoba", it's "anywhere in Chandrapur
// district", which could be 50km+ away — so for a specific-place search we
// only surface curated entries genuinely close to it.
const CURATED_NEARBY_RADIUS_KM = 35;

function nearestCurated(
  list: Attraction[],
  isCategory: (c: string) => boolean,
  center: { lat: number; lng: number } | null
): Attraction[] {
  if (!center) return [];
  return list
    .filter((a) => isCategory(a.category))
    .map((a) => ({ a, km: haversineDistanceKm(center.lat, center.lng, a.lat, a.lng) }))
    .filter(({ km }) => km <= CURATED_NEARBY_RADIUS_KM)
    .sort((x, y) => x.km - y.km)
    .map(({ a }) => a);
}

// A query that names one of our own curated *sightseeing* attractions (e.g.
// "tadoba" for "Tadoba-Andhari Tiger Reserve") should resolve to that same
// curated page — with its rating, booking link, and curated notes — rather
// than a bare OSM search hit for the same place. Restricted to the five
// sightseeing categories (CATEGORY_ORDER) and source "curated" because a
// famous landmark's name also shows up on unrelated things that shouldn't
// win this match: businesses named after it (e.g. the several
// "tadoba_safari_resort" hotels trading on the name) and stray "community"
// rows a previous OSM-place search may have persisted for the landmark
// itself under a different name (e.g. a same-named village, or a
// differently-titled park entry) — those would otherwise make the match
// ambiguous and silently fall back to a raw OSM hit instead.
function findCuratedMatch(list: Attraction[], query: string): Attraction | undefined {
  if (query.length < 3) return undefined;
  const q = query.toLowerCase();
  const matches = list.filter(
    (a) =>
      a.source === "curated" &&
      (CATEGORY_ORDER as string[]).includes(a.category) &&
      a.name.toLowerCase().includes(q)
  );
  return matches.length === 1 ? matches[0] : undefined;
}

// Only treat a match as a browsable administrative area (triggering the
// "show this whole district" flow) when it carries a real boundary polygon.
// Nominatim also tags plain point-only places — e.g. a small village that
// happens to share a name with a nearby reserve — as `is_area`, and without
// this check searching for a specific attraction like "Tadoba" would wrongly
// pick up the "Tadoba" village node and dump the entire Chandrapur district's
// curated list instead of just that attraction.
function pickAreaResult(results: Place[]): Place | undefined {
  // The backend puts a known Maharashtra district first for an exact
  // district search (e.g. "Nagpur"). City searches keep their own boundary.
  return results.find((r) => r.is_area && r.boundary && r.scope_kind === "district")
    ?? results.find((r) => r.is_area && r.boundary);
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [checking, setChecking] = useState(true);

  const [allCurated, setAllCurated] = useState<Attraction[]>([]);
  const [allCuratedLoading, setAllCuratedLoading] = useState(true);
  const [allCuratedError, setAllCuratedError] = useState<string | null>(null);

  const [query, setQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<Place[] | null>(null);
  // The curated attraction a specific-place search resolved to (see
  // findCuratedMatch) — surfaced as its own card in the results list rather
  // than auto-opened, so the user picks it the same way they'd pick any
  // other search result.
  const [curatedMatch, setCuratedMatch] = useState<Attraction | null>(null);
  const [activeDistrict, setActiveDistrict] = useState<string | null>(null);
  const [activeScopeKind, setActiveScopeKind] = useState<"district" | "city" | null>(null);
  const [boundary, setBoundary] = useState<PlaceBoundary | null>(null);
  const [boundaryKey, setBoundaryKey] = useState<string>("");
  const [focusCenter, setFocusCenter] = useState<{ lat: number; lng: number } | null>(null);

  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");
  const [nearbyResults, setNearbyResults] = useState<Place[]>([]);
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [nearbyError, setNearbyError] = useState<string | null>(null);

  const [selectedAttraction, setSelectedAttraction] = useState<Attraction | null>(null);
  const [resolving, setResolving] = useState(false);

  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [routePositions, setRoutePositions] = useState<[number, number][] | null>(null);

  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [favoriteBusy, setFavoriteBusy] = useState(false);

  // Guards against an older, slower search/loadDistrict response clobbering
  // a newer one that happened to resolve first (e.g. the initial featured-
  // district fetch racing a manual search fired right after page load).
  const searchSeqRef = useRef(0);

  // Lets handleSearch await the curated fetch instead of racing it — typing
  // and hitting search fast enough (very plausible on page load) could
  // otherwise land while allCuratedLoading is still true, silently skipping
  // the curated-attraction match and falling back to a raw OSM result for a
  // place, like Tadoba, that's actually in the curated dataset.
  const allCuratedPromiseRef = useRef<Promise<Attraction[]> | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }
    getCurrentUser()
      .catch(() => router.replace("/login"))
      .finally(() => setChecking(false));
  }, [router]);

  // Back to the neutral starting state: an India-wide map and an empty list
  // until the user searches for something. Nothing is preloaded — showing a
  // district's places without being asked read as confusing.
  function resetToDefault() {
    ++searchSeqRef.current; // discard any search still in flight
    setQuery("");
    setSearchResults(null);
    setCuratedMatch(null);
    setSearchError(null);
    setSearchLoading(false);
    setActiveDistrict(null);
    setActiveScopeKind(null);
    setBoundary(null);
    setBoundaryKey("");
    setFocusCenter(null);
    setCategoryFilter("all");
    setSelectedAttraction(null);
    setRoutePositions(null);
    clearPlaceContext();
  }

  // Fetches the full curated dataset (Chandrapur's tourist attractions and
  // restaurants today, more later) that the district view and the
  // Restaurants/Hotels chips both depend on, retrying once before giving up.
  // Pure data-fetching — no state here — so both the mount effect and the
  // retry button can drive it with only their own `.then`/`.catch`.
  async function fetchAllCurated(): Promise<Attraction[]> {
    try {
      return await listAttractions();
    } catch {
      await new Promise((r) => setTimeout(r, 800));
      return listAttractions();
    }
  }

  useEffect(() => {
    if (checking) return;
    // This list silently staying empty previously meant curated restaurants
    // could vanish for the rest of a session after one transient failure
    // (e.g. a backend restart mid-request) with no visible sign of it.
    const promise = fetchAllCurated();
    allCuratedPromiseRef.current = promise;
    promise
      .then((data) => {
        setAllCurated(data);
        setAllCuratedLoading(false);
      })
      .catch((err) => {
        setAllCuratedError(extractErrorMessage(err, "Could not load Chandrapur's curated places."));
        setAllCuratedLoading(false);
      });
    listFavorites()
      .then(setFavorites)
      .catch(() => {
        // Non-critical — the star button just falls back to "not favourited".
      });
  }, [checking]);

  useEffect(() => {
    const categoryParam = searchParams.get("category");
    if (!allCuratedLoading && (categoryParam === "restaurants" || categoryParam === "hotels")) {
      selectCategory(categoryParam);
      // Clean up the URL without triggering a full page reload or scrolling
      router.replace("/dashboard", { scroll: false });
    }
  }, [searchParams, allCuratedLoading]);

  // Extracted so both the mount effect and a manual retry (see PlaceSheet's
  // "Enable location access" prompt) can request it — a one-shot call on
  // mount alone means granting permission *after* an initial denial/timeout
  // would never be picked up without a full page reload.
  function requestUserLocation() {
    if (!window.isSecureContext) {
      setLocationError("Location needs a secure (https) connection — this page is loaded over http.");
      return;
    }
    if (!navigator.geolocation) {
      setLocationError("This browser doesn't support location access.");
      return;
    }
    setLocationError(null);

    // Fast resolution: allow cached location up to 5 minutes old
    const fastOptions: PositionOptions = {
      enableHighAccuracy: false,
      timeout: 8000,
      maximumAge: 300000,
    };

    const accurateOptions: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 12000,
      maximumAge: 60000,
    };

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocationError(null);
      },
      () => {
        // Retry with high accuracy if fast resolution didn't produce a fix
        navigator.geolocation.getCurrentPosition(
          (accuratePos) => {
            setUserLocation({ lat: accuratePos.coords.latitude, lng: accuratePos.coords.longitude });
            setLocationError(null);
          },
          (err) => {
            setLocationError(
              err.code === err.PERMISSION_DENIED
                ? "Location access is blocked for this site — allow it in your browser's site settings, then try again."
                : err.code === err.TIMEOUT
                  ? "Timed out getting your location. Try again."
                  : "Your device couldn't determine your location. Check that Location Services is turned on in macOS System Settings > Privacy & Security > Location Services."
            );
          },
          accurateOptions
        );
      },
      fastOptions
    );
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      requestUserLocation();
    }, 0);

    // Listen for browser permission change (e.g. user clicks "Allow" in browser bar)
    if (typeof navigator !== "undefined" && navigator.permissions && navigator.permissions.query) {
      navigator.permissions
        .query({ name: "geolocation" })
        .then((permissionStatus) => {
          permissionStatus.onchange = () => {
            if (permissionStatus.state === "granted") {
              requestUserLocation();
            }
          };
        })
        .catch(() => {});
    }

    // Set up a background watcher to catch location fix when ready
    let watchId: number | null = null;
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      watchId = navigator.geolocation.watchPosition(
        (pos) => {
          setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
          setLocationError(null);
        },
        () => {},
        { enableHighAccuracy: false, maximumAge: 300000, timeout: 15000 }
      );
    }

    return () => {
      clearTimeout(timer);
      if (watchId !== null && typeof navigator !== "undefined" && navigator.geolocation) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, []);

  async function openPlace(place: Place) {
    setResolving(true);
    setSearchError(null);
    try {
      const attraction = await resolveAttraction(place);
      setSelectedAttraction(attraction);
      setFocusCenter({ lat: attraction.lat, lng: attraction.lng });
      triggerAiHelper({
        placeId: attraction.id,
        placeName: attraction.name,
        district: attraction.district || activeDistrict,
        category: attraction.category,
        area: attraction.area,
      });
    } catch (err) {
      setSearchError(extractErrorMessage(err, "Could not open this place."));
    } finally {
      setResolving(false);
    }
  }

  function openAttraction(attraction: Attraction) {
    setSelectedAttraction(attraction);
    setFocusCenter({ lat: attraction.lat, lng: attraction.lng });
    triggerAiHelper({
      placeId: attraction.id,
      placeName: attraction.name,
      district: attraction.district || activeDistrict,
      category: attraction.category,
      area: attraction.area,
    });
  }

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    const seq = ++searchSeqRef.current;
    setCategoryFilter("all");
    setSelectedAttraction(null);
    setSearchLoading(true);
    setSearchError(null);
    try {
      const results = await searchPlaces(q);
      if (seq !== searchSeqRef.current) return; // a newer search has since started
      const area = pickAreaResult(results);
      if (area) {
        setBoundary(area.boundary ?? null);
        setBoundaryKey(`${area.osm_type ?? "area"}:${area.osm_id ?? area.name}`);
        setFocusCenter({ lat: area.lat, lng: area.lng });
        // Keep the area the user searched for. Nominatim's `state_district`
        // reports Ramtek as "Nagpur", which is its parent district and would
        // otherwise incorrectly turn a Ramtek search into a Nagpur-wide list.
        setActiveDistrict(area.name);
        setActiveScopeKind(area.scope_kind ?? "city");
        setSearchResults(null);
        setCuratedMatch(null);
      } else {
        setBoundary(null);
        setBoundaryKey("");
        setActiveDistrict(null);
        setActiveScopeKind(null);
        setSearchResults(results);
        // A curated match (see findCuratedMatch) is surfaced as its own
        // card in the list — same as any other search result — rather than
        // auto-opened, so the user picks it explicitly like they would
        // Tadoba-Andhari Tiger Reserve from the Chandrapur/Wildlife list.
        // Awaits the curated fetch itself (rather than checking
        // allCuratedLoading) so a search fired quickly after page load —
        // before that fetch has resolved — doesn't race it and silently
        // miss the match.
        const curatedList = allCuratedPromiseRef.current
          ? await allCuratedPromiseRef.current.catch(() => allCurated)
          : allCurated;
        if (seq !== searchSeqRef.current) return; // a newer search started while we waited
        const curatedMatch = findCuratedMatch(curatedList, q);
        setCuratedMatch(curatedMatch ?? null);
        if (curatedMatch) {
          // Center the map on the curated, verified coordinates rather than
          // whatever Nominatim happened to return first (e.g. the wrong
          // "Tadoba" village node instead of the actual reserve).
          setFocusCenter({ lat: curatedMatch.lat, lng: curatedMatch.lng });
        } else if (results[0]) {
          setFocusCenter({ lat: results[0].lat, lng: results[0].lng });
          if (results.length === 1) await openPlace(results[0]);
        }
      }
      if (results.length === 0) setSearchError(`No results for "${q}".`);
    } catch (err) {
      if (seq !== searchSeqRef.current) return;
      setSearchError(extractErrorMessage(err, "Could not search. Try again."));
    } finally {
      if (seq === searchSeqRef.current) setSearchLoading(false);
    }
  }

  async function selectCategory(cat: CategoryFilter) {
    setCategoryFilter(cat);
    setSelectedAttraction(null);
    if (cat !== "restaurants" && cat !== "hotels") return;

    // Chandrapur has its own curated restaurant and hotel directories —
    // prefer them over a live OSM search. While browsing a whole district,
    // match by district (comprehensive coverage); for a specific-place
    // search, match by proximity instead — see nearestCurated. If the
    // curated list is still loading (or failed and hasn't retried yet),
    // wait rather than assuming "no curated coverage" and firing an OSM
    // search that would show a misleading empty result.
    // The dashboard is deliberately search-led: location permission alone
    // must not pull Chandrapur's curated directory into an otherwise empty
    // India-wide map. The dedicated Food/Hotels near-me pages are the place
    // for a location-only browse.
    const searchCenter = focusCenter || userLocation;
    if (!activeDistrict && !searchCenter) {
      setNearbyResults([]);
      setNearbyError("Search for a place first, or enable location access.");
      return;
    }
    if (allCuratedLoading) return;
    const isCuratedCategory = cat === "restaurants" ? isFoodCategory : isHotelCategory;
    const curated = nearestCurated(allCurated, isCuratedCategory, searchCenter);
    if (curated.length > 0) return;

    if (!searchCenter) {
      setNearbyError("Search a place first, or enable location access.");
      return;
    }
    setNearbyLoading(true);
    setNearbyError(null);
    try {
      const osmCategory = cat === "restaurants" ? "amenity~restaurant|cafe|fast_food" : "tourism=hotel";
      const results = await nearbyPlaces(searchCenter.lat, searchCenter.lng, 35000, osmCategory);
      setNearbyResults(results);
    } catch {
      setNearbyError(`Could not load nearby ${cat}.`);
    } finally {
      setNearbyLoading(false);
    }
  }

  const displayList: ListItem[] = useMemo(() => {
    if (categoryFilter !== "all" && categoryFilter !== "restaurants" && categoryFilter !== "hotels") {
      // Category chips filter the area that's been searched — with nothing
      // searched yet there's nothing to filter, so don't surface places from
      // a district the user never asked about.
      if (!activeDistrict) return [];
      return allCurated
        .filter((a) => a.category === categoryFilter && districtMatches(a, activeDistrict, activeScopeKind))
        .map((data) => ({ type: "attraction", data }) as const);
    }
    if (categoryFilter === "restaurants" || categoryFilter === "hotels") {
      // Use focusCenter or fallback to userLocation if they haven't searched yet.
      const searchCenter = focusCenter || userLocation;
      if (!searchCenter) return [];
      const isCuratedCategory = categoryFilter === "restaurants" ? isFoodCategory : isHotelCategory;
      const curated = nearestCurated(allCurated, isCuratedCategory, searchCenter);
      if (curated.length > 0) {
        return curated.map((data) => ({ type: "attraction", data }) as const);
      }
      return nearbyResults.map((data) => ({ type: "place", data }) as const);
    }
    // "All" means all tourist attractions — restaurants and hotels only show
    // up when their own chip is picked, so they don't crowd out sightseeing
    // spots on the default view just because they happen to sort first.
    if (activeDistrict) {
      return allCurated
        .filter(
          (a) =>
            !isFoodCategory(a.category) &&
            !isHotelCategory(a.category) &&
            districtMatches(a, activeDistrict, activeScopeKind)
        )
        .map((data) => ({ type: "attraction", data }) as const);
    }
    if (searchResults) {
      // The curated match (if any) is the same real-world place as one of
      // the raw OSM hits — drop that duplicate rather than showing both,
      // and surface the curated card (richer data, opens the curated page)
      // in its place.
      const items: ListItem[] = searchResults
        .filter(
          (p) =>
            !curatedMatch || haversineDistanceKm(p.lat, p.lng, curatedMatch.lat, curatedMatch.lng) > 2
        )
        .map((data) => ({ type: "place", data }) as const);
      if (curatedMatch) items.unshift({ type: "attraction", data: curatedMatch });
      return items;
    }
    // Nothing searched yet — start empty rather than preloading a district.
    return [];
  }, [categoryFilter, allCurated, activeDistrict, activeScopeKind, searchResults, curatedMatch, nearbyResults, focusCenter, userLocation]);

  // Wildlife/Lake & Nature/etc. only ever return results while browsing a
  // whole district's curated list — for a search that resolved to a specific
  // site instead (like "Tadoba"), those chips can't do anything, so keep
  // only the two that still work: Restaurants and Hotels (via curated
  // cross-reference or a live nearby search).
  const visibleChips = activeDistrict
    ? FILTER_CHIPS
    : FILTER_CHIPS.filter((c) => c.id === "all" || c.id === "restaurants" || c.id === "hotels");

  const listPlaces = displayList.map((item) => ({
    name: item.data.name,
    lat: item.data.lat,
    lng: item.data.lng,
    category: item.type === "attraction" ? categoryLabel(item.data.category) : item.data.category,
  }));
  const mapPlaces = useMemo(() => {
    if (!selectedAttraction) return listPlaces;
    const already = listPlaces.some(
      (p) => p.lat === selectedAttraction.lat && p.lng === selectedAttraction.lng
    );
    if (already) return listPlaces;
    return [
      ...listPlaces,
      {
        name: selectedAttraction.name,
        lat: selectedAttraction.lat,
        lng: selectedAttraction.lng,
        category: categoryLabel(selectedAttraction.category),
      },
    ];
  }, [listPlaces, selectedAttraction]);
  const selectedMapIndex = selectedAttraction
    ? mapPlaces.findIndex((p) => p.lat === selectedAttraction.lat && p.lng === selectedAttraction.lng)
    : null;

  const mapCenter: [number, number] = selectedAttraction
    ? [selectedAttraction.lat, selectedAttraction.lng]
    : focusCenter
      ? [focusCenter.lat, focusCenter.lng]
      : FALLBACK_CENTER;

  const selectedFavorite = selectedAttraction
    ? (favorites.find((f) => placeKey(f) === placeKey(selectedAttraction)) ?? null)
    : null;

  function handleMapSelect(idx: number) {
    if (idx >= displayList.length) return; // the extra pin for an already-selected place
    const item = displayList[idx];
    if (item.type === "attraction") openAttraction(item.data);
    else openPlace(item.data);
  }

  function distanceToPlace(lat: number, lng: number): string | null {
    if (!userLocation) return null;
    return formatDistanceKm(haversineDistanceKm(userLocation.lat, userLocation.lng, lat, lng));
  }

  async function toggleFavorite() {
    if (!selectedAttraction) return;
    setFavoriteBusy(true);
    try {
      if (selectedFavorite) {
        await removeFavorite(selectedFavorite.id);
        setFavorites((prev) => prev.filter((f) => f.id !== selectedFavorite.id));
      } else {
        const created = await addFavorite({
          name: selectedAttraction.name,
          lat: selectedAttraction.lat,
          lng: selectedAttraction.lng,
          category: categoryLabel(selectedAttraction.category),
          address: selectedAttraction.area ?? selectedAttraction.district ?? undefined,
          opening_hours: selectedAttraction.opening_access ?? undefined,
          website: selectedAttraction.source_urls[0],
        });
        setFavorites((prev) => [created, ...prev]);
      }
    } catch {
      setSearchError("Could not update favourites. Try again.");
    } finally {
      setFavoriteBusy(false);
    }
  }

  if (checking) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-muted">Loading...</p>
      </div>
    );
  }

  return (
    <div className="relative flex-1 overflow-hidden" style={{ height: "calc(100dvh - 65px)" }}>
      <div className="absolute inset-0">
        <Map
          center={mapCenter}
          places={mapPlaces}
          zoom={selectedAttraction ? 15 : focusCenter ? 12 : 5}
          fitToPlaces={!selectedAttraction}
          onSelectPlace={handleMapSelect}
          selectedIndex={selectedMapIndex}
          route={routePositions ?? undefined}
          boundary={boundary}
          boundaryKey={boundaryKey}
        />
      </div>

      <div className="pointer-events-none absolute inset-0 z-[1100] flex p-4">
        <div className="pointer-events-auto flex w-full max-w-[420px] flex-col overflow-hidden rounded-2xl bg-card shadow-2xl">
          {selectedAttraction ? (
            <PlaceSheet
              key={selectedAttraction.id}
              attraction={selectedAttraction}
              isFavorite={!!selectedFavorite}
              favoriteBusy={favoriteBusy}
              onToggleFavorite={toggleFavorite}
              onBack={() => {
                setSelectedAttraction(null);
                setRoutePositions(null);
              }}
              userLocation={userLocation}
              locationError={locationError}
              onRequestLocation={requestUserLocation}
              onRouteChange={setRoutePositions}
              onRatingChange={(avgRating, reviewCount) =>
                setAllCurated((prev) =>
                  prev.map((a) =>
                    a.id === selectedAttraction.id ? { ...a, avg_rating: avgRating, review_count: reviewCount } : a
                  )
                )
              }
            />
          ) : (
            <div className="flex h-full flex-col">
              <div className="shrink-0 p-4">
                <p className="font-display text-xl font-semibold text-card-foreground">
                  Discover incredible India
                </p>
                <p className="mt-1 text-xs text-muted">Search any city, district or place</p>
                <form onSubmit={handleSearch} className="relative mt-3">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
                  >
                    <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                    <path d="m20 20-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for a place, city or district"
                    className="w-full rounded-full border border-border bg-background py-2.5 pl-10 pr-9 text-sm outline-none ring-2 ring-transparent transition-shadow focus:ring-primary"
                  />
                  {query && (
                    <button
                      type="button"
                      onClick={resetToDefault}
                      aria-label="Clear search"
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-primary"
                    >
                      ✕
                    </button>
                  )}
                </form>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {visibleChips.map((chip) => (
                    <button
                      key={chip.id}
                      type="button"
                      onClick={() => selectCategory(chip.id)}
                      className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                        categoryFilter === chip.id
                          ? "bg-primary text-primary-foreground"
                          : "border border-border bg-card text-card-foreground hover:border-primary hover:text-primary"
                      }`}
                    >
                      {chip.icon} {chip.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto border-t border-border px-3 py-3">
                {(searchLoading || nearbyLoading || resolving || ((categoryFilter === "restaurants" || categoryFilter === "hotels") && allCuratedLoading)) && (
                  <p className="px-1 pb-2 text-sm text-muted">
                    {resolving ? "Opening…" : "Loading…"}
                  </p>
                )}
                {searchError && <p className="px-1 pb-2 text-sm text-red-500">{searchError}</p>}
                {nearbyError && <p className="px-1 pb-2 text-sm text-red-500">{nearbyError}</p>}
                {allCuratedError && (
                  <p className="px-1 pb-2 text-sm text-red-500">
                    {allCuratedError}{" "}
                    <button
                      type="button"
                      onClick={() => {
                        setAllCuratedLoading(true);
                        setAllCuratedError(null);
                        const promise = fetchAllCurated();
                        allCuratedPromiseRef.current = promise;
                        promise
                          .then((data) => {
                            setAllCurated(data);
                            setAllCuratedLoading(false);
                          })
                          .catch((err) => {
                            setAllCuratedError(
                              extractErrorMessage(err, "Could not load Chandrapur's curated places.")
                            );
                            setAllCuratedLoading(false);
                          });
                      }}
                      className="font-medium underline"
                    >
                      Retry
                    </button>
                  </p>
                )}
                {activeDistrict && categoryFilter === "all" && (
                  <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-secondary">
                    {activeDistrict.replace(/\s+(town|city)$/i, "").trim()} {activeScopeKind ?? "area"}
                  </p>
                )}

                {!searchLoading &&
                  !nearbyLoading &&
                  !((categoryFilter === "restaurants" || categoryFilter === "hotels") && allCuratedLoading) &&
                  displayList.length === 0 && (
                    <p className="px-1 text-sm text-muted">
                      {categoryFilter === "restaurants" || categoryFilter === "hotels"
                        ? `No ${categoryFilter} found nearby.`
                        : categoryFilter !== "all"
                          ? activeDistrict
                            ? "Nothing found for this filter yet."
                            : "Search for a city or district first, then filter by category."
                          : activeDistrict || searchResults
                            ? "No curated places here yet."
                            : "Search for a city, district or place to start exploring."}
                    </p>
                  )}

                <div className="flex flex-col gap-2">
                  {displayList.map((item, idx) => {
                    const isAttraction = item.type === "attraction";
                    const d = item.data;
                    const attractionData = isAttraction ? (d as Attraction) : null;
                    const placeDistrict = attractionData?.district || activeDistrict;
                    return (
                      <div
                        key={isAttraction ? `a-${(d as Attraction).id}` : `p-${idx}-${d.lat}-${d.lng}`}
                        className="group relative rounded-xl border border-border bg-card p-3 shadow-xs transition-all hover:-translate-y-0.5 hover:shadow-md cursor-pointer"
                        onClick={() => (isAttraction ? openAttraction(d as Attraction) : openPlace(d as Place))}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="flex items-center gap-1.5 font-medium text-card-foreground group-hover:text-primary transition-colors">
                            <span>{categoryIcon(d.category ?? "place")}</span>
                            <span>{d.name}</span>
                          </p>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              triggerAiHelper({
                                placeId: attractionData?.id,
                                placeName: d.name,
                                district: placeDistrict,
                                category: d.category,
                                area: attractionData?.area,
                              });
                            }}
                            className="shrink-0 inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2.5 py-0.5 text-[0.7rem] font-semibold text-primary transition-all hover:bg-primary/20 active:scale-95 shadow-xs"
                            title={`Ask AI about ${d.name}`}
                          >
                            <span className="text-accent text-xs">✦</span> Ask AI
                          </button>
                        </div>
                        <p className="mt-1 flex flex-wrap items-center gap-2 text-xs">
                          <span className="rounded-full bg-primary/10 px-2 py-0.5 font-medium uppercase tracking-wide text-primary">
                            {categoryLabel(d.category ?? "place")}
                          </span>
                          {isAttraction ? (
                            <span className="flex items-center gap-1.5">
                              {(d as Attraction).avg_rating ? (
                                <span className="font-medium text-accent">★ {(d as Attraction).avg_rating!.toFixed(1)}</span>
                              ) : (
                                <span className="text-muted">No ratings yet</span>
                              )}
                              {(d as Attraction).external_rating ? (
                                <span className="border-l border-border pl-1.5 text-[10px] text-muted">
                                  Google: <span className="font-medium text-foreground/70">★ {(d as Attraction).external_rating}</span> ({(d as Attraction).external_rating_count})
                                </span>
                              ) : null}
                            </span>
                          ) : null}
                        </p>
                        {!isAttraction && (d as Place).address && (
                          <p className="mt-1.5 truncate text-xs text-muted">{(d as Place).address}</p>
                        )}
                        {isAttraction && (d as Attraction).area && (
                          <p className="mt-1.5 text-xs text-muted">{(d as Attraction).area}</p>
                        )}
                        {isAttraction && ((d as Attraction).specialty || (d as Attraction).price_tier) && (
                          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                            {(d as Attraction).price_tier && (
                              <span className="rounded bg-secondary/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-secondary">
                                {(d as Attraction).price_tier}
                              </span>
                            )}
                            {(d as Attraction).specialty && (
                              <span className="truncate text-[11px] text-muted max-w-[250px]" title={(d as Attraction).specialty!}>
                                {(d as Attraction).specialty}
                              </span>
                            )}
                          </div>
                        )}
                        <div className="mt-2 flex items-center justify-between gap-2 border-t border-border/50 pt-1.5">
                          {distanceToPlace(d.lat, d.lng) ? (
                            <p className="text-xs font-medium text-primary">
                              {distanceToPlace(d.lat, d.lng)} away
                            </p>
                          ) : (
                            <span className="text-[0.7rem] text-muted">
                              {placeDistrict ? `${placeDistrict}` : "India"}
                            </span>
                          )}
                          {isAttraction && (d as Attraction).booking_url && (
                            <a
                              href={(d as Attraction).booking_url!}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="rounded-full bg-primary px-2.5 py-0.5 text-xs font-medium text-primary-foreground transition-opacity hover:opacity-90 shadow-2xs"
                            >
                              Book slot
                            </a>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-background">
          <p className="text-muted">Loading...</p>
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
