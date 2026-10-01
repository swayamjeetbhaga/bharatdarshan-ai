from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.attraction import (
    AttractionOut,
    AttractionDetailOut,
    AttractionResolveRequest,
    ReviewOut,
    ReviewCreate,
)
from app.services import attractions as attractions_service
from app.services import uploads as uploads_service
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/attractions", tags=["attractions"])

def _review_out(review, username: str) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        user_id=review.user_id,
        username=username,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )

@router.get("", response_model=list[AttractionOut])
async def list_attractions(
    district: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await attractions_service.list_attractions(db, district)

@router.post("/resolve", response_model=AttractionOut)
async def resolve_attraction(
    data: AttractionResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await attractions_service.resolve_attraction(db, data)

@router.get("/{attraction_id}", response_model=AttractionDetailOut)
async def get_attraction(
    attraction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attraction = await attractions_service.get_attraction(db, attraction_id)
    reviews = await attractions_service.list_reviews(db, attraction_id)
    my_review_row = await attractions_service.get_my_review(db, attraction_id, current_user.id)

    return AttractionDetailOut(
        **AttractionOut.model_validate(attraction).model_dump(),
        reviews=[_review_out(review, username) for review, username in reviews],
        my_review=_review_out(*my_review_row) if my_review_row else None,
    )

@router.post("/{attraction_id}/photos", response_model=AttractionOut)
async def upload_photo(
    attraction_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await attractions_service.get_attraction(db, attraction_id)
    url = await uploads_service.save_attraction_photo(attraction_id, file)
    return await attractions_service.add_photo(db, attraction_id, url)

@router.post("/{attraction_id}/reviews", response_model=ReviewOut, status_code=201)
async def upsert_review(
    attraction_id: int,
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await attractions_service.upsert_review(db, attraction_id, current_user.id, data)
    return _review_out(review, current_user.username)

@router.delete("/{attraction_id}/reviews", status_code=204)
async def delete_my_review(
    attraction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await attractions_service.delete_my_review(db, attraction_id, current_user.id)
