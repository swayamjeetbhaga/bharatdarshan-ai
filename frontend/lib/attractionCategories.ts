import type { CuratedCategory, FoodCategory, HotelCategory } from "./api";

export const CATEGORY_LABELS: Record<CuratedCategory, string> = {
  wildlife: "Wildlife",
  lake_nature: "Lake & Nature",
  religious_heritage: "Religious & Heritage",
  historical_fort: "Historical Fort",
  social_educational: "Social & Educational",
};

export const CATEGORY_ICONS: Record<CuratedCategory, string> = {
  wildlife: "🐯",
  lake_nature: "🌊",
  religious_heritage: "🛕",
  historical_fort: "🏰",
  social_educational: "🤝",
};

export const CATEGORY_ORDER: CuratedCategory[] = [
  "wildlife",
  "lake_nature",
  "religious_heritage",
  "historical_fort",
  "social_educational",
];

export const FOOD_CATEGORY_LABELS: Record<FoodCategory, string> = {
  fine_dining_veg: "Fine Dining (Veg)",
  non_veg_grills: "Non-Veg & Grills",
  thali_north_indian: "Thali & North Indian",
  momos_street_food: "Momos & Street Food",
  chinese_fast_food: "Chinese & Fast Food",
  family_restaurant: "Family Restaurant",
  cafe_continental: "Cafe & Continental",
  bakery_cafe: "Bakery & Cafe",
  snacks_cafe: "Snacks & Cafe",
  dhaba_budget: "Dhaba & Budget Eats",
  bar_dining: "Bar & Dining",
};

export const FOOD_CATEGORY_ICONS: Record<FoodCategory, string> = {
  fine_dining_veg: "🍽️",
  non_veg_grills: "🍢",
  thali_north_indian: "🍛",
  momos_street_food: "🥟",
  chinese_fast_food: "🥡",
  family_restaurant: "👨‍👩‍👧",
  cafe_continental: "🍝",
  bakery_cafe: "🧁",
  snacks_cafe: "🥤",
  dhaba_budget: "🍲",
  bar_dining: "🍸",
};

export const HOTEL_CATEGORY_LABELS: Record<HotelCategory, string> = {
  city_hotel: "City Hotel",
  resort_farm_stay: "Resort & Farm Stay",
  tadoba_safari_resort: "Tadoba Safari Resort",
};

export const HOTEL_CATEGORY_ICONS: Record<HotelCategory, string> = {
  city_hotel: "🏨",
  resort_farm_stay: "🏕️",
  tadoba_safari_resort: "🐅",
};

const FOOD_CATEGORIES = new Set<string>(Object.keys(FOOD_CATEGORY_LABELS));
const HOTEL_CATEGORIES = new Set<string>(Object.keys(HOTEL_CATEGORY_LABELS));

// True for any place in the curated Chandrapur restaurant directory —
// used so the "Restaurants" filter can prefer this real data over a live
// OSM search when browsing a district it covers.
export function isFoodCategory(category: string): category is FoodCategory {
  return FOOD_CATEGORIES.has(category);
}

// Same idea as isFoodCategory, for the curated hotel/resort directory.
export function isHotelCategory(category: string): category is HotelCategory {
  return HOTEL_CATEGORIES.has(category);
}

function isCurated(category: string): category is CuratedCategory {
  return category in CATEGORY_LABELS;
}

// A community-resolved place (anywhere in India, outside our curated
// datasets) carries whatever free-text category the map search gave it —
// these fall back to a title-cased label and a generic pin icon.
export function categoryLabel(category: string): string {
  if (isCurated(category)) return CATEGORY_LABELS[category];
  if (isFoodCategory(category)) return FOOD_CATEGORY_LABELS[category];
  if (isHotelCategory(category)) return HOTEL_CATEGORY_LABELS[category];
  return category
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

const KEYWORD_ICONS: [RegExp, string][] = [
  [/hotel|lodg|resort|guest.?house/i, "🏨"],
  [/bakery|bakers|cake|pastry/i, "🧁"],
  [/bar\b|liquor|pub/i, "🍸"],
  [/dhaba/i, "🍲"],
  [/momo/i, "🥟"],
  [/restaurant|cafe|food|eatery/i, "🍽️"],
  [/temple|mosque|church|shrine|religious/i, "🛕"],
  [/fort|palace|monument|tomb|historic|museum/i, "🏰"],
  [/lake|river|dam|waterfall|nature|park|forest/i, "🌊"],
  [/wildlife|tiger|sanctuary|zoo/i, "🐯"],
  [/administrative|city|town|village|district|state|county|place/i, "📍"],
];

export function categoryIcon(category: string): string {
  if (isCurated(category)) return CATEGORY_ICONS[category];
  if (isFoodCategory(category)) return FOOD_CATEGORY_ICONS[category];
  if (isHotelCategory(category)) return HOTEL_CATEGORY_ICONS[category];
  const match = KEYWORD_ICONS.find(([re]) => re.test(category));
  return match ? match[1] : "📍";
}
