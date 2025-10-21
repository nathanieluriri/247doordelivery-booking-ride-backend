
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.ride import (
    RideCreate,
    RideOut,
    RideBase,
    RideUpdate,
)
from services.ride_service import (
    add_ride,
    remove_ride,
    retrieve_rides,
    retrieve_ride_by_ride_id,
    update_ride_by_id,
)

router = APIRouter(prefix="/rides", tags=["Rides"])

@router.get("/", response_model=APIResponse[List[RideOut]])
async def list_rides():
    items = await retrieve_rides()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[RideOut])
async def get_my_ride_details(id: str = Query(..., description="ride ID to fetch specific item")):
    items = await retrieve_ride_by_ride_id(id=id)
    return APIResponse(status_code=200, data=items, detail="rides items fetched")

