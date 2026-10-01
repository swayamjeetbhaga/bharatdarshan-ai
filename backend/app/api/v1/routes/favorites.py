from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.services import favorites as favorites_service
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("", response_model=list[FavoriteResponse])
async def list_favorites(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await favorites_service.list_favorites(db, current_user)

@router.post("", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    data: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await favorites_service.add_favorite(db, current_user, data)

@router.delete("/{favorite_id}", status_code=204)
async def remove_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await favorites_service.remove_favorite(db, current_user, favorite_id)
