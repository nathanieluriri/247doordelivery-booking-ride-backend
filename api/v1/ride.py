
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
async def list_ride_history_for_drivers_and_users():
    items = await retrieve_rides()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[RideOut])
async def use_ride_id_to_get_more_details_on_a_particular_ride(id: str = Query(..., description="ride ID to fetch specific item")):
    items = await retrieve_ride_by_ride_id(id=id)
    return APIResponse(status_code=200, data=items, detail="rides items fetched")


@router.post("/book",response_model=APIResponse[RideOut])
async def users_use_this_to_book_for_rides(ride:RideBase):
    pass
    
    
@router.post("/accept",response_model=APIResponse[RideOut])
async def drivers_use_this_to_accept_an_available_ride_that_was_suggested_for_said_driver(ride:RideBase):
    pass
