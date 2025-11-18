from fastapi import APIRouter, Query
from sub_app.schemas.places import (
    AutocompleteResponse,
    PlaceDetailsResponse,
    ErrorResponse,
)
from sub_app.services.places import get_autocomplete, get_place_details
from typing import List, Union
from schemas.response_schema import APIResponse
router = APIRouter()

@router.get(
    "/autocomplete",
    response_model=APIResponse[Union[List[AutocompleteResponse],ErrorResponse]],
    summary="Get location suggestions (cached for 14 days)",
)
async def autocomplete(
    input: str = Query(..., description="User input text for autocomplete"),
    country: str | None = Query(None, description="Optional country code (e.g. 'us', 'ng')")
):
    """Return location autocomplete suggestions."""
    return await get_autocomplete(input, country)


@router.get(
    "/details",
     
    summary="Get place details (cached for 14 days)",
)
async def place_details(
    place_id: str = Query(..., description="Google Place ID")
):
    """Return full details for a given place."""
    return await get_place_details(place_id)
