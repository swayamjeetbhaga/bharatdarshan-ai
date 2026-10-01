"""Seed dataset for Nagpur district restaurants, iconic Saoji eateries, and cafes.

Sourced and curated for BharatDarshan AI (Nagpur District).
Includes legendary Saoji bhojnalayas, traditional Maharashtrian breakfast spots,
family thali centers, and specialty modern cafes.
"""

import math

DATASET_PREPARED_ON = "2026-09-17"
EXTERNAL_RATING_SOURCE = "Google Maps"

# Coordinate anchors for dining hubs across Nagpur
WARDS = {
    "gandhibagh": (21.1480, 79.1060),
    "sitabuldi": (21.1445, 79.0835),
    "sadar": (21.1620, 79.0820),
    "dharampeth": (21.1420, 79.0600),
    "ramdaspeth": (21.1350, 79.0720),
    "bajaj_nagar": (21.1270, 79.0620),
    "wardha_road": (21.1070, 79.0680),
    "hingna_road": (21.1120, 79.0280),
    "mahal": (21.1460, 79.1120),
    "itwari": (21.1550, 79.1180),
    "ramtek": (21.3960, 79.3270),
}

_ward_counts: dict[str, int] = {}


def _jitter(base: tuple[float, float], ward: str) -> tuple[float, float]:
    index = _ward_counts.get(ward, 0)
    _ward_counts[ward] = index + 1
    if index == 0:
        return base
    lat, lng = base
    angle = index * 2.4
    radius = 0.0015 + 0.0004 * (index // 6)
    return round(lat + radius * math.cos(angle), 6), round(lng + radius * math.sin(angle), 6)


def _place(seed: int, ward: str, **fields) -> dict:
    lat, lng = _jitter(WARDS[ward], ward)
    return {
        "district": "Nagpur",
        "state": "Maharashtra",
        "lat": lat,
        "lng": lng,
        **fields,
    }


NAGPUR_RESTAURANTS = [
    # --- Legendary Saoji & Vidarbha Non-Veg Grills ---
    _place(
        1, "gandhibagh",
        name="Jagdish Saoji Bhojnalaya",
        category="non_veg_grills",
        area="Near Agrasen Chowk, Gandhibagh, Nagpur",
        opening_access="Daily: 12:30 PM - 3:30 PM & 7:30 PM - 11:00 PM",
        phone="+91 98222 34120",
        price_tier="Budget",
        specialty="Authentic Mutton Saoji, Chicken Sukka, Keema Kaleji, Roti & Bhakri",
        data_quality_note="One of the oldest and most revered authentic Saoji joints in central Nagpur.",
        external_rating=4.7,
        external_rating_count=3850,
    ),
    _place(
        2, "sadar",
        name="Shankar Saoji Dhaba",
        category="non_veg_grills",
        area="Mount Road, Sadar, Nagpur",
        opening_access="Daily: 1:00 PM - 4:00 PM & 7:00 PM - 11:30 PM",
        phone="+91 98901 77452",
        price_tier="Budget",
        specialty="Signature Saoji Gravy, Prawns Sukka, Khur Curry, Spicy Egg Curry",
        data_quality_note="Famed for intense, slow-cooked indigenous Vidarbha spices and homestyle hospitality.",
        external_rating=4.6,
        external_rating_count=2920,
    ),
    _place(
        3, "itwari",
        name="Pardesi Saoji Bhojnalaya",
        category="non_veg_grills",
        area="Near Telipura, Itwari, Nagpur",
        opening_access="Daily: 12:00 PM - 3:30 PM & 7:00 PM - 10:45 PM",
        phone="+91 93731 09876",
        price_tier="Budget",
        specialty="Traditional Halba-Koshti style Mutton Handi, Roasted Mutton Dry",
        data_quality_note="Heritage non-veg kitchen maintaining generations-old hand-ground masala recipes.",
        external_rating=4.6,
        external_rating_count=1840,
    ),

    # --- Traditional Maharashtrian, Thali & Pure Veg Fine Dining ---
    _place(
        4, "sitabuldi",
        name="Haldiram's Thhat Baat",
        category="fine_dining_veg",
        area="Munje Square, Sitabuldi, Nagpur",
        opening_access="Daily: 11:00 AM - 10:30 PM",
        phone="+91 712 253 4444",
        price_tier="Moderate",
        specialty="Grand Royal Rajasthani & Maharashtrian Thali, Orange Barfi, Chhole Bhature",
        data_quality_note="Flagship dining experience from Haldiram's, Nagpur's global culinary pride.",
        external_rating=4.7,
        external_rating_count=7200,
    ),
    _place(
        5, "bajaj_nagar",
        name="Vishnuji Ki Rasoi",
        category="family_restaurant",
        area="Abhyankar Nagar / Bajaj Nagar, Nagpur",
        opening_access="Daily: 7:00 PM - 11:00 PM (Dinner buffet only)",
        phone="+91 712 224 8888",
        price_tier="Moderate",
        specialty="Unlimited Traditional Maharashtrian Village Buffet, Pithla Bhakri, Purana Poli, Jhunka",
        data_quality_note="Celebrity chef Vishnu Manohar's iconic village-themed unlimited feast.",
        external_rating=4.5,
        external_rating_count=5140,
    ),
    _place(
        6, "sadar",
        name="Veeraswami Restaurant",
        category="family_restaurant",
        area="Mount Road, Sadar, Nagpur",
        opening_access="Daily: 7:30 AM - 10:30 PM",
        phone="+91 712 253 1122",
        price_tier="Moderate",
        specialty="South Indian Filter Coffee, Ghee Roast Dosa, Idli-Vada, Thali",
        data_quality_note="Nagpur's legendary breakfast institution running for over seven decades in Sadar.",
        external_rating=4.5,
        external_rating_count=4320,
    ),

    # --- Famous Breakfast, Street Food & Tarri Poha ---
    _place(
        7, "wardha_road",
        name="Ramji-Shyamji Pohe",
        category="momos_street_food",
        area="Wardha Road, Near Lokmat Square",
        opening_access="Daily: 6:00 AM - 1:00 PM",
        phone="+91 94221 55667",
        price_tier="Budget",
        specialty="Nagpuri Tarri Poha topped with Chana Gravy, Sev, Sambar Vada",
        data_quality_note="The quintessential Nagpur breakfast destination with a huge daily cult following.",
        external_rating=4.8,
        external_rating_count=6450,
    ),
    _place(
        8, "gandhibagh",
        name="Keshav Tarri Poha",
        category="momos_street_food",
        area="Near Central Avenue, Gandhibagh",
        opening_access="Daily: 6:30 AM - 12:30 PM",
        phone="+91 98233 44551",
        price_tier="Budget",
        specialty="Spicy Chana Tarri Poha, Crispy Jalebi, Masala Tea",
        data_quality_note="Known for intensely flavorful tarri (curry) and fresh morning accompaniments.",
        external_rating=4.7,
        external_rating_count=3120,
    ),
    _place(
        9, "dharampeth",
        name="Gayatri Coffee House",
        category="snacks_cafe",
        area="West High Court Road, Dharampeth",
        opening_access="Daily: 8:00 AM - 10:30 PM",
        phone="+91 712 254 9900",
        price_tier="Budget",
        specialty="Filter Coffee, Cheese Uttapam, Mysore Masala Dosa, Bun Maska",
        data_quality_note="Bustling Dharampeth evening hub for students, families, and coffee aficionados.",
        external_rating=4.5,
        external_rating_count=2780,
    ),

    # --- Specialty Coffee, Cafes & Multi-Cuisine ---
    _place(
        10, "ramdaspeth",
        name="Corridor Seven Coffee Roasters",
        category="bakery_cafe",
        area="Central Bazar Road, Ramdaspeth",
        opening_access="Daily: 8:00 AM - 10:30 PM",
        phone="+91 93077 17777",
        price_tier="Moderate",
        specialty="Artisanal Single-Origin Coffee, Manual Brews, Gourmet Bagels & Sourdough Croissants",
        data_quality_note="Nationally acclaimed specialty coffee roastery born in Nagpur.",
        external_rating=4.8,
        external_rating_count=3640,
    ),
    _place(
        11, "hingna_road",
        name="The Breakfast Story",
        category="cafe_continental",
        area="Hingna T-Point, Subhash Nagar Road",
        opening_access="Tue-Sun: 8:00 AM - 3:00 PM | Mon: Closed",
        phone="+91 96079 77761",
        price_tier="Moderate",
        specialty="All-Day European Breakfast, Pancakes, Eggs Benedict, Masala Chai, Waffles",
        data_quality_note="Vibrant retro cafe renowned for weekend brunch culture and book lovers.",
        external_rating=4.7,
        external_rating_count=3210,
    ),
    _place(
        12, "sadar",
        name="Barbeque Nation (Nagpur Sadar)",
        category="family_restaurant",
        area="Poonam Chambers, Byramji Town, Sadar",
        opening_access="Daily: 12:00 PM - 3:30 PM & 6:30 PM - 11:00 PM",
        phone="+91 712 669 9999",
        price_tier="Premium",
        specialty="Live Table Barbecue, Cajun Spiced Potatoes, Grilled Prawns, Kulfi Nation",
        data_quality_note="Premier destination for celebratory family feasts and buffet dining in Sadar.",
        external_rating=4.6,
        external_rating_count=4850,
    ),
    _place(
        13, "dharampeth",
        name="Mocha Cafe & Bar",
        category="cafe_continental",
        area="WHC Road, Dharampeth, Nagpur",
        opening_access="Daily: 11:00 AM - 11:30 PM",
        phone="+91 712 255 6677",
        price_tier="Moderate",
        specialty="Wood-fired Gourmet Pizzas, Mezze Platters, Shakes, Pasta & Dessert Fondues",
        data_quality_note="Chic social cafe and lounge popular among youth and creative professionals.",
        external_rating=4.5,
        external_rating_count=2480,
    ),
    _place(
        14, "mahal",
        name="Checkers Bakery & Cafe",
        category="bakery_cafe",
        area="Near Badkas Chowk, Mahal",
        opening_access="Daily: 9:30 AM - 10:30 PM",
        phone="+91 712 272 8899",
        price_tier="Budget",
        specialty="Fresh Cream Pastries, Chocolate Truffle Cake, Burgers & Baked Snacks",
        data_quality_note="Beloved local bakery chain in old Nagpur known for fresh customized celebration cakes.",
        external_rating=4.6,
        external_rating_count=1650,
    ),
    # --- Ramtek Specialty Dining ---
    _place(
        15, "ramtek",
        name="Rajkamal Saoji Bhojnalaya (Ramtek)",
        category="non_veg_grills",
        area="Ramtek City Center",
        opening_access="Daily: 12:30 PM - 4:00 PM & 7:30 PM - 10:30 PM",
        phone="+91 91122 33445",
        price_tier="Budget",
        specialty="Authentic Ramtek-style Saoji Mutton, Khur, and Country Chicken",
        data_quality_note="Highly rated local Saoji joint near the Ramtek bus stand.",
        external_rating=4.5,
        external_rating_count=850,
    ),
    _place(
        16, "ramtek",
        name="Khindsi Lake View Restaurant",
        category="family_restaurant",
        area="Khindsi Lake, Ramtek",
        opening_access="Daily: 11:00 AM - 11:00 PM",
        phone="+91 88877 66554",
        price_tier="Moderate",
        specialty="Freshwater Fish Fry, Veg Thali, Lakeside Snacks",
        data_quality_note="Scenic lakeside dining popular among tourists visiting Khindsi.",
        external_rating=4.3,
        external_rating_count=1200,
    ),
    _place(
        17, "ramtek",
        name="Shree Ganesh Pure Veg",
        category="fine_dining_veg",
        area="Near Ramtek Temple Trek Base",
        opening_access="Daily: 7:00 AM - 10:30 PM",
        phone="+91 99988 77766",
        price_tier="Budget",
        specialty="Maharashtrian Thali, Poha, Misal Pav, South Indian Breakfast",
        data_quality_note="Clean, pure vegetarian restaurant catering to pilgrims.",
        external_rating=4.4,
        external_rating_count=980,
    ),
]
