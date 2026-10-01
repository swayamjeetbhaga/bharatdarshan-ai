from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field

class AttractionCategory(str, Enum):
    """Categories used by our own curated datasets (Chandrapur today, more
    districts later). Community-resolved places store whatever free-text
    category the map search gives them, so this enum is a display hint for
    the frontend, not a hard constraint on `Attraction.category`."""

    WILDLIFE = "wildlife"
    LAKE_NATURE = "lake_nature"
    RELIGIOUS_HERITAGE = "religious_heritage"
    HISTORICAL_FORT = "historical_fort"
    SOCIAL_EDUCATIONAL = "social_educational"

class AttractionSource(str, Enum):
    CURATED = "curated"
    COMMUNITY = "community"

class AttractionOut(BaseModel):
    id: int
    external_id: str
    source: AttractionSource
    name: str
    district: str | None = None
    state: str | None = None
    category: str
    area: str | None = None
    lat: float
    lng: float
    coordinates_verified: bool
    distance_from_chandrapur_km: float | None = None
    distance_from_nagpur_km: float | None = None
    distance_from_nagpur_airport_km: float | None = None
    opening_access: str | None = None
    entry_fee_status: str | None = None
    transportation: str | None = None
    data_quality_note: str | None = None
    source_urls: list[str] = []
    dataset_prepared_on: date | None = None
    phone: str | None = None
    price_tier: str | None = None
    specialty: str | None = None
    external_rating: float | None = None
    external_rating_count: int | None = None
    external_rating_source: str | None = None
    booking_url: str | None = None
    amenities: list[str] = []
    photo_urls: list[str] = []
    avg_rating: float | None = None
    review_count: int

    class Config:
        from_attributes = True

class ReviewOut(BaseModel):
    id: int
    user_id: int
    username: str
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AttractionDetailOut(AttractionOut):
    reviews: list[ReviewOut] = []
    my_review: ReviewOut | None = None

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)

class AttractionResolveRequest(BaseModel):
    """Identifies a place found through live map search so it can be
    looked up (or lazily created) as a reviewable/photographable Attraction.
    """

    name: str
    lat: float
    lng: float
    category: str | None = None
    area: str | None = None
    district: str | None = None
    state: str | None = None
    osm_type: str | None = None
    osm_id: int | None = None
