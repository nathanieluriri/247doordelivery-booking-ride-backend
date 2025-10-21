
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
from typing import List
from schemas.response_schema import APIResponse
from schemas.tokens_schema import accessTokenOut
from schemas.driver import (
    DriverCreate,
    DriverOut,
    DriverBase,
    DriverUpdate,
    DriverRefresh,
)
from services.driver_service import (
    add_driver,
    remove_driver,
    retrieve_drivers,
    authenticate_driver,
    retrieve_driver_by_driver_id,
    update_driver,
    update_driver_by_id,
    refresh_driver_tokens_reduce_number_of_logins,

)
from security.auth import verify_token,verify_token_to_refresh
router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/",response_model_exclude={"data": {"__all__": {"password"}}}, response_model=APIResponse[List[DriverOut]],response_model_exclude_none=True,dependencies=[Depends(verify_token)])
async def list_drivers(start:int= 0, stop:int=100):
    items = await retrieve_drivers(start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model_exclude={"data": {"password"}},response_model=APIResponse[DriverOut],dependencies=[Depends(verify_token)],response_model_exclude_none=True)
async def get_driver_details(token:accessTokenOut = Depends(verify_token)):
    items = await retrieve_driver_by_driver_id(id=token.userId)
    return APIResponse(status_code=200, data=items, detail="users items fetched")



@router.post("/signup", response_model_exclude={"data": {"password"}},response_model=APIResponse[DriverOut])
async def signup_new_driver(user_data:DriverBase):
    new_user = DriverCreate(**user_data.model_dump())
    items = await add_driver(driver_data=new_user)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.post("/login",response_model_exclude={"data": {"password"}}, response_model=APIResponse[DriverOut])
async def login_driver(user_data:DriverBase):
    items = await authenticate_driver(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.post("/refesh",response_model_exclude={"data": {"password"}},response_model=APIResponse[DriverOut],dependencies=[Depends(verify_token_to_refresh)])
async def refresh_driver_tokens(user_data:DriverRefresh,token:accessTokenOut = Depends(verify_token_to_refresh)):
    
    items= await refresh_driver_tokens_reduce_number_of_logins(user_refresh_data=user_data,expired_access_token=token.accesstoken)

    return APIResponse(status_code=200, data=items, detail="users items fetched")


@router.delete("/account",dependencies=[Depends(verify_token)])
async def delete_user_account(token:accessTokenOut = Depends(verify_token)):
    result = await remove_driver(driver_id=token.userId)
    return result