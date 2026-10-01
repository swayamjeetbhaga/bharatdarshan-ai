from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import SignupRequest, LoginRequest
import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL)

async def signup(data: SignupRequest, db: AsyncSession):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def login(data: LoginRequest, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    # Store refresh token in Redis with expiry
    await redis_client.setex(
        f"refresh:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        refresh_token
    )

    return {"access_token": access_token, "refresh_token": refresh_token}

async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")

    # Check Redis — token must exist and match
    stored = await redis_client.get(f"refresh:{user_id}")
    if not stored or stored.decode() != refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token expired or reused")

    # Issue new access token
    new_access = create_access_token({"sub": user_id, "email": payload.get("email")})
    return {"access_token": new_access, "refresh_token": refresh_token}

async def logout(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload:
        await redis_client.delete(f"refresh:{payload.get('sub')}")