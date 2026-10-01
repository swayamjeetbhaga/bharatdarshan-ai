from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.favorite import FavoriteCreate

async def list_favorites(db: AsyncSession, user: User) -> list[Favorite]:
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == user.id).order_by(Favorite.created_at.desc())
    )
    return list(result.scalars().all())

async def add_favorite(db: AsyncSession, user: User, data: FavoriteCreate) -> Favorite:
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id,
            Favorite.name == data.name,
            Favorite.lat == data.lat,
            Favorite.lng == data.lng,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    favorite = Favorite(user_id=user.id, **data.model_dump())
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_favorite(db: AsyncSession, user: User, favorite_id: int) -> None:
    result = await db.execute(
        select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user.id)
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(favorite)
    await db.commit()
