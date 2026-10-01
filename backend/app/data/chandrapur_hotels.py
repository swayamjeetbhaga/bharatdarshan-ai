"""Seed dataset for Chandrapur district hotels, resorts and Tadoba safari
lodges.

Sourced from a "Chandrapur District Hotels & Accommodation Directory"
document (prepared 03 September 2026) whose facts — address, zone,
reception hours, phone, amenities, "best for", notable remarks, and
rating/review counts — are attributed there to Google Maps.

Coordinates are NOT part of that source. City-hotel zones (Civil Lines,
Wadgaon, Tukum, Bazar Ward, Lohara) reuse the same ward anchors as the
Chandrapur restaurant seed for consistency. New city zones (Babupeth,
Rashtrawadi Nagar, Padoli) and the Tadoba-area buffer zones — a genuinely
different, more spread-out region than the city (Moharli, Kolara/Chimur,
Bhadravati taluka villages) — were geocoded fresh against OpenStreetMap/
Nominatim, bounded to the wider Chandrapur district to avoid drift to a
same-named place elsewhere. One zone (Thanegaon) didn't resolve and falls
back to the Moharli gate anchor, since the source description places it
right by that gate. Every record here has `coordinates_verified=False`
pending manual verification, same as the other Chandrapur seeds.

Ratings/review counts are stored as `external_rating`/`external_rating_count`
(a Google Maps snapshot), kept separate from `avg_rating`/`review_count`
(always this app's own `reviews` aggregate) for the same reason as the
restaurant seed: an in-app review must never silently overwrite an
imported number.
"""

import math

DATASET_PREPARED_ON = "2026-09-03"
EXTERNAL_RATING_SOURCE = "Google Maps"

# Ward/zone anchors. The first six reuse the exact points from
# chandrapur_restaurants.py's WARDS for consistency; the rest are new,
# either fresh Nominatim lookups (see module docstring) or, for
# thanegaon_moharli, a same-gate fallback.
WARDS = {
    "old_city_core": (19.9480, 79.2950),
    "civil_lines": (19.9550, 79.3050),
    "tukum": (19.9718, 79.3007),
    "wadgaon": (19.9900, 79.3200),
    "lohara": (19.9871, 79.3593),
    "padoli": (19.9994, 79.2485),           # geocoded
    "babupeth": (19.9245, 79.3157),         # geocoded
    "rashtrawadi_nagar": (20.0225, 79.2812),  # geocoded (CSTPS Hospital)
    "padmapur_kitali": (20.0525, 79.2976),  # geocoded
    "borda_village": (20.0155, 79.4326),    # geocoded
    "erai_dam": (20.1188, 79.2660),         # geocoded
    "pangadi_shirkheda": (20.2794, 79.5723),  # geocoded (Wasera)
    "wadala_tukum_bhadravati": (20.3032, 79.2526),  # geocoded
    "manemohadi_chimur": (20.4139, 79.4133),  # geocoded
    "kolara_gate": (20.4070, 79.3675),      # geocoded
    "madanapur_chimur": (20.3915, 79.4097),  # geocoded
    "kondegaon_mal": (20.2410, 79.3026),    # geocoded
    "moharli_gate": (20.1886, 79.3338),     # geocoded
    "mudholi_bhadravati": (20.2555, 79.2930),  # geocoded
    "thanegaon_moharli": (20.1916, 79.3368),  # fallback: near moharli_gate, offset to avoid an exact overlap
}

_ward_counts: dict[str, int] = {}


def _jitter(base: tuple[float, float], ward: str) -> tuple[float, float]:
    """Small deterministic spread so records sharing a ward don't stack
    exactly on top of each other on the map (see chandrapur_restaurants.py,
    same scheme)."""
    index = _ward_counts.get(ward, 0)
    _ward_counts[ward] = index + 1
    if index == 0:
        return base
    lat, lng = base
    angle = index * 2.4
    radius = 0.0015 + 0.0004 * (index // 6)
    return round(lat + radius * math.cos(angle), 6), round(lng + radius * math.sin(angle), 6)


def _place(seed: int, ward: str, amenities: str, **fields) -> dict:
    lat, lng = _jitter(WARDS[ward], ward)
    return {
        "lat": lat,
        "lng": lng,
        "amenities": [a.strip() for a in amenities.split("•") if a.strip()],
        **fields,
    }


CHANDRAPUR_HOTELS = [
    # --- City Hotels (Chandrapur City) ---
    _place(
        1, "civil_lines",
        name="The Grand Icon",
        category="city_hotel",
        area="Civil Lines, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 92711 51721",
        specialty="Business travellers, city stays, events & banquets",
        amenities="AC Rooms • Banquet Hall • Restaurant • Parking • City Centre Location",
        data_quality_note="Newest premium property in Chandrapur city. Ample parking — rare in Civil Lines.",
        external_rating=4.9,
        external_rating_count=221,
    ),
    _place(
        2, "wadgaon",
        name="URBAN STAY 24x7",
        category="city_hotel",
        area="Wadgaon, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 92704 22248",
        specialty="Budget travellers, short business stays, solo travellers",
        amenities="AC Rooms • 24-Hr Reception • Mall Location • Affordable Rates • Room Service",
        data_quality_note="Perfect 5.0 rating. Located inside CBC Mall — extremely convenient.",
        external_rating=5.0,
        external_rating_count=50,
    ),
    _place(
        3, "rashtrawadi_nagar",
        name="Enrise by Sayaji, Chandrapur",
        category="city_hotel",
        area="Rashtrawadi Nagar, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 91725 69777",
        specialty="Corporate stays, family events, birthday celebrations",
        amenities="AC Rooms • Multi-Cuisine Restaurant • Banquet • Event Space • Housekeeping • Room Service • Parking",
        data_quality_note="Part of the Sayaji Group — reliable branded chain.",
        external_rating=4.6,
        external_rating_count=291,
    ),
    _place(
        4, "tukum",
        name="Hotel Dwarika",
        category="city_hotel",
        area="Tukum, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 92093 03336",
        specialty="General travellers, Tukum area convenience",
        amenities="AC Rooms • Clean Rooms • Helpful Staff • Parking • Restaurant",
        data_quality_note="Located in Tukum — convenient for bus stand and city centre.",
        external_rating=4.6,
        external_rating_count=125,
    ),
    _place(
        5, "babupeth",
        name="Hotel Elite",
        category="city_hotel",
        area="Babupeth, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 93251 66830",
        specialty="Travellers on the Nagpur-Chandrapur highway, nature lovers",
        amenities="AC Rooms • Nature Views • Spacious Rooms • Well-Trained Staff • Comfortable Beds",
        data_quality_note="On the main highway in Babupeth area, praised for tasteful room design.",
        external_rating=4.6,
        external_rating_count=94,
    ),
    _place(
        6, "wadgaon",
        name="Western Hotel",
        category="city_hotel",
        area="Wadgaon, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 76662 67449",
        specialty="Business travellers, transit stays, short leisure trips",
        amenities="AC Rooms • Good Location • Cooperative Staff • Sanitized Washrooms • Nearby Mall",
        data_quality_note="Beside MDR Mall on Nagpur Road. Limited parking — plan ahead.",
        external_rating=4.5,
        external_rating_count=218,
    ),
    _place(
        7, "civil_lines",
        name="Hotel Lohara Inn",
        category="city_hotel",
        area="Civil Lines, Chandrapur",
        opening_access="Reception: 24 x 7",
        specialty="Premium city stays, leisure travel, business",
        amenities="Luxury Rooms • Restaurant • Housekeeping • Modern Interiors • Courteous Staff",
        data_quality_note="Praised for luxurious, well-maintained rooms and exceptional staff.",
        external_rating=4.5,
        external_rating_count=116,
    ),
    _place(
        8, "old_city_core",
        name="Hotel LOTUS",
        category="city_hotel",
        area="Bazar Ward, Chandrapur",
        opening_access="Reception: Open 24 Hours",
        phone="+91 86050 00326",
        specialty="Tadoba safari base (40 min to gates), business, budget-conscious travellers",
        amenities="AC Rooms • Shidori Restaurant (Pure Veg) • Complimentary Buffet Breakfast • Jain Food on Request • 24-Hr Front Desk",
        data_quality_note="1,060 reviews — most reviewed city hotel in Chandrapur. 40 min drive to Tadoba gates.",
        external_rating=4.1,
        external_rating_count=1060,
    ),
    _place(
        9, "tukum",
        name="Hotel Siddharth Premiere",
        category="city_hotel",
        area="Tukum, Chandrapur",
        opening_access="Reception: Daily 12 AM - 11:30 PM",
        phone="+91 84128 00000",
        specialty="Leisure stays, couple trips, dining + cocktail experience",
        amenities="AC Rooms • Multi-Cuisine Restaurant • Bar / Cocktails • Valet Parking • Complimentary Breakfast • Room Dining",
        data_quality_note="Known for a skilled mixologist making excellent cocktails. Near bus stand.",
        external_rating=4.2,
        external_rating_count=489,
    ),
    _place(
        10, "wadgaon",
        name="The ND Hotel",
        category="city_hotel",
        area="Wadgaon, Chandrapur",
        opening_access="Reception: Open 24 Hours",
        phone="+91 77449 77770",
        specialty="Business stays, long-term corporate accommodation",
        amenities="AC Rooms • Multi-Cuisine Restaurant • Laundry • 24-Hr Front Desk • Mall Adjacent • Parking",
        data_quality_note="Most reviewed hotel in Chandrapur (5,052 reviews). Beside CBC Mall, opposite Haldiram's.",
        external_rating=4.1,
        external_rating_count=5052,
    ),
    _place(
        11, "old_city_core",
        name="HOTEL VYANKATESH",
        category="city_hotel",
        area="Jatpura, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 78229 87886",
        specialty="Budget stays, solo business travel, short transit stays",
        amenities="AC Rooms • Clean Rooms • Good Lighting • Functional Workspace • Helpful Staff",
        data_quality_note="Budget option near Jatpura Gate area. No car parking — be aware.",
        external_rating=4.1,
        external_rating_count=100,
    ),
    _place(
        12, "tukum",
        name="Hotel Rajwada Palace",
        category="city_hotel",
        area="Tukum / Urjanagar, Chandrapur",
        opening_access="Reception: Open 24 Hours",
        phone="+91 99210 19664",
        specialty="Weddings, naming ceremonies, engagement parties, kitty parties, corporate events",
        amenities="Rooms • Grand Banquet Hall • Event Decoration • Catering • Parking • Family Events",
        data_quality_note="Primary reputation is as a premium banquet/event venue.",
        external_rating=4.2,
        external_rating_count=460,
    ),
    _place(
        13, "padoli",
        name="Treebo Royal, Chandrapur",
        category="city_hotel",
        area="Padoli / Nagpur Highway",
        opening_access="Reception: 24 x 7",
        phone="+91 93228 00100",
        specialty="Budget stays, Tadoba safari base on highway",
        amenities="AC Rooms • Breakfast • Safari Vehicle Booking • Parking • Nagpur Highway Location",
        data_quality_note="On Nagpur-Chandrapur highway. Affordable pricing (~Rs 2,000/night).",
        external_rating=3.9,
        external_rating_count=151,
    ),
    _place(
        14, "tukum",
        name="Hotel Palace",
        category="city_hotel",
        area="Tukum, Chandrapur",
        opening_access="Reception: 24 x 7",
        phone="+91 88885 50444",
        specialty="Budget travellers using bus/rail transport",
        amenities="AC Rooms • Vegetarian Restaurant • Banquet • Near Bus Stand",
        data_quality_note="Mixed reviews. Best for short 1-2 night stays only.",
        external_rating=3.7,
        external_rating_count=336,
    ),
    # --- Resorts & Farm Stays (Chandrapur District) ---
    _place(
        15, "padmapur_kitali",
        name="Bhimranjana Villa",
        category="resort_farm_stay",
        area="Padmapur, Kitali (Tadoba-adjacent)",
        opening_access="Reception: 24 x 7",
        phone="+91 96656 11642",
        specialty="Family trips to Tadoba, couples, friends group getaways",
        amenities="Private Villa • Clean Rooms • Pest-Free • Kids-Friendly • Tadoba Safari Access • Warm Hosts",
        data_quality_note="Perfect 5.0 rating. Completely pest-free, home-like hospitality.",
        external_rating=5.0,
        external_rating_count=51,
    ),
    _place(
        16, "borda_village",
        name="Chillarwar Farm's & Resort",
        category="resort_farm_stay",
        area="Mul Road, near Borda Village",
        opening_access="Reception: 24 x 7",
        phone="+91 78218 52500",
        specialty="Weddings, corporate outings, family gatherings, Tadoba base",
        amenities="Multiple Lawns • Swimming Pool • Accommodation Rooms • Dormitory • Event Spaces • Catering • Safari Proximity",
        data_quality_note="918 reviews — one of the most reviewed properties in the district. Wi-Fi weak in this area.",
        external_rating=4.7,
        external_rating_count=918,
    ),
    _place(
        17, "erai_dam",
        name="MAHARANA RESORT",
        category="resort_farm_stay",
        area="Erai Dam, Sawari, Vadholi",
        opening_access="Reception: 24 x 7",
        phone="+91 98222 02971",
        specialty="Family picnics, corporate trips, one-day outings, relaxation",
        amenities="Swimming Pool • Sports Facilities • Forest Setting • Child-Friendly • Restaurant • Party Venue",
        data_quality_note="Situated near Erai Dam in the middle of forest — away from city noise.",
        external_rating=4.6,
        external_rating_count=417,
    ),
    _place(
        18, "lohara",
        name="S.S. Kingdom & Holiday Resort (WaterPark)",
        category="resort_farm_stay",
        area="Lohara, Mul Road, Chandrapur",
        opening_access="Reception: Daily 11 AM - 10:30 PM",
        phone="+91 96577 01656",
        specialty="Day outings, water park fun, family stays",
        amenities="Hotel Rooms • Restaurant • Small Water Park • Changing Rooms • Lockers",
        data_quality_note="Only resort in Chandrapur city limits with a water park. New construction — some snags.",
        external_rating=4.0,
        external_rating_count=746,
    ),
    # --- Tadoba National Park Resorts ---
    _place(
        19, "pangadi_shirkheda",
        name="Wildcat Resort",
        category="tadoba_safari_resort",
        area="Pangadi Shirkheda, Tadoba (Eastern Buffer)",
        opening_access="Reception: Open 24 Hours",
        phone="+91 98865 45725",
        specialty="Families, international tourists, premium Tadoba experience",
        amenities="Safari Cottages • Swimming Pool • All Meals Included • Airport Transfers • Safari Booking • Naturalist Guide • Cold Towel Welcome",
        data_quality_note="Run by the resort owners personally. Access to Pangdi, Somnath, Keslaghat buffer safaris.",
        external_rating=4.8,
        external_rating_count=713,
    ),
    _place(
        20, "wadala_tukum_bhadravati",
        name="Waghoba Eco Lodge",
        category="tadoba_safari_resort",
        area="Wadala Tukum, Bhadravati Taluk (Tadoba Buffer)",
        opening_access="Reception: 24 x 7",
        phone="+91 11 4014 6400",
        specialty="Eco-conscious travellers, wildlife enthusiasts, international tourists",
        amenities="Eco Cottages (Local Materials) • Solar Power • In-House Garden • Filtered Water • Naturalist-Led Safaris • All Meals • Expert Guides",
        data_quality_note="Part of Pugdundee Safaris network. Solar-powered, locally sourced materials.",
        external_rating=4.8,
        external_rating_count=253,
    ),
    _place(
        21, "manemohadi_chimur",
        name="Trees N Tigers Tadoba National Park",
        category="tadoba_safari_resort",
        area="Manemohadi, Chimur (Kolara Zone)",
        opening_access="Reception: 24 x 7",
        phone="+91 92721 04009",
        specialty="Luxury seekers, couples, international wildlife tourists",
        amenities="Luxury Safari Tents • Personal Pool per Tent • AC • Bar • All Meals • Expert Naturalist • Multi-Gate Access",
        data_quality_note="Each tent has a private pool and AC. Quick 30-min drive to several gate zones.",
        external_rating=4.8,
        external_rating_count=76,
    ),
    _place(
        22, "kolara_gate",
        name="WelcomHeritage Tadoba Vanya Villas Resort & Spa",
        category="tadoba_safari_resort",
        area="Kolara Buffer Zone, Chimur Taluk",
        opening_access="Reception/Office: 9 AM - 8 PM",
        phone="+91 92252 22136",
        specialty="Premium family holidays, couples, spa seekers",
        amenities="Pool • Spa • Wildlife Activities • Kids Activities • All Meals • Safari Arrangement • Bar • Nature Walks",
        data_quality_note="1,279 reviews — most reviewed Tadoba resort. Part of WelcomHeritage chain, right in the wildlife corridor.",
        external_rating=4.7,
        external_rating_count=1279,
    ),
    _place(
        23, "madanapur_chimur",
        name="Gondwana Jungle Resort",
        category="tadoba_safari_resort",
        area="Madanapur, Chimur (Near Kolara Gate)",
        opening_access="Reception: 24 x 7",
        phone="+91 99211 50541",
        specialty="Families, value-for-money Tadoba experience, Kolara gate safaris",
        amenities="Clean Rooms • Swimming Pool (Kids-Friendly) • Restaurant • Souvenir Shop • Safari Organization • Kettle/Tea-Coffee in Rooms",
        data_quality_note="Right next to Madnapur Gate; also 30 min to other gates.",
        external_rating=4.7,
        external_rating_count=235,
    ),
    _place(
        24, "kondegaon_mal",
        name="Tadoba Safari Stay — Nature's Sprout",
        category="tadoba_safari_resort",
        area="Kondegaon Mal, Tadoba",
        opening_access="Reception: Open 24 Hours",
        phone="+91 77198 06444",
        specialty="Families, friends groups, value stays near Tadoba",
        amenities="Rooms • Pool Table • Carrom Board • Restaurant • Packed Safari Breakfast • Nature Surroundings • Family-Friendly",
        data_quality_note="896 reviews. Very close to Tadoba gate — easy for early morning safaris.",
        external_rating=4.6,
        external_rating_count=896,
    ),
    _place(
        25, "moharli_gate",
        name="Irai Safari Retreat",
        category="tadoba_safari_resort",
        area="Bhamdeli Road, Near Moharli Gate",
        opening_access="Reception: 24 x 7",
        phone="+91 87999 16166",
        specialty="International wildlife tourists, photography enthusiasts, premium family stays",
        amenities="Spacious Rooms • Machan View Point • Restaurant • Safari Arrangement • Naturalist Deepak • Boating Access • Irai Dam View",
        data_quality_note="1,009 reviews. 10-15 min from both Moharli core and buffer gates. Close to Irai Dam.",
        external_rating=4.6,
        external_rating_count=1009,
    ),
    _place(
        26, "moharli_gate",
        name="Tadoba Jungle Camp",
        category="tadoba_safari_resort",
        area="Moharli Gate, Tadoba Andhari Tiger Reserve",
        opening_access="Reception: Open 24 Hours",
        phone="+91 99990 81177",
        specialty="Couples, bird watchers, intimate jungle experience",
        amenities="Spacious Rooms • Swimming Pool • All Meals • Packed Safari Breakfast • Bird Watching • Personal Experience (Limited Rooms)",
        data_quality_note="Limited number of rooms — more personalized service. Literally inside the jungle.",
        external_rating=4.6,
        external_rating_count=386,
    ),
    _place(
        27, "mudholi_bhadravati",
        name="Limban Resort",
        category="tadoba_safari_resort",
        area="Mudholi, Bhadravati (Tadoba Buffer)",
        opening_access="Reception: Daily 8 AM - 8 PM",
        phone="+91 90226 80451",
        specialty="Honeymooners, eco-conscious couples, photography enthusiasts",
        amenities="Canvas Tents • Pre-Cooled Rooms • Restaurant • Safari Booking • Sustainability Focus • Expert Staff",
        data_quality_note="Pre-cooled rooms before guest arrival. Sustainability-focused without compromising comfort.",
        external_rating=4.6,
        external_rating_count=203,
    ),
    _place(
        28, "moharli_gate",
        name="Camp Serai Tiger Tadoba",
        category="tadoba_safari_resort",
        area="Moharli, Sitaram Peth",
        opening_access="Reception: Open 24 Hours",
        phone="+91 98104 80259",
        specialty="Wildlife enthusiasts, nature lovers, jungle atmosphere seekers",
        amenities="AC Tents • Machan • Barbeque • Restaurant • Safari Pickup/Drop • Nature Walks • Wildlife Conservation Focus",
        data_quality_note="Rustic charm blends with surroundings. Owner is a wildlife enthusiast and conservationist.",
        external_rating=4.6,
        external_rating_count=593,
    ),
    _place(
        29, "kolara_gate",
        name="Tadoba Aranya Villa Resort",
        category="tadoba_safari_resort",
        area="Kolara, Chimur Taluk",
        opening_access="Reception: 24 x 7",
        phone="+91 83299 25018",
        specialty="Kolara gate safari visitors, families, couples",
        amenities="Rooms • Swimming Pool • Restaurant • Welcome Drinks • Rose Water Towels • Safari Basket (Water & Juice) • 2 Min to Gate",
        data_quality_note="2 minutes from Kolara gate — one of the closest resorts.",
        external_rating=4.7,
        external_rating_count=101,
    ),
    _place(
        30, "thanegaon_moharli",
        name="Avadale Tadoba",
        category="tadoba_safari_resort",
        area="Thanegaon, near Moharli Gate",
        opening_access="Reception: 24 x 7",
        phone="+91 80 6951 0265",
        specialty="Budget-conscious Tadoba tourists, international visitors, food-sensitive guests",
        amenities="Rooms • Restaurant • Safari Arrangement • Close to Moharli Gate • Kayaking Nearby • Irai Dam Nearby • Allergen-Aware Kitchen",
        data_quality_note="Walking distance to Moharli gate. Kitchen accommodates severe food allergies. Basic, budget-friendly.",
        external_rating=4.5,
        external_rating_count=440,
    ),
]
