import re
import httpx

from app.data.maharashtra_districts import canonical_maharashtra_district

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
OSRM_URL = "https://router.project-osrm.org"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {"User-Agent": "BharatDarshanAI/1.0"}

def _describe_place(name: str, category: str | None, tags: dict) -> str:
    kind = (category or "place").replace("_", " ").strip().lower() or "place"
    sentence = f"{name} is a {kind} in India."

    highlights = []
    if tags.get("historic"):
        highlights.append("recognized as a historic site")
    if tags.get("cuisine"):
        highlights.append(f"known for {tags['cuisine'].replace('_', ' ')} cuisine")
    if tags.get("religion"):
        highlights.append(f"associated with the {tags['religion']} faith")
    if tags.get("wikidata") or tags.get("wikipedia"):
        highlights.append("documented on Wikipedia")

    if highlights:
        sentence += " It is " + " and ".join(highlights) + "."
    return sentence

def _build_address(tags: dict) -> str | None:
    parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:city"),
        tags.get("addr:state"),
    ]
    parts = [p for p in parts if p]
    return ", ".join(parts) if parts else None

def _guess_district(address: dict) -> str | None:
    """Best-effort administrative district/city name from a Nominatim address
    block, used to cross-reference our own curated attraction records."""
    return (
        address.get("state_district")
        or address.get("county")
        or address.get("city")
        or address.get("town")
        or None
    )

async def search_places(query: str, country: str = "India"):
    """India-wide place/area search. Backed by Nominatim — results can be a
    specific point of interest (a restaurant, a fort) or an administrative
    area (a district, city or state), in which case `boundary` carries its
    outline geojson and `district` is a best guess for cross-referencing our
    own curated attraction records."""
    # A name such as "Nagpur" can represent both a city and a district.
    # Treat exact Maharashtra-district searches as districts; a caller can
    # still explicitly search "Nagpur city" to receive the city boundary.
    requested_district = canonical_maharashtra_district(query) if country.lower() == "india" else None
    geocoder_query = f"{requested_district} district" if requested_district else query

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{NOMINATIM_URL}/search",
            params={
                "q": f"{geocoder_query}, {country}" if country else geocoder_query,
                "format": "json",
                "limit": 10,
                "addressdetails": 1,
                "extratags": 1,
                "polygon_geojson": 1,
            },
            headers=HEADERS,
        )
        results = response.json()
        places = []
        for r in results:
            extratags = r.get("extratags") or {}
            address = r.get("address") or {}
            name = r["display_name"].split(",")[0]
            category = r.get("type") or r.get("class") or "place"
            # Surface only real administrative outlines. This includes city
            # and town boundaries, not just districts; POI/building polygons
            # must remain pins rather than becoming a misleading search area.
            # Restricted to `type == "administrative"` (rather than any
            # `class == "boundary"` result) because protected areas like
            # Tadoba-Andhari Tiger Reserve are also tagged `boundary=*` in
            # OSM and carry a real polygon — without this check, searching
            # "Tadoba" would wrongly trigger the whole-district browse (every
            # curated Chandrapur attraction) instead of resolving to just
            # that one reserve.
            is_area = r.get("class") == "boundary" and r.get("type") == "administrative"
            geojson = r.get("geojson") or {}
            # Some "place" results (e.g. a city node) carry a degenerate
            # single-point "geometry" rather than a real outline — fitting
            # the map to a zero-area box zooms in to the max level on that
            # one point, which looks like a bug. Only pass through geometry
            # that's actually a polygon.
            has_polygon = geojson.get("type") in ("Polygon", "MultiPolygon")
            scope_kind = "district" if requested_district and name.lower() == requested_district.lower() else "city"
            places.append({
                "name": name,
                "address": r["display_name"],
                "lat": float(r["lat"]),
                "lng": float(r["lon"]),
                "category": category,
                "description": _describe_place(name, category, extratags),
                "opening_hours": extratags.get("opening_hours"),
                "website": extratags.get("website"),
                "phone": extratags.get("phone"),
                "osm_type": r.get("osm_type"),
                "osm_id": r.get("osm_id"),
                "district": _guess_district(address),
                "scope_kind": scope_kind if is_area and has_polygon else None,
                "boundary": geojson if (is_area and has_polygon) else None,
                "is_area": is_area,
            })
        return places

async def _route(client: httpx.AsyncClient, lat1: float, lng1: float, lat2: float, lng2: float):
    coords = f"{lng1},{lat1};{lng2},{lat2}"
    response = await client.get(
        f"{OSRM_URL}/route/v1/driving/{coords}",
        params={"overview": "full", "geometries": "geojson", "steps": "true"}
    )
    data = response.json()
    if data.get("code") != "Ok":
        return None

    route = data["routes"][0]
    leg = route["legs"][0]

    # Deduplicated chain of named waypoints along the route (road/street names).
    waypoints = []
    for step in leg["steps"]:
        name = step.get("name")
        if name and (not waypoints or waypoints[-1] != name):
            waypoints.append(name)

    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_min": round(route["duration"] / 60, 2),
        "steps": [s["maneuver"]["type"] + " " + s.get("name", "") for s in leg["steps"]],
        "waypoints": waypoints,
        "geometry": route["geometry"],
    }

async def get_directions_by_coords(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
    async with httpx.AsyncClient(timeout=20.0) as client:
        return await _route(client, origin_lat, origin_lng, dest_lat, dest_lng)

def _parse_category(category: str) -> tuple[str, str, str]:
    """Split a category spec into (tag_key, operator, value).

    Supports bare tag keys ("tourism" -> presence match), exact matches
    ("tourism=hotel"), and regex-alternation matches
    ("amenity~restaurant|cafe|fast_food") for OSM tag filtering.
    """
    match = re.match(r"^([a-zA-Z_:]+)(=|~)(.+)$", category)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return category, "", ""

def _overpass_filter(key: str, operator: str, value: str) -> str:
    if operator == "=":
        return f'["{key}"="{value}"]'
    if operator == "~":
        return f'["{key}"~"{value}"]'
    return f'["{key}"]'

async def nearby_places(lat: float, lng: float, radius: int = 5000, category: str = "tourism"):
    key, operator, value = _parse_category(category)
    tag_filter = _overpass_filter(key, operator, value)
    query = f"""
    [out:json];
    node{tag_filter}(around:{radius},{lat},{lng});
    out body 20;
    """
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(OVERPASS_URL, data={"data": query}, headers=HEADERS)
        try:
            elements = response.json().get("elements", [])
        except ValueError:
            # The public Overpass instance returns a non-JSON body (an HTML
            # rate-limit page, or nothing) when it's overloaded — degrade to
            # "no results" rather than failing the whole request.
            return []
        places = []
        for e in elements:
            tags = e.get("tags")
            if not tags:
                continue
            name = tags.get("name", "Unknown")
            kind = tags.get(key) or tags.get("tourism") or tags.get("historic") or tags.get("amenity") or key
            places.append({
                "name": name,
                "address": _build_address(tags),
                "lat": e["lat"],
                "lng": e["lon"],
                "category": kind,
                "description": _describe_place(name, kind, tags),
                "opening_hours": tags.get("opening_hours"),
                "website": tags.get("website") or tags.get("contact:website"),
                "phone": tags.get("phone") or tags.get("contact:phone"),
            })
        return places
