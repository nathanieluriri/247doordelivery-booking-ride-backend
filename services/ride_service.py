# ============================================================================
# RIDE SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-21 02:22:58 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.ride import (
    create_ride,
    get_ride,
    get_rides,
    update_ride,
    delete_ride,
)
from schemas.ride import RideCreate, RideUpdate, RideOut


async def add_ride(ride_data: RideCreate) -> RideOut:
    """adds an entry of RideCreate to the database and returns an object

    Returns:
        _type_: RideOut
    """
    return await create_ride(ride_data)


async def remove_ride(ride_id: str):
    """deletes a field from the database and removes RideCreateobject 

    Raises:
        HTTPException 400: Invalid ride ID format
        HTTPException 404:  Ride not found
    """
    if not ObjectId.is_valid(ride_id):
        raise HTTPException(status_code=400, detail="Invalid ride ID format")

    filter_dict = {"_id": ObjectId(ride_id)}
    result = await delete_ride(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ride not found")


async def retrieve_ride_by_ride_id(id: str) -> RideOut:
    """Retrieves ride object based specific Id 

    Raises:
        HTTPException 404(not found): if  Ride not found in the db
        HTTPException 400(bad request): if  Invalid ride ID format

    Returns:
        _type_: RideOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ride ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_ride(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Ride not found")

    return result


async def retrieve_rides(start=0,stop=100) -> List[RideOut]:
    """Retrieves RideOut Objects in a list

    Returns:
        _type_: RideOut
    """
    return await get_rides(start=start,stop=stop)


async def update_ride_by_id(ride_id: str, ride_data: RideUpdate) -> RideOut:
    """updates an entry of ride in the database

    Raises:
        HTTPException 404(not found): if Ride not found or update failed
        HTTPException 400(not found): Invalid ride ID format

    Returns:
        _type_: RideOut
    """
    if not ObjectId.is_valid(ride_id):
        raise HTTPException(status_code=400, detail="Invalid ride ID format")

    filter_dict = {"_id": ObjectId(ride_id)}
    result = await update_ride(filter_dict, ride_data)

    if not result:
        raise HTTPException(status_code=404, detail="Ride not found or update failed")

    return result