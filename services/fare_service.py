# ============================================================================
# FARE SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-23 12:39:50 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.fare import (
    create_fare,
    get_fare,
    get_fares,
    update_fare,
    delete_fare,
)
from schemas.fare import FareCreate, FareUpdate, FareOut


async def add_fare(fare_data: FareCreate) -> FareOut:
    """adds an entry of FareCreate to the database and returns an object

    Returns:
        _type_: FareOut
    """
    return await create_fare(fare_data)


async def remove_fare(fare_id: str):
    """deletes a field from the database and removes FareCreateobject 

    Raises:
        HTTPException 400: Invalid fare ID format
        HTTPException 404:  Fare not found
    """
    if not ObjectId.is_valid(fare_id):
        raise HTTPException(status_code=400, detail="Invalid fare ID format")

    filter_dict = {"_id": ObjectId(fare_id)}
    result = await delete_fare(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fare not found")


async def retrieve_fare_by_fare_id(id: str) -> FareOut:
    """Retrieves fare object based specific Id 

    Raises:
        HTTPException 404(not found): if  Fare not found in the db
        HTTPException 400(bad request): if  Invalid fare ID format

    Returns:
        _type_: FareOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid fare ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_fare(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Fare not found")

    return result


async def retrieve_fares(start=0,stop=100) -> List[FareOut]:
    """Retrieves FareOut Objects in a list

    Returns:
        _type_: FareOut
    """
    return await get_fares(start=start,stop=stop)


async def update_fare_by_id(fare_id: str, fare_data: FareUpdate) -> FareOut:
    """updates an entry of fare in the database

    Raises:
        HTTPException 404(not found): if Fare not found or update failed
        HTTPException 400(not found): Invalid fare ID format

    Returns:
        _type_: FareOut
    """
    if not ObjectId.is_valid(fare_id):
        raise HTTPException(status_code=400, detail="Invalid fare ID format")

    filter_dict = {"_id": ObjectId(fare_id)}
    result = await update_fare(filter_dict, fare_data)

    if not result:
        raise HTTPException(status_code=404, detail="Fare not found or update failed")

    return result