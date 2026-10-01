"""Curated Nagpur district tourism starter dataset.

Transcribed from the supplied "Nagpur Tourism Dataset - BharatDarshan AI
2026" PDF (prepared 2026-09-09). The source explicitly marks coordinates as
requiring manual verification; the approximate map positions below are only
for discovery and are deliberately flagged as unverified by the migration.
"""

DATASET_PREPARED_ON = "2026-09-09"

SOURCES = {
    "S1": "https://nagpur.gov.in/tourist-places/",
    "S2": "https://maharashtratourism.gov.in/districts/nagpur/",
    "S3": "https://maharashtratourism.gov.in/heritage/deekshabhoomi/",
    "S4": "https://nagpur.gov.in/history/",
    "S5": "https://nagpur.gov.in/slider/dragon-palace-temple/",
    "S6": "https://maharashtratourism.gov.in/temple/ramtek-khindsi/",
    "S7": "https://nagpur.gov.in/tourist-place/khindsi-lake/",
    "S8": "https://nagpur.gov.in/tourist-place/khekranala-lake/",
    "S9": "https://nagpur.gov.in/tourist-place/totladoh/",
    "S10": "https://nagpur.gov.in/mr/nnnnnnnn-nnnnnn/",
    "S11": "https://nagpur.gov.in/tourist-place/gandhi-sagar-lake/",
    "S12": "https://nagpur.gov.in/tourist-place/satpuda-botanical-garden/",
}


def _sources(*codes: str) -> list[str]:
    return [SOURCES[code] for code in codes]


NAGPUR_ATTRACTIONS = [
    {"name": "Deekshabhoomi", "category": "religious_heritage", "area": "Ramdaspeth, Nagpur city", "lat": 21.1281, "lng": 79.0669, "distance_from_nagpur_km": 4, "distance_from_nagpur_airport_km": 7, "opening_access": "Public monument; confirm current visitor hours", "entry_fee_status": "Generally free; verify onsite rules", "transportation": "Metro/auto/cab; central city access", "data_quality_note": "Official attraction; current hours not stated on tourism page", "source_urls": _sources("S2", "S3")},
    {"name": "Zero Mile Marker", "category": "historical_fort", "area": "Civil Lines, Nagpur city", "lat": 21.1458, "lng": 79.0882, "distance_from_nagpur_km": 0, "distance_from_nagpur_airport_km": 9, "opening_access": "Roadside heritage landmark; daylight/evening visit", "entry_fee_status": "No standard entry fee", "transportation": "Metro/auto/cab; Civil Lines", "data_quality_note": "Official historical description; city distance uses the reference origin", "source_urls": _sources("S1", "S4")},
    {"name": "Dragon Palace Buddhist Temple", "category": "religious_heritage", "area": "Kamptee", "lat": 21.2315, "lng": 79.1943, "distance_from_nagpur_km": 18, "distance_from_nagpur_airport_km": 27, "opening_access": "Temple schedule; confirm current hours", "entry_fee_status": "Generally free; donations may apply", "transportation": "Local train/bus/cab to Kamptee, then auto", "data_quality_note": "Official attraction; operational details should be refreshed", "source_urls": _sources("S2", "S5")},
    {"name": "Ramtek Fort Temple", "category": "religious_heritage", "area": "Ramtek city", "lat": 21.3956, "lng": 79.3290, "distance_from_nagpur_km": 50, "distance_from_nagpur_airport_km": 57, "opening_access": "Temple access; daylight visit recommended", "entry_fee_status": "Generally free; local charges may apply", "transportation": "MSRTC/private bus or cab to Ramtek", "data_quality_note": "Maharashtra Tourism lists road connectivity; timings and fees are dynamic", "source_urls": _sources("S2", "S6")},
    {"name": "Khindsi Lake", "category": "lake_nature", "area": "Near Ramtek city", "lat": 21.3827, "lng": 79.3379, "distance_from_nagpur_km": 53, "distance_from_nagpur_airport_km": 60, "opening_access": "Daylight visit; boating depends on operator/weather", "entry_fee_status": "Boating/activity charges vary", "transportation": "Road to Ramtek/Khindsi by bus/cab/private vehicle", "data_quality_note": "District page confirms 53 km and boating/adventure activities", "source_urls": _sources("S1", "S7")},
    {"name": "Khekranala Lake", "category": "lake_nature", "area": "Khapa range", "lat": 21.3510, "lng": 79.1690, "distance_from_nagpur_km": 65, "distance_from_nagpur_airport_km": 72, "opening_access": "Daylight visit recommended", "entry_fee_status": "Local/MTDC activity or parking charges may apply", "transportation": "Private vehicle/cab via Chhindwara Road/Khapa", "data_quality_note": "District page confirms 65 km; forest/dam conditions may change", "source_urls": _sources("S1", "S8")},
    {"name": "Totladoh Dam", "category": "lake_nature", "area": "Near Ramtek / Pench corridor", "lat": 21.6550, "lng": 79.3470, "distance_from_nagpur_km": 80, "distance_from_nagpur_airport_km": 87, "opening_access": "Access may be restricted; verify before travel", "entry_fee_status": "Not standardized", "transportation": "Private vehicle/cab toward Ramtek/Pench corridor", "data_quality_note": "District page confirms 80 km; do not assume dam premises are unrestricted", "source_urls": _sources("S1", "S9")},
    {"name": "Shree Mahalaxmi Jagdamba Temple", "category": "religious_heritage", "area": "Koradi", "lat": 21.2472, "lng": 79.0478, "distance_from_nagpur_km": 15, "distance_from_nagpur_airport_km": 22, "opening_access": "Temple schedule; festival periods may be crowded", "entry_fee_status": "Generally free; offerings optional", "transportation": "City bus/auto/cab to Koradi", "data_quality_note": "Maharashtra Tourism states about 15 km north of Nagpur", "source_urls": _sources("S2")},
    {"name": "Adasa Ganpati Temple", "category": "religious_heritage", "area": "Adasa", "lat": 21.4230, "lng": 78.9480, "distance_from_nagpur_km": 43, "distance_from_nagpur_airport_km": 50, "opening_access": "Temple schedule; daylight visit recommended", "entry_fee_status": "Generally free; offerings optional", "transportation": "Road via Saoner-Kalmeshwar side; bus/cab", "data_quality_note": "District page states 43 km northwest of Nagpur", "source_urls": _sources("S10")},
    {"name": "Nagardhan Fort", "category": "historical_fort", "area": "Nagardhan, near Ramtek city", "lat": 21.3650, "lng": 79.3420, "distance_from_nagpur_km": 38, "distance_from_nagpur_airport_km": 45, "opening_access": "Daylight heritage visit recommended", "entry_fee_status": "Verify locally", "transportation": "Road/cab toward Ramtek, then Nagardhan", "data_quality_note": "District history page states 38 km northeast of Nagpur", "source_urls": _sources("S4")},
    {"name": "Gandhi Sagar Lake", "category": "lake_nature", "area": "Mahal, Nagpur city", "lat": 21.1509, "lng": 79.1038, "distance_from_nagpur_km": 3, "distance_from_nagpur_airport_km": 10, "opening_access": "Public lakefront; boating availability can vary", "entry_fee_status": "Lake access generally free; boating may be charged", "transportation": "Auto/cab; near Raman Science Centre", "data_quality_note": "District page confirms boating facility but not current schedule", "source_urls": _sources("S1", "S11")},
    {"name": "Satpuda Botanical Garden", "category": "social_educational", "area": "Seminary Hills, Nagpur city", "lat": 21.1510, "lng": 79.0480, "distance_from_nagpur_km": 5, "distance_from_nagpur_airport_km": 11, "opening_access": "Garden access; confirm current opening hours", "entry_fee_status": "Verify current fee/status", "transportation": "City bus/auto/cab to Seminary Hills", "data_quality_note": "Official attraction; rare plants and educational value confirmed", "source_urls": _sources("S1", "S12")},
    {"name": "Ambala Lake & Temples", "category": "religious_heritage", "area": "Ramtek", "lat": 21.3967, "lng": 79.3175, "distance_from_nagpur_km": 51, "distance_from_nagpur_airport_km": 58, "opening_access": "Daylight visit recommended", "entry_fee_status": "Generally free", "transportation": "MSRTC/private bus or cab to Ramtek", "data_quality_note": "Famous pilgrimage spot near Ramtek Fort; hosts rituals.", "source_urls": _sources("S6")},
    {"name": "Karpur Baoli", "category": "historical_fort", "area": "Ramtek", "lat": 21.3970, "lng": 79.3240, "distance_from_nagpur_km": 50, "distance_from_nagpur_airport_km": 57, "opening_access": "Daylight visit recommended", "entry_fee_status": "Generally free", "transportation": "MSRTC/private bus or cab to Ramtek", "data_quality_note": "Ancient stepwell with historical significance.", "source_urls": _sources("S4")},
    {"name": "Shantinath Jain Temple", "category": "religious_heritage", "area": "Ramtek", "lat": 21.3995, "lng": 79.3305, "distance_from_nagpur_km": 50, "distance_from_nagpur_airport_km": 57, "opening_access": "Temple schedule; confirm current hours", "entry_fee_status": "Generally free", "transportation": "MSRTC/private bus or cab to Ramtek", "data_quality_note": "Ancient Jain pilgrimage site in Ramtek.", "source_urls": _sources("S6")},
]
