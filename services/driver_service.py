# ============================================================================
# DRIVER SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-21 00:18:01 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.driver import (
    create_driver,
    get_driver,
    get_drivers,
    update_driver,
    delete_driver,
)
from schemas.driver import DriverCreate, DriverUpdate, DriverOut,DriverBase,DriverRefresh
from security.hash import check_password
from security.encrypting_jwt import create_jwt_member_token
from repositories.tokens_repo import add_refresh_tokens, add_access_tokens, accessTokenCreate,accessTokenOut,refreshTokenCreate
from repositories.tokens_repo import get_refresh_tokens,get_access_tokens,delete_access_token,delete_refresh_token,delete_all_tokens_with_user_id
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()



oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
 

async def add_driver(driver_data: DriverCreate) -> DriverOut:
    """adds an entry of UserCreate to the database and returns an object

    Returns:
        _type_: UserOut
    """
    user =  await get_driver(filter_dict={"email":driver_data.email})
    if user==None:
        new_user= await create_driver(driver_data)
        access_token = await add_access_tokens(token_data=accessTokenCreate(userId=new_user.id))
        refresh_token  = await add_refresh_tokens(token_data=refreshTokenCreate(userId=new_user.id,previousAccessToken=access_token.accesstoken))
        new_user.password=""
        new_user.access_token= access_token.accesstoken 
        new_user.refresh_token = refresh_token.refreshtoken
        return new_user
    else:
        raise HTTPException(status_code=409,detail="User Already exists")


async def authenticate_driver(user_data:DriverBase )->DriverOut:
    user = await get_driver(filter_dict={"email":user_data.email})

    if user != None:
        if check_password(password=user_data.password,hashed=user.password ):
            user.password=""
            access_token = await add_access_tokens(token_data=accessTokenCreate(userId=user.id))
            refresh_token  = await add_refresh_tokens(token_data=refreshTokenCreate(userId=user.id,previousAccessToken=access_token.accesstoken))
            user.access_token= access_token.accesstoken 
            user.refresh_token = refresh_token.refreshtoken
            return user
        else:
            raise HTTPException(status_code=401, detail="Unathorized, Invalid Login credentials")
    else:
        raise HTTPException(status_code=404,detail="User not found")


async def refresh_driver_tokens_reduce_number_of_logins(user_refresh_data:DriverRefresh,expired_access_token):
    refreshObj= await get_refresh_tokens(user_refresh_data.refresh_token)
    if refreshObj:
        if refreshObj.previousAccessToken==expired_access_token:
            user = await get_driver(filter_dict={"_id":ObjectId(refreshObj.userId)})
            
            if user!= None:
                    access_token = await add_access_tokens(token_data=accessTokenCreate(userId=user.id))
                    refresh_token  = await add_refresh_tokens(token_data=refreshTokenCreate(userId=user.id,previousAccessToken=access_token.accesstoken))
                    user.access_token= access_token.accesstoken 
                    user.refresh_token = refresh_token.refreshtoken
                    await delete_access_token(accessToken=expired_access_token)
                    await delete_refresh_token(refreshToken=user_refresh_data.refresh_token)
                    return user
     
        await delete_refresh_token(refreshToken=user_refresh_data.refresh_token)
        await delete_access_token(accessToken=expired_access_token)
  
    raise HTTPException(status_code=404,detail="Invalid refresh token ")  


async def remove_driver(driver_id: str):
    """deletes a field from the database and removes DriverCreateobject 

    Raises:
        HTTPException 400: Invalid driver ID format
        HTTPException 404:  Driver not found
    """
    if not ObjectId.is_valid(driver_id):
        raise HTTPException(status_code=400, detail="Invalid driver ID format")

    filter_dict = {"_id": ObjectId(driver_id)}
    result = await delete_driver(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Driver not found")


async def retrieve_driver_by_driver_id(id: str) -> DriverOut:
    """Retrieves driver object based specific Id 

    Raises:
        HTTPException 404(not found): if  Driver not found in the db
        HTTPException 400(bad request): if  Invalid driver ID format

    Returns:
        _type_: DriverOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid driver ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_driver(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Driver not found")

    return result


async def retrieve_drivers(start=0,stop=100) -> List[DriverOut]:
    """Retrieves DriverOut Objects in a list

    Returns:
        _type_: DriverOut
    """
    return await get_drivers(start=start,stop=stop)


async def update_driver_by_id(driver_id: str, driver_data: DriverUpdate) -> DriverOut:
    """updates an entry of driver in the database

    Raises:
        HTTPException 404(not found): if Driver not found or update failed
        HTTPException 400(not found): Invalid driver ID format

    Returns:
        _type_: DriverOut
    """
    if not ObjectId.is_valid(driver_id):
        raise HTTPException(status_code=400, detail="Invalid driver ID format")

    filter_dict = {"_id": ObjectId(driver_id)}
    result = await update_driver(filter_dict, driver_data)

    if not result:
        raise HTTPException(status_code=404, detail="Driver not found or update failed")

    return result