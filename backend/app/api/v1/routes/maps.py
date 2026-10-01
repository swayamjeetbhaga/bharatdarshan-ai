from fastapi import APIRouter, Depends
from app.schemas.maps import PlaceSearchRequest, NearbyRequest, DirectionsByCoordsRequest
from app.services import maps as maps_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/search")
async def search(data: PlaceSearchRequest, current_user: User = Depends(get_current_user)):
    return await maps_service.search_places(data.query, data.country)

@router.post("/nearby")
async def nearby(data: NearbyRequest, current_user: User = Depends(get_current_user)):
    return await maps_service.nearby_places(data.lat, data.lng, data.radius, data.category)

@router.post("/directions-by-coords")
async def directions_by_coords(
    data: DirectionsByCoordsRequest, current_user: User = Depends(get_current_user)
):
    return await maps_service.get_directions_by_coords(
        data.origin_lat, data.origin_lng, data.dest_lat, data.dest_lng
    )
