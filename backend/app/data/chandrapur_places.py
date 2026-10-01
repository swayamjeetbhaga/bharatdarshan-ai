"""Seed dataset for Chandrapur district tourist attractions.

Sourced from the "Chandrapur Tourism Dataset" pilot document (prepared
2026-09-02) whose core facts (category, area, distances, access notes,
transportation, data-quality notes and source links) come from the
official government tourism pages listed in SOURCES below.

Coordinates are NOT part of that source document — it explicitly asks for
them to be added "only after verifying each location manually". The
lat/lng below are hand-added approximations from general knowledge of
these well-known landmarks, so `coordinates_verified` is False for every
record until someone checks them against a mapping/routing provider.

Ratings, reviews and photos are intentionally absent — the source
document excludes them ("change frequently and require an API-backed
refresh"); this app collects ratings/reviews from its own users instead
of fabricating any.
"""

DATASET_PREPARED_ON = "2026-09-02"

SOURCES = {
    "S1": "https://chanda.nic.in/en/tourist-places/",
    "S2": "https://maharashtratourism.gov.in/districts/chandrapur/",
    "S3": "https://chanda.nic.in/en/tourist-place/ghoda_jhari_lake/",
    "S4": "https://zpchandrapur.maharashtra.gov.in/en/tourism/",
    "S5": "https://chanda.nic.in/en/tourist-place/anchaleshwar-temple/",
    "S6": "https://en.wikipedia.org/wiki/Ballarpur_Fort",
    "S7": "https://en.wikipedia.org/wiki/Manikgad",
    "S8": "https://anandwan.in/",
}


def _sources(*codes: str) -> list[str]:
    return [SOURCES[code] for code in codes]


# category values match AttractionCategory in app/schemas/attraction.py
CHANDRAPUR_ATTRACTIONS = [
    {
        "name": "Tadoba-Andhari Tiger Reserve",
        "category": "wildlife",
        "area": "Tadoba / Moharli side",
        "lat": 20.2333,
        "lng": 79.3667,
        "distance_from_chandrapur_km": 45,
        "distance_from_nagpur_km": 132,
        "opening_access": "Safari slots vary; advance permit required",
        "entry_fee_status": "Variable; verify official booking portal",
        "transportation": "Taxi/private vehicle; Chandrapur railhead",
        "data_quality_note": "Official attraction; distance depends on selected gate",
        "source_urls": _sources("S1", "S2"),
        # Maharashtra Forest Department's official safari permit portal.
        "booking_url": "https://mytadoba.mahaforest.gov.in/",
    },
    {
        "name": "Ghoda Jhari Lake",
        "category": "lake_nature",
        "area": "Nagbhir tehsil",
        "lat": 20.58,
        "lng": 79.95,
        "distance_from_chandrapur_km": 106,
        "distance_from_nagpur_km": 97,
        "opening_access": "Daylight visit recommended",
        "entry_fee_status": "Local charges may apply",
        "transportation": "Road via Nagpur-Chandrapur highway + 6 km diversion",
        "data_quality_note": "Official distances",
        "source_urls": _sources("S1", "S3"),
    },
    {
        "name": "Mahakali Temple",
        "category": "religious_heritage",
        "area": "Chandrapur city",
        "lat": 19.9515,
        "lng": 79.2989,
        "distance_from_chandrapur_km": 3,
        "distance_from_nagpur_km": 153,
        "opening_access": "Temple schedule; confirm locally",
        "entry_fee_status": "Generally free; offerings optional",
        "transportation": "City bus/auto/taxi; near Chandrapur station",
        "data_quality_note": "City route distances are approximate",
        "source_urls": _sources("S2", "S4"),
    },
    {
        "name": "Anchaleshwar Mahadev Temple",
        "category": "religious_heritage",
        "area": "Near Gond Fort, Chandrapur",
        "lat": 19.953,
        "lng": 79.301,
        "distance_from_chandrapur_km": 3,
        "distance_from_nagpur_km": 148,
        "opening_access": "Approx. 5:00 AM-5:00 PM; verify locally",
        "entry_fee_status": "Generally free",
        "transportation": "Auto from Chandrapur bus depot; station about 3 km",
        "data_quality_note": "Chandrapur and Nagpur airport distances are official",
        "source_urls": _sources("S1", "S5"),
    },
    {
        "name": "Chandrapur Fort (Gond Raja Fort)",
        "category": "historical_fort",
        "area": "Chandrapur city",
        "lat": 19.95,
        "lng": 79.298,
        "distance_from_chandrapur_km": 3,
        "distance_from_nagpur_km": 153,
        "opening_access": "Open-access heritage area; daylight visit",
        "entry_fee_status": "Usually free; verify locally",
        "transportation": "City auto/taxi; near railway station",
        "data_quality_note": "City route distances are approximate",
        "source_urls": _sources("S2", "S4"),
    },
    {
        "name": "Ballarpur Fort",
        "category": "historical_fort",
        "area": "Ballarpur",
        "lat": 19.835,
        "lng": 79.35,
        "distance_from_chandrapur_km": 16,
        "distance_from_nagpur_km": 170,
        "opening_access": "Daylight visit recommended",
        "entry_fee_status": "Usually free; verify locally",
        "transportation": "Bus/local train/taxi to Ballarpur",
        "data_quality_note": "Fort is open to public; distances approximate",
        "source_urls": _sources("S2", "S6"),
    },
    {
        "name": "Manikgad Fort",
        "category": "historical_fort",
        "area": "Jiwati-Gadchandur area",
        "lat": 19.72,
        "lng": 79.1,
        "distance_from_chandrapur_km": 35,
        "distance_from_nagpur_km": 190,
        "opening_access": "Approx. 9:00 AM-5:00 PM; daylight trek",
        "entry_fee_status": "Usually free; verify locally",
        "transportation": "Private vehicle/taxi via Gadchandur",
        "data_quality_note": "Remote hill fort; carry water and avoid solo late visits",
        "source_urls": _sources("S2", "S7"),
    },
    {
        "name": "Bhadravati Jain Temple",
        "category": "religious_heritage",
        "area": "Bhadravati",
        "lat": 20.15,
        "lng": 79.12,
        "distance_from_chandrapur_km": 32,
        "distance_from_nagpur_km": 128,
        "opening_access": "Temple schedule; confirm locally",
        "entry_fee_status": "Generally free; donations optional",
        "transportation": "Road/rail to Bhadravati, then local auto",
        "data_quality_note": "Distance and timings should be verified before production use",
        "source_urls": _sources("S2"),
    },
    {
        "name": "Ramala Talav",
        "category": "lake_nature",
        "area": "Chandrapur city",
        "lat": 19.945,
        "lng": 79.295,
        "distance_from_chandrapur_km": 2,
        "distance_from_nagpur_km": 151,
        "opening_access": "Daylight/evening; confirm local restrictions",
        "entry_fee_status": "Usually free",
        "transportation": "City auto/taxi",
        "data_quality_note": "Route distances are approximate",
        "source_urls": _sources("S2"),
    },
    {
        "name": "Junona Lake",
        "category": "lake_nature",
        "area": "Junona, near Chandrapur",
        "lat": 19.98,
        "lng": 79.26,
        "distance_from_chandrapur_km": 15,
        "distance_from_nagpur_km": 165,
        "opening_access": "Daylight visit recommended",
        "entry_fee_status": "Verify locally",
        "transportation": "Road by taxi/private vehicle",
        "data_quality_note": "Secondary attraction; verify route before production use",
        "source_urls": _sources("S2"),
    },
    {
        "name": "Irai Lake / Dam View Area",
        "category": "lake_nature",
        "area": "Near Chandrapur",
        "lat": 19.9,
        "lng": 79.2,
        "distance_from_chandrapur_km": 15,
        "distance_from_nagpur_km": 145,
        "opening_access": "Access can be restricted; verify before visit",
        "entry_fee_status": "Not standardized",
        "transportation": "Road by taxi/private vehicle",
        "data_quality_note": "Do not treat dam premises as unrestricted tourist access",
        "source_urls": _sources("S2"),
    },
    {
        "name": "Anandwan",
        "category": "social_educational",
        "area": "Warora",
        "lat": 20.2333,
        "lng": 79.0,
        "distance_from_chandrapur_km": 47,
        "distance_from_nagpur_km": 108,
        "opening_access": "Visitor access and timings must be confirmed",
        "entry_fee_status": "Confirm with institution",
        "transportation": "Train/bus to Warora, then local auto/taxi",
        "data_quality_note": "Useful optional project record; not in the core official attraction list",
        "source_urls": _sources("S8"),
    },
]
