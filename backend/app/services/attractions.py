from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attraction import Attraction, Review
from app.models.user import User
from app.schemas.attraction import ReviewCreate, AttractionResolveRequest

def _slugify(name: str) -> str:
    return "-".join(name.strip().lower().split())

def _external_id_for(data: AttractionResolveRequest) -> str:
    if data.osm_type and data.osm_id is not None:
        return f"osm:{data.osm_type}:{data.osm_id}"
    # No stable geocoder id available — fall back to a rounded-coordinate key
    # so the same point searched twice still resolves to one row.
    return f"geo:{round(data.lat, 5)}:{round(data.lng, 5)}:{_slugify(data.name)}"

async def list_attractions(db: AsyncSession, district: str | None = None) -> list[Attraction]:
    query = select(Attraction).order_by(Attraction.name)
    if district:
        query = query.where(Attraction.district.ilike(f"%{district}%"))
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_attraction(db: AsyncSession, attraction_id: int) -> Attraction:
    attraction = await db.get(Attraction, attraction_id)
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return attraction

async def resolve_attraction(db: AsyncSession, data: AttractionResolveRequest) -> Attraction:
    """Find the Attraction for a place surfaced by live map search, creating
    a lightweight 'community' row the first time anyone opens it — this is
    what lets reviews/photos work for any place in India, not just the
    curated pilot datasets."""
    external_id = _external_id_for(data)

    result = await db.execute(select(Attraction).where(Attraction.external_id == external_id))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    attraction = Attraction(
        external_id=external_id,
        source="community",
        name=data.name,
        district=data.district,
        state=data.state,
        category=data.category or "place",
        area=data.area,
        lat=data.lat,
        lng=data.lng,
        coordinates_verified=True,  # came from a live geocoder, not a hand estimate
    )
    db.add(attraction)
    try:
        await db.commit()
    except Exception:
        # Lost a race with a concurrent resolve of the same place.
        await db.rollback()
        result = await db.execute(select(Attraction).where(Attraction.external_id == external_id))
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        raise
    await db.refresh(attraction)
    return attraction

async def add_photo(db: AsyncSession, attraction_id: int, url: str) -> Attraction:
    attraction = await get_attraction(db, attraction_id)
    attraction.photo_urls = [*attraction.photo_urls, url]
    await db.commit()
    await db.refresh(attraction)
    return attraction

async def list_reviews(db: AsyncSession, attraction_id: int) -> list[tuple[Review, str]]:
    result = await db.execute(
        select(Review, User.username)
        .join(User, User.id == Review.user_id)
        .where(Review.attraction_id == attraction_id)
        .order_by(Review.created_at.desc())
    )
    return list(result.all())

async def get_my_review(db: AsyncSession, attraction_id: int, user_id: int) -> tuple[Review, str] | None:
    result = await db.execute(
        select(Review, User.username)
        .join(User, User.id == Review.user_id)
        .where(Review.attraction_id == attraction_id, Review.user_id == user_id)
    )
    return result.first()

async def _recompute_rating(db: AsyncSession, attraction_id: int) -> None:
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(
            Review.attraction_id == attraction_id
        )
    )
    avg_rating, review_count = result.one()
    attraction = await db.get(Attraction, attraction_id)
    attraction.avg_rating = round(float(avg_rating), 2) if avg_rating is not None else None
    attraction.review_count = review_count or 0

async def upsert_review(
    db: AsyncSession, attraction_id: int, user_id: int, data: ReviewCreate
) -> Review:
    await get_attraction(db, attraction_id)

    result = await db.execute(
        select(Review).where(Review.attraction_id == attraction_id, Review.user_id == user_id)
    )
    review = result.scalar_one_or_none()
    if review:
        review.rating = data.rating
        review.comment = data.comment
    else:
        review = Review(
            attraction_id=attraction_id,
            user_id=user_id,
            rating=data.rating,
            comment=data.comment,
        )
        db.add(review)

    await db.flush()
    await _recompute_rating(db, attraction_id)
    await db.commit()
    await db.refresh(review)
    return review

async def delete_my_review(db: AsyncSession, attraction_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Review).where(Review.attraction_id == attraction_id, Review.user_id == user_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    await db.delete(review)
    await db.flush()
    await _recompute_rating(db, attraction_id)
    await db.commit()
