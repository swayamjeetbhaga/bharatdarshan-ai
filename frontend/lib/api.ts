import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh_token = localStorage.getItem("refresh_token");
      if (refresh_token) {
        try {
          const res = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
            { refresh_token }
          );
          localStorage.setItem("access_token", res.data.access_token);
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api(error.config);
        } catch {
          localStorage.clear();
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const API_ORIGIN = process.env.NEXT_PUBLIC_API_URL ?? "";

// The backend returns uploaded-photo URLs as paths relative to its own
// origin (e.g. "/media/attractions/1/x.png") — this makes them absolute.
export function mediaUrl(path: string): string {
  if (/^https?:\/\//.test(path)) return path;
  return `${API_ORIGIN}${path}`;
}

// Pulls the backend's specific error detail out of a failed request, falling
// back to a generic message when the response doesn't carry one.
export function extractErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export interface CurrentUser {
  id: number;
  email: string;
  username: string;
}

export const getCurrentUser = async (): Promise<CurrentUser> => {
  const res = await api.get("/api/v1/auth/me");
  return res.data;
};

// General-purpose "Ask AI" travel helper shown in the navbar — separate from
// the per-place data below, this is a free-form chat assistant.
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export const sendChatMessage = async (
  message: string,
  history: ChatMessage[],
  placeName?: string,
  district?: string,
  attractionId?: number | null
): Promise<ChatResponse> => {
  const res = await api.post("/api/v1/agent/chat", {
    message,
    history,
    place_name: placeName,
    district,
    attraction_id: attractionId,
  });
  return res.data;
};

// A rough GeoJSON polygon/multipolygon shape — enough for react-leaflet's
// <GeoJSON> without pulling in the full `geojson` type package.
export interface PlaceBoundary {
  type: string;
  coordinates: unknown;
}

// Live, India-wide OSM lookups. Used for the main search/nearby experience
// and by the general-purpose Food/Hotels near-me pages.
export interface Place {
  name: string;
  address?: string;
  lat: number;
  lng: number;
  category?: string;
  description?: string;
  opening_hours?: string;
  website?: string;
  phone?: string;
  osm_type?: string | null;
  osm_id?: number | null;
  district?: string | null;
  scope_kind?: "district" | "city" | null;
  is_area?: boolean;
  boundary?: PlaceBoundary | null;
}

export const searchPlaces = async (query: string, country = "India"): Promise<Place[]> => {
  const res = await api.post("/api/v1/places/search", { query, country });
  return res.data;
};

export const nearbyPlaces = async (
  lat: number,
  lng: number,
  radius = 5000,
  category = "tourism"
): Promise<Place[]> => {
  const res = await api.post("/api/v1/places/nearby", { lat, lng, radius, category });
  return res.data;
};

export interface Directions {
  distance_km: number;
  duration_min: number;
  steps: string[];
  waypoints: string[];
  geometry: { type: string; coordinates: [number, number][] };
}

export const getDirectionsByCoords = async (
  originLat: number,
  originLng: number,
  destLat: number,
  destLng: number
): Promise<Directions | null> => {
  const res = await api.post("/api/v1/places/directions-by-coords", {
    origin_lat: originLat,
    origin_lng: originLng,
    dest_lat: destLat,
    dest_lng: destLng,
  });
  return res.data;
};

// Curated categories used by our own hand-seeded datasets (Chandrapur
// today, more districts later). A community-resolved place (anywhere else
// in India) carries whatever free-text category the map search gave it, so
// `category` is a plain string — this union is only a display hint.
export type CuratedCategory =
  | "wildlife"
  | "lake_nature"
  | "religious_heritage"
  | "historical_fort"
  | "social_educational";

// Chandrapur city's curated restaurant/cafe directory.
export type FoodCategory =
  | "fine_dining_veg"
  | "non_veg_grills"
  | "thali_north_indian"
  | "momos_street_food"
  | "chinese_fast_food"
  | "family_restaurant"
  | "cafe_continental"
  | "bakery_cafe"
  | "snacks_cafe"
  | "dhaba_budget"
  | "bar_dining";

// Chandrapur district's curated hotel/resort directory.
export type HotelCategory = "city_hotel" | "resort_farm_stay" | "tadoba_safari_resort";

export type AttractionSource = "curated" | "community";

// Places you can review, rate and photograph. A curated row comes from a
// hand-verified dataset (e.g. the Chandrapur pilot); a community row is
// created on the fly the first time someone opens a place found through
// live map search anywhere else in India.
export interface Attraction {
  id: number;
  external_id: string;
  source: AttractionSource;
  name: string;
  district?: string | null;
  state?: string | null;
  category: string;
  area?: string | null;
  lat: number;
  lng: number;
  coordinates_verified: boolean;
  distance_from_chandrapur_km?: number | null;
  distance_from_nagpur_km?: number | null;
  distance_from_nagpur_airport_km?: number | null;
  opening_access?: string | null;
  entry_fee_status?: string | null;
  transportation?: string | null;
  data_quality_note?: string | null;
  source_urls: string[];
  dataset_prepared_on?: string | null;
  phone?: string | null;
  price_tier?: string | null;
  specialty?: string | null;
  // A rating snapshot from an external source (e.g. Google Maps at seed
  // time) — separate from avg_rating/review_count below, which are always
  // this app's own review aggregate.
  external_rating?: number | null;
  external_rating_count?: number | null;
  external_rating_source?: string | null;
  // Official online booking/permit portal (e.g. a national park's safari
  // slot booking site).
  booking_url?: string | null;
  // Facility list — hotels/resorts (AC Rooms, Pool, Restaurant, ...).
  amenities: string[];
  photo_urls: string[];
  avg_rating?: number | null;
  review_count: number;
}

export interface Review {
  id: number;
  user_id: number;
  username: string;
  rating: number;
  comment?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AttractionDetail extends Attraction {
  reviews: Review[];
  my_review: Review | null;
}

export const listAttractions = async (district?: string): Promise<Attraction[]> => {
  const res = await api.get("/api/v1/attractions", { params: district ? { district } : undefined });
  return res.data;
};

export const getAttraction = async (id: number): Promise<AttractionDetail> => {
  const res = await api.get(`/api/v1/attractions/${id}`);
  return res.data;
};

// Turns a live map search/nearby result into a reviewable, photographable
// Attraction — creating a lightweight "community" row the first time this
// exact place (matched by OSM id, or by coordinates+name as a fallback) is
// opened. Idempotent: resolving the same place again returns the same row.
export const resolveAttraction = async (place: Place): Promise<Attraction> => {
  const res = await api.post("/api/v1/attractions/resolve", {
    name: place.name,
    lat: place.lat,
    lng: place.lng,
    category: place.category,
    area: place.address,
    district: place.district,
    osm_type: place.osm_type,
    osm_id: place.osm_id,
  });
  return res.data;
};

export const uploadAttractionPhoto = async (
  attractionId: number,
  file: File
): Promise<Attraction> => {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post(`/api/v1/attractions/${attractionId}/photos`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const submitReview = async (
  attractionId: number,
  rating: number,
  comment: string
): Promise<Review> => {
  const res = await api.post(`/api/v1/attractions/${attractionId}/reviews`, {
    rating,
    comment: comment.trim() || null,
  });
  return res.data;
};

export const deleteMyReview = async (attractionId: number): Promise<void> => {
  await api.delete(`/api/v1/attractions/${attractionId}/reviews`);
};

export interface Favorite {
  id: number;
  name: string;
  lat: number;
  lng: number;
  category?: string;
  address?: string;
  opening_hours?: string;
  website?: string;
  created_at: string;
}

export const listFavorites = async (): Promise<Favorite[]> => {
  const res = await api.get("/api/v1/favorites");
  return res.data;
};

export const addFavorite = async (place: {
  name: string;
  lat: number;
  lng: number;
  category?: string;
  address?: string;
  opening_hours?: string;
  website?: string;
}): Promise<Favorite> => {
  const res = await api.post("/api/v1/favorites", place);
  return res.data;
};

export const removeFavorite = async (favoriteId: number): Promise<void> => {
  await api.delete(`/api/v1/favorites/${favoriteId}`);
};
