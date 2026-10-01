from pydantic import BaseModel

class PlaceSearchRequest(BaseModel):
    query: str
    country: str = "India"

class NearbyRequest(BaseModel):
    lat: float
    lng: float
    radius: int = 5000
    category: str = "tourism"

class DirectionsByCoordsRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
