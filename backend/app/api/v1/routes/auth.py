from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services import auth as auth_service
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=201)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.signup(data, db)
    return {"message": "User created", "username": user.username}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(data, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    return await auth_service.refresh(data.refresh_token)

@router.post("/logout")
async def logout(data: RefreshRequest):
    await auth_service.logout(data.refresh_token)
    return {"message": "Logged out"}

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
    }