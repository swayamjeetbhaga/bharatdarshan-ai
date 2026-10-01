import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.attraction import Attraction
from app.data.nagpur_places import NAGPUR_ATTRACTIONS

async def run():
    async with AsyncSessionLocal() as db:
        for p in NAGPUR_ATTRACTIONS:
            res = await db.execute(select(Attraction).where(Attraction.name == p["name"]))
            existing = res.scalars().first()
            if not existing:
                attraction = Attraction(
                    external_id=f"nagpur_place_{p['name'].lower().replace(' ', '_')}",
                    source="curated",
                    district="Nagpur",
                    state="Maharashtra",
                    **p
                )
                db.add(attraction)
        await db.commit()
        print("Successfully seeded Ramtek places.")

if __name__ == "__main__":
    asyncio.run(run())
