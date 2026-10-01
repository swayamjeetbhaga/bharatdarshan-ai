"use client";

import { useMemo, useState } from "react";
import {
  estimateTravelExpenses,
  findNearestLocation,
  getPresetsForAttraction,
  ALL_INDIAN_HUBS,
  type DynamicFare,
} from "@/lib/travelExpenses";
import { searchPlaces } from "@/lib/api";
import { formatDistanceKm } from "@/lib/geo";
import { triggerAiHelper } from "@/lib/aiHelper";

interface TravelExpensesProps {
  attraction: {
    id: number;
    name: string;
    area?: string | null;
    district?: string | null;
    state?: string | null;
    lat: number;
    lng: number;
    category?: string;
  };
  userLocation?: { lat: number; lng: number } | null;
  locationError?: string | null;
  onRequestLocation?: () => void;
}

export default function TravelExpenses({
  attraction,
  userLocation,
  locationError,
  onRequestLocation,
}: TravelExpensesProps) {
  // Nearest preset town to user GPS
  const nearestGpsTown = useMemo(() => {
    if (!userLocation) return null;
    return findNearestLocation(userLocation.lat, userLocation.lng);
  }, [userLocation]);

  // Contextual presets for this attraction's district/region
  const presets = useMemo(() => {
    return getPresetsForAttraction(attraction);
  }, [attraction]);

  // Selected starting point
  const [customOrigin, setCustomOrigin] = useState<{
    name: string;
    lat: number;
    lng: number;
    isGps?: boolean;
  } | null>(null);

  const [originSearch, setOriginSearch] = useState<string>("");
  const [searching, setSearching] = useState<boolean>(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [showSearchBox, setShowSearchBox] = useState<boolean>(false);

  // Active Origin
  const activeOrigin = useMemo(() => {
    if (customOrigin) return customOrigin;
    if (userLocation) {
      return {
        name: nearestGpsTown
          ? `Your GPS (~${nearestGpsTown.distanceKm} km to ${nearestGpsTown.location.name})`
          : "Your Location (GPS)",
        lat: userLocation.lat,
        lng: userLocation.lng,
        isGps: true,
      };
    }
    // Default to the first preset hub for this destination
    const defaultHub = presets[0] || ALL_INDIAN_HUBS[0];
    return {
      name: defaultHub.name,
      lat: defaultHub.lat,
      lng: defaultHub.lng,
      isGps: false,
    };
  }, [customOrigin, userLocation, nearestGpsTown, presets]);

  // Dynamic Fare calculation
  const fareData: DynamicFare = useMemo(() => {
    return estimateTravelExpenses(
      { name: activeOrigin.name, lat: activeOrigin.lat, lng: activeOrigin.lng },
      { name: attraction.name, category: attraction.category, lat: attraction.lat, lng: attraction.lng }
    );
  }, [activeOrigin, attraction]);

  function handleSelectPreset(name: string, lat: number, lng: number) {
    setCustomOrigin({ name, lat, lng, isGps: false });
    setShowSearchBox(false);
    setSearchError(null);
  }

  function handleUseGps() {
    setCustomOrigin(null);
    setShowSearchBox(false);
    setSearchError(null);
    if (onRequestLocation && !userLocation) {
      onRequestLocation();
    }
  }

  async function handleCustomSearch(e: React.FormEvent) {
    e.preventDefault();
    const query = originSearch.trim();
    if (!query) return;

    // Check if directly in presets or all Indian hubs
    const localMatch = ALL_INDIAN_HUBS.find((h) => h.name.toLowerCase() === query.toLowerCase());
    if (localMatch) {
      setCustomOrigin({ name: localMatch.name, lat: localMatch.lat, lng: localMatch.lng, isGps: false });
      setShowSearchBox(false);
      setOriginSearch("");
      setSearchError(null);
      return;
    }

    setSearching(true);
    setSearchError(null);
    try {
      const results = await searchPlaces(query);
      if (results && results.length > 0) {
        const top = results[0];
        setCustomOrigin({
          name: top.name,
          lat: top.lat,
          lng: top.lng,
          isGps: false,
        });
        setShowSearchBox(false);
        setOriginSearch("");
      } else {
        setSearchError(`Could not find "${query}". Please check spelling.`);
      }
    } catch {
      setSearchError("Search lookup failed. Try choosing from the suggestions.");
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="rounded-2xl border border-border bg-card/90 p-4 shadow-md backdrop-blur-xs transition-all">
      {/* Header */}
      <div className="flex items-center justify-between gap-2 border-b border-border/70 pb-3">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-lg">
            🧭
          </span>
          <div>
            <h4 className="font-display text-sm font-semibold text-card-foreground flex items-center gap-1.5">
              <span>Estimated Travel Expenses</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.2 text-[0.65rem] font-medium text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                All-India Fares
              </span>
            </h4>
            <p className="text-[0.7rem] text-muted">
              Calculated dynamically from your starting location to {attraction.name}
            </p>
          </div>
        </div>
      </div>

      {/* Origin & Destination Direction Card (Google Maps Style) */}
      <div className="mt-3.5 rounded-xl border border-border/80 bg-background/80 p-3 shadow-xs">
        {/* Origin */}
        <div className="flex items-center gap-2.5">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-500 text-[0.65rem] font-bold text-white shadow-xs">
            A
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[0.68rem] font-semibold uppercase tracking-wider text-muted">
                {activeOrigin.isGps ? "Your Live GPS Location" : "Starting Location"}
              </span>
              <button
                type="button"
                onClick={() => setShowSearchBox((prev) => !prev)}
                className="text-[0.68rem] font-medium text-primary hover:underline"
              >
                {showSearchBox ? "Close" : "Change city/village ▾"}
              </button>
            </div>
            <p className="text-xs font-semibold text-card-foreground truncate">
              {activeOrigin.name}
            </p>
          </div>
        </div>

        {/* Route Connector Line with Live Distance */}
        <div className="my-1.5 ml-2.5 flex items-center gap-2 border-l-2 border-dashed border-primary/40 pl-4 py-0.5">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-0.5 text-[0.7rem] font-semibold text-primary">
            <span>📍</span>
            <span>
              {formatDistanceKm(fareData.distanceKm)} · ~{fareData.durationMin} mins by road
            </span>
          </span>
        </div>

        {/* Destination */}
        <div className="flex items-center gap-2.5">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-500 text-[0.65rem] font-bold text-white shadow-xs">
            B
          </span>
          <div className="flex-1 min-w-0">
            <span className="text-[0.68rem] font-semibold uppercase tracking-wider text-muted">
              Destination Tourist Spot
            </span>
            <p className="text-xs font-semibold text-card-foreground truncate">
              {attraction.name} {attraction.area ? `(${attraction.area})` : ""}
            </p>
          </div>
        </div>
      </div>

      {/* City/Village Search Form (Supports any city or village across India) */}
      {showSearchBox && (
        <div className="mt-2.5 rounded-xl border border-border bg-background p-2.5 shadow-sm">
          <form onSubmit={handleCustomSearch} className="flex gap-1.5">
            <input
              value={originSearch}
              onChange={(e) => setOriginSearch(e.target.value)}
              placeholder="Search any village, town or city in India (e.g. Pune, Jaipur, Warora, Thane)..."
              className="flex-1 rounded-xl border border-border bg-card px-3 py-1.5 text-xs outline-none focus:border-primary"
            />
            <button
              type="submit"
              disabled={searching || !originSearch.trim()}
              className="rounded-xl bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground shadow-xs hover:opacity-90 disabled:opacity-50"
            >
              {searching ? "Searching…" : "Apply"}
            </button>
          </form>
          {searchError && <p className="mt-1.5 text-[0.68rem] text-red-500">{searchError}</p>}
        </div>
      )}

      {/* Quick Starting Points Chips */}
      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <button
          type="button"
          onClick={handleUseGps}
          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[0.72rem] font-medium transition-all ${
            activeOrigin.isGps
              ? "bg-blue-600 text-white shadow-xs"
              : "border border-blue-500/40 bg-blue-500/10 text-blue-600 dark:text-blue-400 hover:bg-blue-500/20"
          }`}
        >
          <span>📍</span>
          <span>My GPS</span>
        </button>

        {presets.map((loc) => {
          const isSelected = !activeOrigin.isGps && activeOrigin.name.toLowerCase() === loc.name.toLowerCase();
          return (
            <button
              key={loc.name}
              type="button"
              onClick={() => handleSelectPreset(loc.name, loc.lat, loc.lng)}
              className={`rounded-full px-2.5 py-0.5 text-[0.72rem] font-medium transition-all ${
                isSelected
                  ? "bg-primary text-primary-foreground shadow-xs"
                  : "border border-border bg-background text-card-foreground hover:border-primary/40 hover:text-primary"
              }`}
            >
              {loc.name}
            </button>
          );
        })}
      </div>

      {/* Location Status Message if GPS is active */}
      {!userLocation && locationError && activeOrigin.isGps && (
        <div className="mt-2 flex items-center justify-between rounded-lg bg-amber-500/10 px-2.5 py-1 text-[0.7rem] text-amber-700 dark:text-amber-300">
          <span>⚠️ Location permission needed. Showing baseline rates from {presets[0]?.name || "Chandrapur"}.</span>
          {onRequestLocation && (
            <button type="button" onClick={onRequestLocation} className="font-semibold text-primary underline">
              Retry
            </button>
          )}
        </div>
      )}

      {/* Dynamic Fares Grid */}
      <div className="mt-3.5">
        {fareData.isSameLocation ? (
          /* You are literally at the spot (< 2.5 km) */
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-emerald-800 dark:text-emerald-200">
            <div className="flex items-center gap-2">
              <span className="text-base">📍</span>
              <div>
                <p className="text-xs font-bold">You are right here at {attraction.name}!</p>
                <p className="text-[0.72rem] opacity-90 mt-0.5">
                  Distance is under 2 km. Walking or short E-Rickshaw ride: <strong>₹20 – ₹40</strong>.
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Realistic Fare Cards */
          <div className="grid grid-cols-3 gap-2">
            {/* Bus Option */}
            <div className="flex flex-col items-center justify-between rounded-xl border border-border/80 bg-background/90 p-2.5 text-center shadow-xs transition-all hover:border-primary/50">
              <div className="flex flex-col items-center">
                <span className="text-xl">🚌</span>
                <span className="mt-1 text-[0.7rem] font-semibold text-card-foreground">
                  {fareData.bus.label}
                </span>
              </div>
              <div className="mt-2">
                <span className="font-display text-base font-bold text-card-foreground">
                  {fareData.bus.fare !== null ? `₹${fareData.bus.fare}` : "—"}
                </span>
                <p className="text-[0.62rem] text-muted leading-tight mt-0.5">{fareData.bus.subLabel}</p>
              </div>
            </div>

            {/* Taxi / Cab Option */}
            <div className="flex flex-col items-center justify-between rounded-xl border border-border/80 bg-background/90 p-2.5 text-center shadow-xs transition-all hover:border-primary/50">
              <div className="flex flex-col items-center">
                <span className="text-xl">🛺</span>
                <span className="mt-1 text-[0.7rem] font-semibold text-card-foreground">
                  {fareData.taxi.label}
                </span>
              </div>
              <div className="mt-2">
                <span className="font-display text-base font-bold text-card-foreground">
                  {fareData.taxi.sharedFare !== null ? `₹${fareData.taxi.sharedFare}` : "—"}
                </span>
                <p className="text-[0.62rem] text-muted leading-tight mt-0.5">{fareData.taxi.subLabel}</p>
              </div>
            </div>

            {/* Railway Option */}
            <div className="flex flex-col items-center justify-between rounded-xl border border-border/80 bg-background/90 p-2.5 text-center shadow-xs transition-all hover:border-primary/50">
              <div className="flex flex-col items-center">
                <span className="text-xl">🚆</span>
                <span className="mt-1 text-[0.7rem] font-semibold text-card-foreground">
                  {fareData.railway.label}
                </span>
              </div>
              <div className="mt-2">
                <span
                  className={`font-display text-base font-bold ${
                    !fareData.railway.available ? "text-xs font-medium text-muted" : "text-card-foreground"
                  }`}
                >
                  {fareData.railway.fare !== null ? `₹${fareData.railway.fare}` : "No direct"}
                </span>
                <p className="text-[0.62rem] text-muted leading-tight mt-0.5">
                  {fareData.railway.note || (fareData.railway.available ? "Direct train line" : "Road transfer")}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Travel Plan with AI Bar */}
      <div className="mt-3.5 flex items-center justify-between gap-2 rounded-xl bg-primary/5 px-3 py-2 text-xs text-muted">
        <span className="text-[0.72rem] truncate">
          Route: <strong className="text-card-foreground">{activeOrigin.name}</strong> ➔{" "}
          <strong className="text-card-foreground">{attraction.name}</strong>
        </span>
        <button
          type="button"
          onClick={() =>
            triggerAiHelper({
              placeId: attraction.id,
              placeName: attraction.name,
              district: attraction.district || undefined,
              category: attraction.category,
              area: attraction.area || undefined,
            })
          }
          className="shrink-0 inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-[0.7rem] font-semibold text-primary hover:bg-primary/20 transition-colors"
        >
          <span className="text-accent text-[0.65rem]">✦</span> Plan with AI
        </button>
      </div>
    </div>
  );
}
