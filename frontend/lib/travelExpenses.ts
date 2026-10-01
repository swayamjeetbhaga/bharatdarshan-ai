export interface DynamicFare {
  distanceKm: number;
  durationMin: number;
  isSameLocation: boolean; // < 2.5 km
  bus: {
    available: boolean;
    fare: number | null; // e.g. 70
    label: string; // e.g. "MSRTC / State Transport / Bus"
    subLabel: string;
  };
  taxi: {
    available: boolean;
    sharedFare: number | null; // e.g. 150
    privateFare: number | null; // e.g. 1400
    label: string;
    subLabel: string;
  };
  railway: {
    available: boolean;
    fare: number | null; // e.g. 45
    label: string;
    note?: string;
  };
}

export interface TransitHub {
  name: string;
  state?: string;
  district?: string;
  lat: number;
  lng: number;
  hasRailway: boolean;
}

export const ALL_INDIAN_HUBS: TransitHub[] = [
  // Maharashtra - Nagpur District Hubs & Talukas
  { name: "Nagpur", district: "Nagpur", state: "Maharashtra", lat: 21.1458, lng: 79.0882, hasRailway: true },
  { name: "Ramtek", district: "Nagpur", state: "Maharashtra", lat: 21.3956, lng: 79.3290, hasRailway: true },
  { name: "Kamptee", district: "Nagpur", state: "Maharashtra", lat: 21.2315, lng: 79.1943, hasRailway: true },
  { name: "Saoner", district: "Nagpur", state: "Maharashtra", lat: 21.3850, lng: 78.9180, hasRailway: true },
  { name: "Kalmeshwar", district: "Nagpur", state: "Maharashtra", lat: 21.2330, lng: 78.9160, hasRailway: true },
  { name: "Katol", district: "Nagpur", state: "Maharashtra", lat: 21.2720, lng: 78.5870, hasRailway: true },
  { name: "Umred", district: "Nagpur", state: "Maharashtra", lat: 20.8540, lng: 79.3260, hasRailway: true },
  { name: "Hingna", district: "Nagpur", state: "Maharashtra", lat: 21.0760, lng: 78.9710, hasRailway: false },
  { name: "Narkhed", district: "Nagpur", state: "Maharashtra", lat: 21.5030, lng: 78.5370, hasRailway: true },
  { name: "Mouda", district: "Nagpur", state: "Maharashtra", lat: 21.2710, lng: 79.3950, hasRailway: false },
  { name: "Kuhi", district: "Nagpur", state: "Maharashtra", lat: 20.9790, lng: 79.3560, hasRailway: false },
  { name: "Bhiwapur", district: "Nagpur", state: "Maharashtra", lat: 20.7620, lng: 79.5240, hasRailway: true },
  { name: "Parsioni", district: "Nagpur", state: "Maharashtra", lat: 21.3780, lng: 79.1820, hasRailway: false },

  // Maharashtra - Chandrapur District Hubs & Talukas
  { name: "Chandrapur", district: "Chandrapur", state: "Maharashtra", lat: 19.95, lng: 79.298, hasRailway: true },
  { name: "Warora", district: "Chandrapur", state: "Maharashtra", lat: 20.233, lng: 79.00, hasRailway: true },
  { name: "Ballarpur", district: "Chandrapur", state: "Maharashtra", lat: 19.835, lng: 79.35, hasRailway: true },
  { name: "Bhadrawati", district: "Chandrapur", state: "Maharashtra", lat: 20.15, lng: 79.12, hasRailway: true },
  { name: "Gadchandur", district: "Chandrapur", state: "Maharashtra", lat: 19.74, lng: 79.16, hasRailway: false },
  { name: "Jiwati", district: "Chandrapur", state: "Maharashtra", lat: 19.65, lng: 79.01, hasRailway: false },
  { name: "Rajura", district: "Chandrapur", state: "Maharashtra", lat: 19.78, lng: 79.36, hasRailway: false },
  { name: "Mul", district: "Chandrapur", state: "Maharashtra", lat: 20.07, lng: 79.67, hasRailway: true },
  { name: "Chimur", district: "Chandrapur", state: "Maharashtra", lat: 20.48, lng: 79.36, hasRailway: false },
  { name: "Brahmapuri", district: "Chandrapur", state: "Maharashtra", lat: 20.61, lng: 79.85, hasRailway: true },

  // Maharashtra - Wardha, Amravati & Other Vidarbha Hubs
  { name: "Wardha", district: "Wardha", state: "Maharashtra", lat: 20.7453, lng: 78.6022, hasRailway: true },
  { name: "Sevagram", district: "Wardha", state: "Maharashtra", lat: 20.7186, lng: 78.6658, hasRailway: true },
  { name: "Hinganghat", district: "Wardha", state: "Maharashtra", lat: 20.5650, lng: 78.8410, hasRailway: true },
  { name: "Arvi", district: "Wardha", state: "Maharashtra", lat: 20.9980, lng: 78.2320, hasRailway: true },
  { name: "Amravati", district: "Amravati", state: "Maharashtra", lat: 20.9374, lng: 77.7796, hasRailway: true },
  { name: "Yavatmal", district: "Yavatmal", state: "Maharashtra", lat: 20.3888, lng: 78.1204, hasRailway: false },
  { name: "Wani", district: "Yavatmal", state: "Maharashtra", lat: 20.0650, lng: 78.9560, hasRailway: true },
  { name: "Gadchiroli", district: "Gadchiroli", state: "Maharashtra", lat: 20.1849, lng: 79.9948, hasRailway: false },
  { name: "Gondia", district: "Gondia", state: "Maharashtra", lat: 21.4600, lng: 80.2000, hasRailway: true },
  { name: "Bhandara", district: "Bhandara", state: "Maharashtra", lat: 21.1700, lng: 79.6500, hasRailway: true },

  // Maharashtra - Western & Central
  { name: "Mumbai", district: "Mumbai", state: "Maharashtra", lat: 18.922, lng: 72.8347, hasRailway: true },
  { name: "Pune", district: "Pune", state: "Maharashtra", lat: 18.5204, lng: 73.8567, hasRailway: true },
  { name: "Nashik", district: "Nashik", state: "Maharashtra", lat: 19.9975, lng: 73.7898, hasRailway: true },
  { name: "Chhatrapati Sambhajinagar", district: "Aurangabad", state: "Maharashtra", lat: 19.8762, lng: 75.3433, hasRailway: true },
  { name: "Kolhapur", district: "Kolhapur", state: "Maharashtra", lat: 16.705, lng: 74.2433, hasRailway: true },
  { name: "Solapur", district: "Solapur", state: "Maharashtra", lat: 17.6599, lng: 75.9064, hasRailway: true },

  // Major All-India Metros & Tourism Hubs
  { name: "New Delhi", district: "Delhi", state: "Delhi", lat: 28.6139, lng: 77.209, hasRailway: true },
  { name: "Jaipur", district: "Jaipur", state: "Rajasthan", lat: 26.9124, lng: 75.7873, hasRailway: true },
  { name: "Varanasi", district: "Varanasi", state: "Uttar Pradesh", lat: 25.3176, lng: 82.9739, hasRailway: true },
  { name: "Agra", district: "Agra", state: "Uttar Pradesh", lat: 27.1767, lng: 78.0081, hasRailway: true },
  { name: "Bengaluru", district: "Bengaluru", state: "Karnataka", lat: 12.9716, lng: 77.5946, hasRailway: true },
  { name: "Hyderabad", district: "Hyderabad", state: "Telangana", lat: 17.385, lng: 78.4867, hasRailway: true },
  { name: "Kolkata", district: "Kolkata", state: "West Bengal", lat: 22.5726, lng: 88.3639, hasRailway: true },
  { name: "Chennai", district: "Chennai", state: "Tamil Nadu", lat: 13.0827, lng: 80.2707, hasRailway: true },
  { name: "Goa (Panaji)", district: "North Goa", state: "Goa", lat: 15.4909, lng: 73.8278, hasRailway: true },
  { name: "Kochi", district: "Ernakulam", state: "Kerala", lat: 9.9312, lng: 76.2673, hasRailway: true },
  { name: "Bhopal", district: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lng: 77.4126, hasRailway: true },
  { name: "Indore", district: "Indore", state: "Madhya Pradesh", lat: 22.7196, lng: 75.8577, hasRailway: true },
];

export function haversineDistKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Checks if a route between origin and destination has direct railway connectivity.
 */
function hasDirectRailCorridor(originName: string, destName: string): boolean {
  const originLower = originName.toLowerCase();
  const destLower = destName.toLowerCase();

  // Non-rail destinations (wildlife reserves, remote hill forts, lakes in hills)
  if (
    destLower.includes("tadoba") ||
    destLower.includes("manikgad") ||
    destLower.includes("ghoda jhari") ||
    destLower.includes("irai") ||
    destLower.includes("khekranala") ||
    destLower.includes("totladoh") ||
    destLower.includes("khindsi") ||
    destLower.includes("national park") ||
    destLower.includes("tiger reserve") ||
    destLower.includes("sanctuary") ||
    (destLower.includes("fort") && (destLower.includes("hill") || destLower.includes("jungle")))
  ) {
    return false;
  }

  // Major connected rail towns
  const railTowns = [
    "nagpur",
    "ramtek",
    "kamptee",
    "saoner",
    "kalmeshwar",
    "katol",
    "umred",
    "narkhed",
    "bhiwapur",
    "chandrapur",
    "warora",
    "ballarpur",
    "bhadrawati",
    "bhadravati",
    "mul",
    "brahmapuri",
    "wardha",
    "sevagram",
    "hinganghat",
    "arvi",
    "amravati",
    "gondia",
    "bhandara",
    "mumbai",
    "pune",
    "nashik",
    "kolhapur",
    "solapur",
    "delhi",
    "jaipur",
    "varanasi",
    "agra",
    "bengaluru",
    "hyderabad",
    "kolkata",
    "chennai",
    "bhopal",
    "indore",
  ];

  return railTowns.some((t) => originLower.includes(t));
}

/**
 * Calculates intuitive, realistic travel expenses based on exact coordinates and distance anywhere in India.
 */
export function estimateTravelExpenses(
  origin: { name: string; lat: number; lng: number },
  destination: { name: string; category?: string; lat: number; lng: number }
): DynamicFare {
  const distanceKm = Math.round(haversineDistKm(origin.lat, origin.lng, destination.lat, destination.lng) * 10) / 10;
  const isSameLocation = distanceKm < 2.5;

  const durationMin = Math.max(10, Math.round((distanceKm / 42) * 60));
  const destLower = destination.name.toLowerCase();
  const isWildlife = destination.category === "wildlife" || destLower.includes("tadoba") || destLower.includes("sanctuary") || destLower.includes("reserve");
  const isRemote = isWildlife || destLower.includes("fort") || destLower.includes("lake");

  // 1. If user is at the location (< 2.5 km)
  if (isSameLocation) {
    return {
      distanceKm,
      durationMin: 5,
      isSameLocation: true,
      bus: { available: true, fare: 10, label: "Walking / Local", subLabel: "Within 2 km" },
      taxi: { available: true, sharedFare: 30, privateFare: 60, label: "E-Rickshaw / Auto", subLabel: "Short local ride" },
      railway: { available: false, fare: null, label: "Local location" },
    };
  }

  // 2. Intra-city (< 6 km)
  if (distanceKm < 6) {
    return {
      distanceKm,
      durationMin: Math.round(distanceKm * 3.5),
      isSameLocation: false,
      bus: { available: true, fare: 15, label: "City Bus", subLabel: "Local city transit" },
      taxi: { available: true, sharedFare: 35, privateFare: 80, label: "Auto-Rickshaw", subLabel: "₹40–₹80 direct ride" },
      railway: { available: false, fare: null, label: "Local distance" },
    };
  }

  // 3. Short regional trips (6 to 25 km)
  if (distanceKm <= 25) {
    const busFare = Math.round(Math.max(20, distanceKm * 1.8) / 5) * 5;
    const sharedTaxi = Math.round((distanceKm * 3.5 + 20) / 10) * 10;
    const privateCab = Math.round((distanceKm * 18 + 150) / 50) * 50;
    const railOk = hasDirectRailCorridor(origin.name, destination.name);
    const railFare = railOk ? 30 : null;

    return {
      distanceKm,
      durationMin,
      isSameLocation: false,
      bus: { available: true, fare: busFare, label: "Bus / State Transport", subLabel: "Regular service" },
      taxi: { available: true, sharedFare: sharedTaxi, privateFare: privateCab, label: "Auto / Cab", subLabel: `Shared: ₹${sharedTaxi} | Private: ₹${privateCab}` },
      railway: {
        available: railOk,
        fare: railFare,
        label: railOk ? "Passenger / Express" : "No direct train",
        note: railOk ? "Direct station connection" : "Best reached by road",
      },
    };
  }

  // 4. Medium regional trips (25 to 70 km)
  if (distanceKm <= 70) {
    const busFare = Math.round((distanceKm * 1.6 + 10) / 5) * 5;
    let sharedTaxi = Math.round((distanceKm * 3.8 + 30) / 10) * 10;
    let privateCab = Math.round((distanceKm * 24 + 300) / 100) * 100;

    if (isWildlife) {
      sharedTaxi = Math.round((distanceKm * 4.2 + 50) / 10) * 10; // Shared safari cruiser
      privateCab = 1500; // Dedicated taxi / Gypsy pickup
    } else if (isRemote) {
      sharedTaxi = Math.round((distanceKm * 3.5 + 20) / 10) * 10;
      privateCab = 1200;
    }

    const railOk = hasDirectRailCorridor(origin.name, destination.name);
    const railFare = railOk ? (distanceKm > 40 ? 50 : 35) : null;

    return {
      distanceKm,
      durationMin,
      isSameLocation: false,
      bus: { available: true, fare: busFare, label: "Bus / State Transport", subLabel: "Frequent daily departures" },
      taxi: {
        available: true,
        sharedFare: sharedTaxi,
        privateFare: privateCab,
        label: isWildlife ? "Safari Cab / Taxi" : "Taxi / Cab",
        subLabel: isWildlife ? `Shared Jeep: ₹${sharedTaxi} | Private: ₹${privateCab}` : `Shared: ₹${sharedTaxi} | Private: ₹${privateCab}`,
      },
      railway: {
        available: railOk,
        fare: railFare,
        label: railOk ? "Express Train" : "No direct railway",
        note: railOk ? "Express/Passenger link" : isWildlife ? "Train to railhead + taxi" : "Take road/bus route",
      },
    };
  }

  // 5. Long regional & Inter-city trips (> 70 km)
  const busFare = Math.round((distanceKm * 1.5 + 20) / 10) * 10;
  const sharedTaxi = Math.round((distanceKm * 2.8 + 50) / 50) * 50;
  const privateCab = Math.round((distanceKm * 18 + 500) / 100) * 100;

  const railOk = hasDirectRailCorridor(origin.name, destination.name);
  const railFare = railOk ? Math.round((distanceKm * 0.7 + 20) / 5) * 5 : null;

  return {
    distanceKm,
    durationMin,
    isSameLocation: false,
    bus: { available: true, fare: busFare, label: "Express / AC Bus", subLabel: "Intercity bus service" },
    taxi: {
      available: true,
      sharedFare: sharedTaxi,
      privateFare: privateCab,
      label: "Outstation Cab / Taxi",
      subLabel: `Shared: ₹${sharedTaxi} | Private: ₹${privateCab}`,
    },
    railway: {
      available: railOk,
      fare: railFare,
      label: railOk ? "Express / Superfast" : "No direct train",
      note: railOk ? "Direct mainline train" : "Rail to hub + road transfer",
    },
  };
}

/**
 * Returns contextual preset starting locations based on attraction's district/state.
 */
export function getPresetsForAttraction(attraction: { district?: string | null; state?: string | null; lat: number; lng: number }): TransitHub[] {
  const distLower = (attraction.district || "").toLowerCase();
  const stateLower = (attraction.state || "").toLowerCase();

  // 1. Nagpur District Attractions
  if (distLower.includes("nagpur")) {
    const nagpurPresetOrder = [
      "Nagpur",
      "Ramtek",
      "Kamptee",
      "Saoner",
      "Kalmeshwar",
      "Katol",
      "Umred",
      "Hingna",
      "Chandrapur",
      "Wardha",
      "Mumbai",
      "Pune",
    ];
    return ALL_INDIAN_HUBS.filter((h) => nagpurPresetOrder.includes(h.name)).sort(
      (a, b) => nagpurPresetOrder.indexOf(a.name) - nagpurPresetOrder.indexOf(b.name)
    );
  }

  // 2. Chandrapur District Attractions
  if (distLower.includes("chandrapur")) {
    const chpPresetOrder = [
      "Chandrapur",
      "Warora",
      "Ballarpur",
      "Bhadrawati",
      "Rajura",
      "Mul",
      "Chimur",
      "Brahmapuri",
      "Gadchandur",
      "Jiwati",
      "Nagpur",
      "Mumbai",
      "Pune",
    ];
    return ALL_INDIAN_HUBS.filter((h) => chpPresetOrder.includes(h.name)).sort(
      (a, b) => chpPresetOrder.indexOf(a.name) - chpPresetOrder.indexOf(b.name)
    );
  }

  // 3. Wardha District Attractions
  if (distLower.includes("wardha")) {
    const wardhaPresetOrder = [
      "Wardha",
      "Sevagram",
      "Hinganghat",
      "Arvi",
      "Nagpur",
      "Chandrapur",
      "Mumbai",
      "Pune",
    ];
    return ALL_INDIAN_HUBS.filter((h) => wardhaPresetOrder.includes(h.name)).sort(
      (a, b) => wardhaPresetOrder.indexOf(a.name) - wardhaPresetOrder.indexOf(b.name)
    );
  }

  // 4. Other Maharashtra Districts
  if (stateLower.includes("maharashtra") || distLower.includes("pune") || distLower.includes("mumbai") || distLower.includes("nashik")) {
    const sameDistrict = ALL_INDIAN_HUBS.filter((h) => h.district?.toLowerCase() === distLower);
    const keyStateHubs = ["Mumbai", "Pune", "Nagpur", "Nashik", "Chhatrapati Sambhajinagar", "Kolhapur", "Chandrapur"];
    const otherHubs = ALL_INDIAN_HUBS.filter((h) => keyStateHubs.includes(h.name) && !sameDistrict.some((d) => d.name === h.name));
    return [...sameDistrict, ...otherHubs].slice(0, 10);
  }

  // 5. All-India destinations (sort closest hubs to the attraction's coordinates)
  return [...ALL_INDIAN_HUBS]
    .map((hub) => ({ hub, dist: haversineDistKm(attraction.lat, attraction.lng, hub.lat, hub.lng) }))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 8)
    .map((item) => item.hub);
}

/**
 * Finds the nearest hub to a given lat/lng coordinate.
 */
export function findNearestLocation(lat: number, lng: number): { location: TransitHub; distanceKm: number } {
  let best = ALL_INDIAN_HUBS[0];
  let min = haversineDistKm(lat, lng, best.lat, best.lng);

  for (const loc of ALL_INDIAN_HUBS) {
    const d = haversineDistKm(lat, lng, loc.lat, loc.lng);
    if (d < min) {
      min = d;
      best = loc;
    }
  }
  return { location: best, distanceKm: Math.round(min * 10) / 10 };
}
