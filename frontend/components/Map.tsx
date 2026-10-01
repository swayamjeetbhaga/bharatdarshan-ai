"use client";

import { MapContainer, TileLayer, Marker, Popup, Polyline, GeoJSON as GeoJSONLayer, Tooltip, useMap } from "react-leaflet";
import { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { PlaceBoundary } from "@/lib/api";

const defaultIcon = L.icon({
  iconUrl: "/leaflet/marker-icon.png",
  iconRetinaUrl: "/leaflet/marker-icon-2x.png",
  shadowUrl: "/leaflet/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// A red pin (à la Google Maps' highlighted marker) for whichever place is
// currently selected, so it stands out from the rest.
const selectedIcon = L.divIcon({
  className: "",
  html: `<svg viewBox="0 0 24 24" width="34" height="34" style="filter:drop-shadow(0 2px 3px rgba(0,0,0,.45))">
    <path fill="#dc2626" stroke="#7f1d1d" stroke-width="1"
      d="M12 2C7.58 2 4 5.58 4 10c0 5.25 6.72 11.19 7.02 11.45a1.5 1.5 0 0 0 1.96 0C13.28 21.19 20 15.25 20 10c0-4.42-3.58-8-8-8z"/>
    <circle cx="12" cy="10" r="3.2" fill="white"/>
  </svg>`,
  iconSize: [34, 34],
  iconAnchor: [17, 34],
  popupAnchor: [0, -30],
});

export interface MapPlace {
  name: string;
  lat: number;
  lng: number;
  category?: string;
}

interface MapProps {
  center: [number, number];
  places?: MapPlace[];
  zoom?: number;
  onSelectPlace?: (index: number) => void;
  selectedIndex?: number | null;
  route?: [number, number][];
  // When true (and there's no route/boundary to fit to), frame the map to
  // show every place at once instead of just centering on `center`.
  fitToPlaces?: boolean;
  boundary?: PlaceBoundary | null;
  // Identifies the current boundary so the GeoJSON layer remounts when a
  // new search result's outline replaces the old one.
  boundaryKey?: string;
}

// MapContainer's center/zoom props only apply on initial mount; this keeps
// an already-mounted map in sync with subsequent center/zoom/route/places/
// boundary changes (e.g. a new search result).
function MapViewController({
  center,
  zoom,
  route,
  places,
  fitToPlaces,
  boundary,
}: {
  center: [number, number];
  zoom: number;
  route?: [number, number][];
  places: MapPlace[];
  fitToPlaces?: boolean;
  boundary?: PlaceBoundary | null;
}) {
  const map = useMap();
  useEffect(() => {
    if (route && route.length > 1) {
      map.fitBounds(L.latLngBounds(route), { padding: [40, 40] });
    } else if (!fitToPlaces) {
      // A specific place is focused (e.g. selected on the map) — center on
      // it directly rather than re-framing to the district boundary or the
      // full place list.
      map.setView(center, zoom);
    } else if (boundary && places.length > 0) {
      const bounds = L.geoJSON(boundary as GeoJSON.GeoJsonObject).getBounds();
      places.forEach((p) => bounds.extend([p.lat, p.lng]));
      map.fitBounds(bounds, { padding: [40, 40] });
    } else if (boundary) {
      map.fitBounds(L.geoJSON(boundary as GeoJSON.GeoJsonObject).getBounds(), { padding: [20, 20] });
    } else if (places.length > 1) {
      map.fitBounds(L.latLngBounds(places.map((p) => [p.lat, p.lng])), { padding: [40, 40] });
    } else {
      map.setView(center, zoom);
    }
  }, [center, zoom, route, fitToPlaces, places, boundary, map]);
  return null;
}

export default function Map({
  center,
  places = [],
  zoom = 13,
  onSelectPlace,
  selectedIndex,
  route,
  fitToPlaces,
  boundary,
  boundaryKey,
}: MapProps) {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      scrollWheelZoom
      className="h-full w-full rounded-lg"
    >
      <MapViewController
        center={center}
        zoom={zoom}
        route={route}
        places={places}
        fitToPlaces={fitToPlaces}
        boundary={boundary}
      />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {boundary && (
        <GeoJSONLayer
          key={boundaryKey ?? "boundary"}
          data={boundary as GeoJSON.GeoJsonObject}
          pathOptions={{ color: "#dc2626", weight: 2, dashArray: "6 5", fillOpacity: 0.04, fillColor: "#dc2626" }}
        />
      )}
      {route && route.length > 1 && (
        <Polyline positions={route} pathOptions={{ color: "#2563eb", weight: 4, opacity: 0.85 }} />
      )}
      {places.map((place, idx) => (
        <Marker
          key={`${place.name}-${idx}`}
          position={[place.lat, place.lng]}
          icon={idx === selectedIndex ? selectedIcon : defaultIcon}
          eventHandlers={{ click: () => onSelectPlace?.(idx) }}
        >
          <Tooltip
            permanent
            direction="top"
            offset={[0, -36]}
            opacity={1}
            className="bharatdarshan-place-label"
          >
            {place.name}
          </Tooltip>
          <Popup>
            <strong>{place.name}</strong>
            {place.category ? <div className="text-xs text-zinc-500">{place.category}</div> : null}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
