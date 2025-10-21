# ============================================================================
# LOCATION SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-21 09:21:01 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.location import (
    create_location,
    get_location,
    get_locations,
    update_location,
    delete_location,
)
from schemas.location import LocationCreate, LocationUpdate, LocationOut


async def add_location(location_data: LocationCreate) -> LocationOut:
    """adds an entry of LocationCreate to the database and returns an object

    Returns:
        _type_: LocationOut
    """
    return await create_location(location_data)


async def remove_location(location_id: str):
    """deletes a field from the database and removes LocationCreateobject 

    Raises:
        HTTPException 400: Invalid location ID format
        HTTPException 404:  Location not found
    """
    if not ObjectId.is_valid(location_id):
        raise HTTPException(status_code=400, detail="Invalid location ID format")

    filter_dict = {"_id": ObjectId(location_id)}
    result = await delete_location(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")


async def retrieve_location_by_location_id(id: str) -> LocationOut:
    """Retrieves location object based specific Id 

    Raises:
        HTTPException 404(not found): if  Location not found in the db
        HTTPException 400(bad request): if  Invalid location ID format

    Returns:
        _type_: LocationOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid location ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_location(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Location not found")

    return result


async def retrieve_locations(start=0,stop=100) -> List[LocationOut]:
    """Retrieves LocationOut Objects in a list

    Returns:
        _type_: LocationOut
    """
    return await get_locations(start=start,stop=stop)


async def update_location_by_id(location_id: str, location_data: LocationUpdate) -> LocationOut:
    """updates an entry of location in the database

    Raises:
        HTTPException 404(not found): if Location not found or update failed
        HTTPException 400(not found): Invalid location ID format

    Returns:
        _type_: LocationOut
    """
    if not ObjectId.is_valid(location_id):
        raise HTTPException(status_code=400, detail="Invalid location ID format")

    filter_dict = {"_id": ObjectId(location_id)}
    result = await update_location(filter_dict, location_data)

    if not result:
        raise HTTPException(status_code=404, detail="Location not found or update failed")

    return result