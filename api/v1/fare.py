
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.fare import (
    FareCreate,
    FareOut,
    FareBase,
    FareUpdate,
)
from services.fare_service import (
    add_fare,
    remove_fare,
    retrieve_fares,
    retrieve_fare_by_fare_id,
    update_fare_by_id,
)

router = APIRouter(prefix="/fares", tags=["Fares"])

@router.get("/", response_model=APIResponse[List[FareOut]])
async def list_fares():
    items = await retrieve_fares()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[FareOut])
async def get_my_fares(id: str = Query(..., description="fare ID to fetch specific item")):
    items = await retrieve_fare_by_fare_id(id=id)
    return APIResponse(status_code=200, data=items, detail="fares items fetched")
