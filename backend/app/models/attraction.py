from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.session import Base

# Curated categories used by our own hand-seeded datasets (Chandrapur today,
# more districts later). Places resolved on the fly from a live map search
# elsewhere in India store whatever free-text category the geocoder gives
# them instead — `category` is intentionally not DB-constrained to this list.
CURATED_CATEGORIES = (
    "wildlife",
    "lake_nature",
    "religious_heritage",
    "historical_fort",
    "social_educational",
)

# 'curated': hand-verified pilot dataset entries (e.g. the Chandrapur seed).
# 'community': lazily created the first time someone opens/reviews/photographs
# a place found through live map search, anywhere in India.
ATTRACTION_SOURCES = ("curated", "community")

class Attraction(Base):
    __tablename__ = "attractions"
    __table_args__ = (
        CheckConstraint(
            f"source IN ({', '.join(repr(s) for s in ATTRACTION_SOURCES)})",
            name="ck_attraction_source",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    # Stable dedupe key: "osm:<type>:<id>" for geocoder-backed places, or
    # "curated:<slug>" for hand-seeded ones — lets repeated searches/resolves
    # of the same real-world place converge on one row instead of duplicating.
    external_id = Column(String, nullable=False, unique=True, index=True)
    source = Column(String, nullable=False, default="community")
    name = Column(String, nullable=False, index=True)
    district = Column(String, nullable=True, index=True)
    state = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    area = Column(String, nullable=True)

    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    coordinates_verified = Column(Boolean, nullable=False, default=False)

    distance_from_chandrapur_km = Column(Float, nullable=True)
    distance_from_nagpur_km = Column(Float, nullable=True)
    distance_from_nagpur_airport_km = Column(Float, nullable=True)

    opening_access = Column(String, nullable=True)
    entry_fee_status = Column(String, nullable=True)
    transportation = Column(String, nullable=True)
    data_quality_note = Column(Text, nullable=True)
    source_urls = Column(JSONB, nullable=False, default=list)
    dataset_prepared_on = Column(Date, nullable=True)

    phone = Column(String, nullable=True)
    price_tier = Column(String, nullable=True)
    specialty = Column(String, nullable=True)

    # A rating snapshot from an external source (e.g. Google Maps at seed
    # time) — kept separate from avg_rating/review_count below, which are
    # always a live aggregate of OUR OWN `reviews` rows. Mixing the two would
    # mean the first in-app review silently wipes out the imported number.
    external_rating = Column(Float, nullable=True)
    external_rating_count = Column(Integer, nullable=True)
    external_rating_source = Column(String, nullable=True)

    # Official online booking/permit portal, for places like national parks
    # where a safari slot must be reserved in advance.
    booking_url = Column(String, nullable=True)

    # Facility list — hotels/resorts (AC Rooms, Pool, Restaurant, ...).
    amenities = Column(JSONB, nullable=False, default=list)

    photo_urls = Column(JSONB, nullable=False, default=list)
    avg_rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("attraction_id", "user_id", name="uq_review_attraction_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    attraction_id = Column(Integer, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
