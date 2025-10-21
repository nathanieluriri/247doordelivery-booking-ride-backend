
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.location import (
    LocationCreate,
    LocationOut,
    LocationBase,
    LocationUpdate,
)
from services.location_service import (
    add_location,
    remove_location,
    retrieve_locations,
    retrieve_location_by_location_id,
    update_location_by_id,
)

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/", response_model=APIResponse[List[LocationOut]])
async def list_locations():
    items = await retrieve_locations()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[LocationOut])
async def get_my_locations(id: str = Query(..., description="location ID to fetch specific item")):
    items = await retrieve_location_by_location_id(id=id)
    return APIResponse(status_code=200, data=items, detail="locations items fetched")
