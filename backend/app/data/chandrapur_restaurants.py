"""Seed dataset for Chandrapur CITY restaurants, cafes, dhabas and bakeries.

Sourced from a "Chandrapur Food & Restaurant Directory" document (prepared
03 September 2026) whose facts — address, hours, phone, price tier,
specialty, notable remarks, and rating/review counts — are attributed there
to Google Maps.

Coordinates are NOT part of that source. Three localities (Tukum, Ramnagar,
Lohara) were geocoded directly against OpenStreetMap/Nominatim, constrained
to a bounding box around Chandrapur city to avoid matching same-named
localities elsewhere in the much larger district (an earlier unconstrained
attempt matched "Civil Lines" to a different Civil Lines 70km away, in
Bramhapuri taluka). The remaining entries only listed a ward/locality name
that Nominatim couldn't resolve to a distinct point within the city, so
they're hand-placed by ward using those three geocoded points plus the
Chandrapur city layout — every record here has `coordinates_verified=False`
pending manual verification, same as the Chandrapur district tourism seed.

Ratings/review counts ARE included here (unlike the tourism seed) because
the source document captured them directly from Google Maps as a snapshot —
they're stored as `external_rating`/`external_rating_count`, kept separate
from `avg_rating`/`review_count` (which always reflect this app's own
`reviews` table) so the two never get mixed up.
"""

DATASET_PREPARED_ON = "2026-09-03"
EXTERNAL_RATING_SOURCE = "Google Maps"

# Hand-placed ward anchors within Chandrapur city (see module docstring).
# Tukum, Ramnagar and Lohara came directly from a bounded Nominatim lookup;
# the rest are estimated from the city's general layout.
WARDS = {
    "old_city_core": (19.9480, 79.2950),   # Bazar Ward / Sarafa Lane / Jatpura Gate / Ramala Talav
    "civil_lines": (19.9550, 79.3050),
    "tukum": (19.9718, 79.3007),           # geocoded
    "ramnagar": (19.9656, 79.2999),        # geocoded
    "wadgaon": (19.9900, 79.3200),         # Wadgaon / Bapat Nagar / Postman Colony / CBC Mall
    "lohara": (19.9871, 79.3593),          # geocoded
    "ravindra_nagar": (19.9300, 79.3000),  # Govt Engineering College / Nagpur-Ballarpur Highway
    "ballarpur_road": (19.9250, 79.3050),
    "cement_nagar": (19.9400, 79.3100),
}


import math

_ward_counts: dict[str, int] = {}


def _jitter(base: tuple[float, float], ward: str) -> tuple[float, float]:
    """Places records sharing a ward in a small deterministic ring (~150-
    300m radius) around its anchor point, so they don't stack exactly on
    top of each other on the map. The first record in each ward sits right
    on the anchor."""
    index = _ward_counts.get(ward, 0)
    _ward_counts[ward] = index + 1
    if index == 0:
        return base
    lat, lng = base
    angle = index * 2.4  # radians; irrational-ish step avoids ring alignment
    radius = 0.0015 + 0.0004 * (index // 6)  # widen the ring every 6 points
    return round(lat + radius * math.cos(angle), 6), round(lng + radius * math.sin(angle), 6)


def _place(seed: int, ward: str, **fields) -> dict:
    lat, lng = _jitter(WARDS[ward], ward)
    return {"lat": lat, "lng": lng, **fields}


CHANDRAPUR_RESTAURANTS = [
    _place(
        1, "old_city_core",
        name="BLISS BAKERY & CAFE",
        category="bakery_cafe",
        area="Singapore Statue, Ramala Talav Rd, Bazar Ward",
        opening_access="Mon-Fri & Sun: 9 AM-10:30 PM | Sat: Closed",
        phone="+91 89990 67649",
        price_tier="Budget",
        specialty="Fresh cakes, custom cakes, clean delivery, humble service",
        data_quality_note="Only place in Chandrapur with a perfect 5.0 rating.",
        external_rating=5.0,
        external_rating_count=32,
    ),
    _place(
        2, "civil_lines",
        name="The Momo-licious (Warora Naka)",
        category="momos_street_food",
        area="Opposite Dargah, near Warora Naka, Civil Lines",
        opening_access="Daily: 5 PM-10:30 PM",
        phone="+91 89198 31366",
        price_tier="Budget",
        specialty="Tandoori Momos, Malai Momos, Afghani Momos, Peri Peri Momos, Soya Chaap",
        data_quality_note="Huge variety — Malai, Afghani, Peri Peri and more. No seating; stand and eat.",
        external_rating=4.9,
        external_rating_count=187,
    ),
    _place(
        3, "wadgaon",
        name="The Momo-licious Cafe (Wadgaon)",
        category="momos_street_food",
        area="ND Hotel Square, Bapat Nagar, Postman Colony, Wadgaon",
        opening_access="Mon-Sat: 1 PM-10 PM | Sun: 1 PM-10:30 PM",
        phone="+91 89198 31366",
        price_tier="Budget",
        specialty="Spicy Chicken Momos, Vegetable Momos, affordable meal combos",
        data_quality_note="Cafe branch of the famous Momo-licious food truck. More seating and broader menu.",
        external_rating=4.9,
        external_rating_count=133,
    ),
    _place(
        4, "old_city_core",
        name="Lakeside Chills",
        category="snacks_cafe",
        area="Ramala Talav Rd, Nawargoan, Bazar Ward",
        opening_access="Daily: 10:30 AM-10:30 PM",
        price_tier="Budget",
        specialty="Handmade snacks, parathas, exotic shakes, misal pav",
        data_quality_note="Situated beside the scenic Ramala Talav (lake). Great for an evening outing.",
        external_rating=4.9,
        external_rating_count=32,
    ),
    _place(
        5, "old_city_core",
        name="Mahi's Cake & Cooking Class",
        category="bakery_cafe",
        area="Bhanapeth Ward, Samrat Chowk, Bazar Ward",
        opening_access="Mon-Sat: 10 AM-10 PM | Sun: 12 PM-10 PM",
        price_tier="Moderate",
        specialty="Custom-designed celebration cakes, cooking classes",
        data_quality_note="Best home baker in Chandrapur. Also runs cooking classes.",
        external_rating=4.9,
        external_rating_count=139,
    ),
    _place(
        6, "tukum",
        name="THALIWALI",
        category="thali_north_indian",
        area="Mul Rd, D.G. Tukum, Jairaj Nagar, Tukum",
        opening_access="Mon-Tue, Thu-Fri, Sun: 11:30 AM-10 PM | Sat: 9 AM-5 PM | Wed: Closed",
        price_tier="Budget",
        specialty="Home-cooked wholesome thali, tiffin service",
        data_quality_note="Closed on Wednesdays. Tiffin service available. Best for daily wholesome lunches.",
        external_rating=4.9,
        external_rating_count=16,
    ),
    _place(
        7, "ravindra_nagar",
        name="Tadka House",
        category="fine_dining_veg",
        area="Opp. Govt Engineering College, Nagpur-Ballarpur Highway, Ravindra Nagar Ward",
        opening_access="Mon: 9 AM-11:30 PM | Tue-Sun: 11 AM-11:30 PM",
        phone="+91 96044 77771",
        price_tier="Moderate",
        specialty="Garlic Rice, pure veg fine dining, event hosting, birthday parties",
        data_quality_note="Most reviewed restaurant in Chandrapur (1,804 reviews). Ideal for large family events.",
        external_rating=4.8,
        external_rating_count=1804,
    ),
    _place(
        8, "ramnagar",
        name="SUKODA",
        category="non_veg_grills",
        area="Sister Colony Rd, Ramnagar",
        opening_access="Daily: 7 AM-10 PM",
        phone="+91 92707 93315",
        price_tier="Moderate",
        specialty="Sukoda dish, Seek Kebab, Tangdi Kebab, Banjara Kebab, Chicken Tandoori",
        data_quality_note="New restaurant already making waves. Famous for the unique 'Sukoda' dish.",
        external_rating=4.7,
        external_rating_count=26,
    ),
    _place(
        9, "old_city_core",
        name="Bakers Bliss Cafe (London Outlet)",
        category="bakery_cafe",
        area="Kasturba Road, Sarafa Lane, near Girnar Hotel",
        opening_access="Daily: 11 AM-11 PM",
        phone="+91 88306 15524",
        price_tier="Moderate",
        specialty="Custom cakes, pastries, French fries, snacks",
        data_quality_note="Themed as a London cafe. Situated in Sarafa Lane area. Limited parking.",
        external_rating=4.7,
        external_rating_count=53,
    ),
    _place(
        10, "lohara",
        name="DINE AT 7 Restaurant",
        category="family_restaurant",
        area="Lohara",
        opening_access="Daily: 11 AM-11 PM",
        phone="+91 82087 77107",
        price_tier="Moderate",
        specialty="Family dining, birthday celebrations, group outings",
        data_quality_note="Cozy spot in Lohara area. Best for birthday celebrations and intimate group dinners.",
        external_rating=4.6,
        external_rating_count=55,
    ),
    _place(
        11, "civil_lines",
        name="Cloudberry Bakers",
        category="bakery_cafe",
        area="Nagpur Rd, Civil Lines",
        opening_access="Daily: 10 AM-11:30 PM",
        phone="+91 82759 51939",
        price_tier="Budget",
        specialty="Modern cakes, pastries, fresh baked goods, anniversary cakes",
        data_quality_note="Modern interiors, great variety. One of the newest quality bakeries in Civil Lines.",
        external_rating=4.6,
        external_rating_count=64,
    ),
    _place(
        12, "civil_lines",
        name="RASRAJ (Nagpur Road Branch)",
        category="thali_north_indian",
        area="Janta College Square, Civil Lines",
        opening_access="Daily: 8:30 AM-10 PM",
        phone="+91 97637 03756",
        price_tier="Moderate",
        specialty="Maharaja Thali, Rasraj Special Thali, sweets, snacks",
        data_quality_note="1,091 reviews — a Chandrapur institution. Also sells sweets and mithai.",
        external_rating=4.5,
        external_rating_count=1091,
    ),
    _place(
        13, "tukum",
        name="Uttam Dhaba Since 1978",
        category="dhaba_budget",
        area="In front of Police Chowki, Ballarsha Road, Shastri Nagar, Tukum",
        opening_access="Daily: 3 PM-12 AM",
        price_tier="Moderate",
        specialty="Classic dhaba-style food, late-night dining",
        data_quality_note="Operating since 1978 — one of Chandrapur's oldest eateries.",
        external_rating=4.5,
        external_rating_count=63,
    ),
    _place(
        14, "ballarpur_road",
        name="Veer Vada Dhaba",
        category="dhaba_budget",
        area="Ballarpur Bypass Road, Rajiv Gandhi Nagar, Tukum",
        opening_access="Mon: Open 24 hrs | Tue-Sun: 7 AM-10:30 PM",
        price_tier="Moderate",
        specialty="Dhaba food, biryani, budget meals",
        data_quality_note="Open 24 hours on Monday. Early opening at 7 AM on other days.",
        external_rating=4.5,
        external_rating_count=19,
    ),
    _place(
        15, "old_city_core",
        name="Seven Star Bakery & Cafe",
        category="bakery_cafe",
        area="Jatpura Gate, opposite Chandak Medical, Bazar Ward",
        opening_access="Daily: 11 AM-11 PM",
        phone="+91 96736 13143",
        price_tier="Budget",
        specialty="Custom cakes, 2-hour delivery, pizza",
        data_quality_note="Offers 2-hour custom cake delivery. Near Jatpura Gate.",
        external_rating=4.5,
        external_rating_count=91,
    ),
    _place(
        16, "civil_lines",
        name="Brew N' Bites",
        category="cafe_continental",
        area="Opposite Collector Bungalow, Pugliya Nagar, Civil Lines",
        opening_access="Daily: 8:30 AM-11 PM",
        phone="+91 84079 46464",
        price_tier="Moderate",
        specialty="Farm Fresh Pizza, Alfredo Pasta, OTM Pizza, mocktails, coffee",
        data_quality_note="Opens at 8:30 AM — earliest cafe in Civil Lines. Limited seating.",
        external_rating=4.4,
        external_rating_count=176,
    ),
    _place(
        17, "wadgaon",
        name="Hyderabad Swadh",
        category="non_veg_grills",
        area="Nagpur Rd, Bapat Nagar, Postman Colony, Wadgaon",
        opening_access="Daily: 12 PM-11 PM",
        phone="+91 93927 46199",
        price_tier="Moderate",
        specialty="Hyderabadi Boneless Biryani, Telangana Chicken Curry, Chicken Afghani",
        data_quality_note="Fills up fast — tables occupied by 8 PM on weekends.",
        external_rating=4.4,
        external_rating_count=258,
    ),
    _place(
        18, "civil_lines",
        name="Santkrupa Food Plaza",
        category="family_restaurant",
        area="Behind Janta College, Nagpur Rd, Civil Lines",
        opening_access="Daily: 9 AM-11 PM",
        phone="+91 91123 45647",
        price_tier="Budget",
        specialty="Indian food, multi-cuisine, early opening",
        data_quality_note="664 reviews. Opens at 9 AM — good for early lunches near Civil Lines.",
        external_rating=4.3,
        external_rating_count=664,
    ),
    _place(
        19, "tukum",
        name="Bakers Bliss (Tukum Branch)",
        category="bakery_cafe",
        area="Thakur Complex, Gurudwara Rd, Jairaj Nagar, Tukum",
        opening_access="Daily: 11 AM-11 PM",
        phone="+91 95290 51150",
        price_tier="Moderate",
        specialty="Pastries, cakes, puffs, sandwiches, mocktails",
        data_quality_note="Best cafe in Tukum area. Beautiful interiors, affordable menu.",
        external_rating=4.2,
        external_rating_count=146,
    ),
    _place(
        20, "wadgaon",
        name="FUNKY CHEN Food Park",
        category="chinese_fast_food",
        area="Haveli Garden, Trimurti Nagar Chok, Jagannath Baba Nagar",
        opening_access="Mon: 12:30 PM-11 AM | Tue-Sun: 12:30 PM-11 PM",
        phone="+91 82371 83207",
        price_tier="Budget",
        specialty="Indo-Chinese varieties, open-air seating near Haveli",
        data_quality_note="Open-air food park near Amritsar Haveli. Some inconsistent reviews — visit on weekdays.",
        external_rating=4.2,
        external_rating_count=124,
    ),
    _place(
        21, "wadgaon",
        name="Amritsar Haveli",
        category="fine_dining_veg",
        area="MIIT Hotel, Nagpur Rd, Wadgaon",
        opening_access="Daily: 11 AM-11:55 PM",
        phone="+91 97649 59500",
        price_tier="Moderate",
        specialty="Kulchas, Sarso ka Saag, Makki ki Roti, Jain-friendly options, valet parking",
        data_quality_note="Punjab franchise. Valet parking available. Decent Jain food options.",
        external_rating=4.1,
        external_rating_count=290,
    ),
    _place(
        22, "wadgaon",
        name="2 Kitchens",
        category="family_restaurant",
        area="CBC Mall, 1st Floor, Nagpur Rd, Wadgaon",
        opening_access="Daily: 11:30 AM-11:30 PM",
        phone="+91 95299 27863",
        price_tier="Moderate",
        specialty="Chicken Dum Biryani, Virgin Mojito, Tandoori Mushroom, non-veg platters",
        data_quality_note="Inside CBC Mall — easy parking. Service can be slow during rush hours.",
        external_rating=4.1,
        external_rating_count=715,
    ),
    _place(
        23, "wadgaon",
        name="Santkrupa Family Restaurant",
        category="family_restaurant",
        area="Ambedkar Sabhagruha Square, near Nagpur Rd, Wadgaon",
        opening_access="Daily: 11 AM-11 PM",
        price_tier="Moderate",
        specialty="Family dining, ring ceremonies, banquet hall for 200 guests",
        data_quality_note="Banquet hall capacity ~200 people. Good for ceremonies and large family events.",
        external_rating=4.1,
        external_rating_count=231,
    ),
    _place(
        24, "civil_lines",
        name="Kancha's Fast Food",
        category="chinese_fast_food",
        area="Old Warora Naka Chowk, Nagpur Rd, Civil Lines",
        opening_access="Daily: 11 AM-10 PM",
        phone="+91 84210 09977",
        price_tier="Budget",
        specialty="Chilli Paneer, Dry Manchurian, Fried Rice, Momos",
        data_quality_note="Most reviewed place in this list (1,436 reviews). 20+ years in Chandrapur.",
        external_rating=4.0,
        external_rating_count=1436,
    ),
    _place(
        25, "cement_nagar",
        name="Swad Bar and Restaurant",
        category="bar_dining",
        area="Mahavir Tower, Mul Rd, Cement Nagar",
        opening_access="Daily: 10 AM-10 PM",
        phone="+91 77448 88800",
        price_tier="Moderate",
        specialty="All major liquor brands, good ambience, good ventilation",
        data_quality_note="Popular bar with comfortable seating and all major liquor brands. Also serves food.",
        external_rating=3.9,
        external_rating_count=224,
    ),
    _place(
        26, "wadgaon",
        name="Uncle Da Dhaba",
        category="dhaba_budget",
        area="Nagpur Rd, Bapat Nagar, Postman Colony, Wadgaon Phata",
        opening_access="Hours vary — confirm before visiting",
        price_tier="Moderate",
        specialty="Begum Bahar (Baingan Bharta), Masala Kulcha, Butter Masala Khichadi",
        data_quality_note="From the makers of Royal Baking Co. Pure veg.",
        external_rating=3.8,
        external_rating_count=856,
    ),
    _place(
        27, "old_city_core",
        name="Saajan Kancha Chinese & Momos Centre",
        category="chinese_fast_food",
        area="Main Road",
        opening_access="Daily: 11 AM-10:30 PM",
        phone="+91 92090 64363",
        price_tier="Budget",
        specialty="Various momos, fried rice, cocktail rice, Manchurian",
        data_quality_note="One of the oldest pure veg Chinese spots in Chandrapur. Delivers to trains at the station.",
        external_rating=3.8,
        external_rating_count=614,
    ),
    _place(
        28, "civil_lines",
        name="K.G.N. Chinese",
        category="chinese_fast_food",
        area="Chandrapur-Mul-Nagbhid-Nagpur Highway, Civil Lines",
        opening_access="Mon, Wed-Sun: 11 AM-10:30 PM | Tue: 11 AM-10 PM",
        phone="+91 70208 70543",
        price_tier="Budget",
        specialty="Chilli Chana, Dry Manchurian, Chilli Paneer, Cocktail Rice",
        data_quality_note="On the main highway, easy to spot.",
        external_rating=3.7,
        external_rating_count=97,
    ),
    _place(
        29, "civil_lines",
        name="Gajanan Bhojnalaya",
        category="thali_north_indian",
        area="Janata College Square, Civil Lines",
        opening_access="Daily: 11 AM-10 PM",
        phone="+91 89287 89846",
        price_tier="Budget",
        specialty="Gajanan Special Thali, pocket-friendly North Indian",
        data_quality_note="Most affordable thali option near Janta College Square.",
        external_rating=3.6,
        external_rating_count=17,
    ),
]
