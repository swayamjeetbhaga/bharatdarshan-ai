from datetime import datetime
from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    name: str
    lat: float
    lng: float
    category: str | None = None
    address: str | None = None
    opening_hours: str | None = None
    website: str | None = None

class FavoriteResponse(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    category: str | None = None
    address: str | None = None
    opening_hours: str | None = None
    website: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
