"""Comprehensive seeder for Nagpur District:
- Seeds Nagpur Hotels & Resorts
- Seeds Nagpur Restaurants, Saoji Eateries & Cafes
- Seeds Authentic Community Reviews for Key Nagpur Tourist Attractions
- Recomputes average ratings and review counts across all seeded places
"""

import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.attraction import Attraction, Review
from app.models.user import User
from app.core.security import hash_password
from app.services.attractions import _recompute_rating
from app.data.nagpur_hotels import NAGPUR_HOTELS
from app.data.nagpur_restaurants import NAGPUR_RESTAURANTS

# Realistic traveler reviews for key Nagpur tourist attractions
ATTRACTION_REVIEWS = {
    "Deekshabhoomi": [
        ("aarav_safari", 5, "A deeply inspiring and serene monument. The architectural grandeur of the stupa and peaceful atmosphere make it unforgettable."),
        ("neha_wildlife", 5, "Magnificent Buddhist stupa, very clean and well-maintained grounds. Visiting during early morning brings profound peace."),
        ("rohit_nature", 5, "Historical powerhouse of social equality. The museum inside offers great insights into Dr. B. R. Ambedkar's life work."),
        ("priya_explorer", 4, "Extremely peaceful place in the middle of Nagpur city. Visit on weekdays to avoid major holiday crowds."),
        ("vikram_tiger", 5, "One of the most impressive Buddhist architecture monuments in Asia. Beautiful gardens and calm surroundings."),
        ("ananya_bio", 5, "Very spacious and spiritually uplifting. Ample parking and close to Ramdaspeth and metro stations."),
        ("rajesh_tours", 5, "A must-visit national heritage landmark. The stupa is magnificent from inside and outside."),
        ("sneha_clicks", 5, "Great place for contemplation and history enthusiasts. Clean premises and humble staff."),
        ("amit_wander", 4, "Beautiful stupa and library. Footwear management is well organized at the entrance."),
        ("kavita_morning", 5, "The evening lighting on the stupa is breathtaking. Truly the heart and soul of Nagpur's cultural heritage."),
        ("sanjay_guide", 5, "Essential stop for anyone visiting Nagpur. Highly accessible via Nagpur Metro Congress Nagar station."),
        ("pooja_family", 5, "Great peaceful visit with family. Kids and elders all appreciated the serene ambiance."),
    ],
    "Ramtek Fort Temple": [
        ("aarav_safari", 5, "Perched high on the hill with panoramic views of the entire valley. The ancient stone carvings and temples are marvelous."),
        ("rohit_nature", 5, "Steeped in epic history and Kalidasa's poetry. Walking up the ramparts feels like traveling back in time."),
        ("priya_explorer", 4, "Breathtaking views of the forest and Ramtek town. Watch out for monkeys on the steps, keep food inside bags."),
        ("vikram_tiger", 5, "Historic 600-year-old fort temple with great spiritual energy. Early morning breeze from the hill is refreshing."),
        ("ananya_bio", 5, "A wonderful blend of Maratha/Gond architecture and serene temple shrines. Must visit Kalidasa Smarak nearby."),
        ("rajesh_tours", 5, "Excellent day trip from Nagpur. Road from Nagpur is smooth and scenic via NH44 and Mansar."),
        ("sneha_clicks", 5, "Photographer's paradise during golden hour. Ancient stone walls overlooking green fields."),
        ("amit_wander", 4, "Peaceful temple with great historical legacy. Steps are manageable; road also goes close to the upper gate."),
        ("kavita_morning", 5, "Serene atmosphere and historical sanctity. The view of Khindsi Lake in the distance is mesmerizing."),
        ("sanjay_guide", 5, "Rich history linked to Lord Rama's exile. Very well respected by pilgrims and travelers across Vidarbha."),
    ],
    "Khindsi Lake": [
        ("neha_wildlife", 5, "Fantastic water sports and speedboat rides! The lake is surrounded by thick green forests."),
        ("rohit_nature", 5, "One of the best weekend getaway spots in Vidarbha. Boating and lakeside dining make it a complete family day out."),
        ("priya_explorer", 4, "Scenic water reservoir with good pedal and motor boats. Afternoon gets sunny, so morning or sunset is ideal."),
        ("vikram_tiger", 5, "Great spot for adventure seekers. Jet ski, banana rides, and speedboats are well operated with safety life jackets."),
        ("ananya_bio", 5, "Peaceful natural lake with scenic hills on the horizon. MTDC resort right next to the water is great for lunch."),
        ("rajesh_tours", 4, "Very enjoyable boating experience. Combine this with Ramtek Fort Temple for a full one-day itinerary."),
        ("sneha_clicks", 5, "Stunning reflection of sunset on the water. Great bird photography during winter months."),
        ("amit_wander", 5, "Clean water and lush forest backdrop. Plenty of snack stalls and family recreation areas."),
        ("sanjay_guide", 4, "Popular picnic hub just 5 km from Ramtek city. Well connected by road from Nagpur."),
        ("pooja_family", 5, "Kids loved the water scooter and paddle boats! Very relaxing atmosphere."),
    ],
    "Dragon Palace Buddhist Temple": [
        ("aarav_safari", 5, "Known as the Lotus Temple of Nagpur. The Japanese-style architecture and pristine white structure are stunning."),
        ("neha_wildlife", 5, "The sandalwood Buddha statue inside the meditation hall radiates tranquility. Very peaceful manicured gardens."),
        ("rohit_nature", 5, "Spiritual bliss in Kamptee. Everything is spotlessly clean, calm, and gracefully maintained."),
        ("priya_explorer", 4, "A tranquil retreat just 18 km from Nagpur city. Easy to reach via auto or cab from Kamptee."),
        ("vikram_tiger", 5, "Beautiful landscape and magnificent golden Buddha icon. A hidden architectural gem in Maharashtra."),
        ("ananya_bio", 5, "The peaceful silence inside the meditation hall is unmatched. Wonderful place to relax the mind."),
        ("rajesh_tours", 5, "Immaculately maintained grounds with colorful flowerbeds. Welcoming to people of all faiths."),
        ("sneha_clicks", 5, "Fabulous photography spot. The symmetric white dome against clear blue skies looks sublime."),
        ("amit_wander", 4, "Calm and peaceful temple. Ample space for sitting, meditating, and walking in the gardens."),
        ("kavita_morning", 5, "Loved the tranquil environment and pleasant temple chants during evening prayer."),
    ],
    "Zero Mile Marker": [
        ("aarav_safari", 5, "Historic geographical milestone marking the exact center of undivided India. Fascinating colonial history."),
        ("rohit_nature", 4, "Nice quick heritage stop in Civil Lines. Great to see the Great Trigonometrical Survey benchmark in person."),
        ("priya_explorer", 4, "Unique monument with sandstone pillar and stone horses. Nicely integrated into the modern metro corridor."),
        ("vikram_tiger", 5, "Must-see landmark for trivia and geography lovers visiting Nagpur. Zero Mile metro station is right here."),
        ("ananya_bio", 5, "Iconic symbol of Nagpur as India's center point. Located in the lush green Civil Lines district."),
        ("rajesh_tours", 4, "Quick 15-minute photo stop with high historical relevance. Very easy city accessibility."),
        ("sneha_clicks", 5, "Classic historical landmark. Beautifully maintained heritage enclave."),
        ("sanjay_guide", 5, "Every India traveler should visit the point from where all national highway distances were measured."),
    ],
    "Totladoh Dam": [
        ("neha_wildlife", 5, "Enormous reservoir set amidst the dense hills of Pench corridor. The sheer scale and forest views are majestic."),
        ("rohit_nature", 5, "Untouched wilderness and breathtaking backwaters. Great birdwatching with crested serpent eagles and storks."),
        ("priya_explorer", 4, "Remote, tranquil, and ruggedly scenic. Check entry rules beforehand since it borders protected forest zones."),
        ("vikram_tiger", 5, "Stunning scenic drive through Satpura hills. The reservoir looks like an inland sea surrounded by teak forests."),
        ("ananya_bio", 5, "Magnificent water body sustaining the Pench ecosystem. Pristine nature at its purest."),
        ("rajesh_tours", 4, "Scenic escape from urban noise. Ideal for nature lovers visiting Pench Maharashtra side."),
        ("sneha_clicks", 5, "Epic panoramic views over the Pench river basin. Breathtaking during monsoon and winter."),
        ("amit_wander", 4, "Peaceful picnic spot and wildlife corridor. Best accessed with private SUV or hired cab."),
    ],
    "Shree Mahalaxmi Jagdamba Temple": [
        ("aarav_safari", 5, "Famous Koradi temple with tremendous spiritual heritage. The temple complex is grand and beautifully renovated."),
        ("neha_wildlife", 5, "Very sacred and powerful shrine of Goddess Jagdamba. The newly built complex and lighting are spectacular."),
        ("rohit_nature", 5, "Spiritual energy here is incredible. Devotees visit from all over central India. Great queue management."),
        ("priya_explorer", 4, "Historic temple located 15 km north of Nagpur. Weekday visits are relaxed and quick."),
        ("vikram_tiger", 5, "Majestic evening aarti and serene temple pond. The surrounding park and fountain add great charm."),
        ("rajesh_tours", 5, "Well organized darshan facilities, clean water and prasad counters. Worth visiting when in Nagpur."),
        ("kavita_morning", 5, "Deeply peaceful experience. Beautiful marble craftsmanship throughout the sanctum."),
        ("pooja_family", 5, "Family had a very blessed darshan. Safe, clean, and spiritually uplifting."),
    ],
    "Adasa Ganpati Temple": [
        ("aarav_safari", 5, "One of the revered ancient Ganesh temples in Vidarbha. The monolithic idol is deeply sacred and peaceful."),
        ("rohit_nature", 5, "Historic hillock temple surrounded by lush countryside. The ancient stone steps and tranquil breeze are delightful."),
        ("priya_explorer", 4, "Scenic drive through Kalmeshwar / Saoner side (~43 km from Nagpur). Very calm village setting."),
        ("vikram_tiger", 5, "Spiritual oasis with centuries of heritage. The deity is worshipped as Shammi Vighneshwar."),
        ("ananya_bio", 5, "Serene surroundings with smaller ancient Shiva temples on the same hill. Great peaceful day trip."),
        ("rajesh_tours", 5, "Very clean temple premises and respectful priests. Prasad is delicious and authentic."),
        ("kavita_morning", 5, "Felt deeply peaceful after morning prayers. Beautiful countryside views from the temple top."),
        ("pooja_family", 4, "Wonderful family pilgrimage spot. Road from Nagpur is well paved."),
    ],
}


def _slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").replace(".", "").replace("'", "").replace("&", "and").replace(",", "")


async def seed_nagpur_all():
    async with AsyncSessionLocal() as db:
        print("--- 1. Seeding Nagpur Hotels & Safari Resorts ---")
        for h in NAGPUR_HOTELS:
            ext_id = f"curated:nagpur:hotel:{_slugify(h['name'])}"
            res = await db.execute(select(Attraction).where(Attraction.external_id == ext_id))
            existing = res.scalar_one_or_none()
            if not existing:
                hotel = Attraction(
                    external_id=ext_id,
                    source="curated",
                    name=h["name"],
                    district=h["district"],
                    state=h["state"],
                    category=h["category"],
                    area=h["area"],
                    lat=h["lat"],
                    lng=h["lng"],
                    coordinates_verified=False,
                    opening_access=h.get("opening_access"),
                    phone=h.get("phone"),
                    price_tier=h.get("price_tier"),
                    specialty=h.get("specialty"),
                    amenities=h.get("amenities", []),
                    booking_url=h.get("booking_url"),
                    data_quality_note=h.get("data_quality_note"),
                    external_rating=h.get("external_rating"),
                    external_rating_count=h.get("external_rating_count"),
                    external_rating_source="Google Maps",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(hotel)
                print(f"  + Added Hotel: {h['name']} ({h['area']})")
            else:
                existing.amenities = h.get("amenities", [])
                existing.phone = h.get("phone")
                existing.price_tier = h.get("price_tier")
                existing.specialty = h.get("specialty")
                existing.booking_url = h.get("booking_url")
                existing.external_rating = h.get("external_rating")
                existing.external_rating_count = h.get("external_rating_count")

        print("\n--- 2. Seeding Nagpur Restaurants, Saoji Eateries & Cafes ---")
        for r in NAGPUR_RESTAURANTS:
            ext_id = f"curated:nagpur:restaurant:{_slugify(r['name'])}"
            res = await db.execute(select(Attraction).where(Attraction.external_id == ext_id))
            existing = res.scalar_one_or_none()
            if not existing:
                restaurant = Attraction(
                    external_id=ext_id,
                    source="curated",
                    name=r["name"],
                    district=r["district"],
                    state=r["state"],
                    category=r["category"],
                    area=r["area"],
                    lat=r["lat"],
                    lng=r["lng"],
                    coordinates_verified=False,
                    opening_access=r.get("opening_access"),
                    phone=r.get("phone"),
                    price_tier=r.get("price_tier"),
                    specialty=r.get("specialty"),
                    amenities=[],
                    data_quality_note=r.get("data_quality_note"),
                    external_rating=r.get("external_rating"),
                    external_rating_count=r.get("external_rating_count"),
                    external_rating_source="Google Maps",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(restaurant)
                print(f"  + Added Restaurant: {r['name']} ({r['area']})")
            else:
                existing.phone = r.get("phone")
                existing.price_tier = r.get("price_tier")
                existing.specialty = r.get("specialty")
                existing.external_rating = r.get("external_rating")
                existing.external_rating_count = r.get("external_rating_count")

        await db.flush()

        print("\n--- 3. Seeding Authentic Visitor Reviews for Nagpur Tourist Spots ---")
        default_pwd = hash_password("Visitor@12345")

        for spot_name, reviews in ATTRACTION_REVIEWS.items():
            res = await db.execute(
                select(Attraction).where(
                    Attraction.name.ilike(f"%{spot_name}%"),
                    Attraction.district == "Nagpur"
                )
            )
            attraction = res.scalars().first()
            if not attraction:
                print(f"  ! Attraction not found for review seeding: {spot_name}")
                continue

            for username, rating, comment in reviews:
                user_res = await db.execute(select(User).where(User.username == username))
                user = user_res.scalar_one_or_none()
                if not user:
                    user = User(
                        username=username,
                        email=f"{username}@example.com",
                        hashed_password=default_pwd,
                        is_active=True,
                        created_at=datetime.utcnow(),
                    )
                    db.add(user)
                    await db.flush()

                rev_res = await db.execute(
                    select(Review).where(
                        Review.attraction_id == attraction.id,
                        Review.user_id == user.id,
                    )
                )
                rev = rev_res.scalar_one_or_none()
                if not rev:
                    rev = Review(
                        attraction_id=attraction.id,
                        user_id=user.id,
                        rating=rating,
                        comment=comment,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    db.add(rev)
                else:
                    rev.rating = rating
                    rev.comment = comment

            await db.flush()
            await _recompute_rating(db, attraction.id)
            await db.flush()
            await db.refresh(attraction)
            avg_str = f"{attraction.avg_rating:.1f}" if attraction.avg_rating is not None else "N/A"
            print(f"  ★ Seeded {len(reviews)} reviews for '{attraction.name}' -> Avg Rating: {avg_str} ★ ({attraction.review_count} reviews)")

        await db.commit()
        print("\n--- Nagpur District Full Seeding Completed Successfully! ---")


if __name__ == "__main__":
    asyncio.run(seed_nagpur_all())
