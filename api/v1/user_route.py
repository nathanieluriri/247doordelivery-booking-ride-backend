
from fastapi import APIRouter, HTTPException, Query, Request, status, Path,Depends
from typing import List
from schemas.response_schema import APIResponse
from schemas.tokens_schema import accessTokenOut
from schemas.user_schema import (
    UserCreate,
    UserOut,
    UserBase,
    UserUpdate,
    UserRefresh,
)
from services.user_service import (
    add_user,
    remove_user,
    retrieve_users,
    authenticate_user,
    retrieve_user_by_user_id,
    update_user,
    update_user_by_id,
    refresh_user_tokens_reduce_number_of_logins,
    oauth

)
from security.auth import verify_token_to_refresh,verify_admin_token,verify_token_user_role



router = APIRouter(prefix="/users", tags=["Users"])
# --- Step 1: Redirect user to Google login ---
@router.get("/google/auth")
async def login(request: Request):
    base_url = request.url_for("root")
    redirect_uri = f"{base_url}auth/callback"
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


# --- Step 2: Handle callback from Google ---
@router.get("/auth/callback",response_model_exclude={"data": {"password"}},response_model=APIResponse[UserOut])
async def auth_callback(request: Request, ):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
    except:
        raise HTTPException(status_code=400,detail="Login session expired or was invalid. Please try logging in again.")
    # Just print or return user info for now
    if user_info:
        new_data= UserCreate(email=user_info["email"],password="",)
        old_data= UserBase(email=user_info["email"],password="",)
        try:
            user= await add_user(user_data=new_data)
        except:
            
           user= await authenticate_user(user_data=old_data)
        # user_info.get("email_verified",False)
        # user_info.get("given_name",None)
        # user_info.get("family_name",None)
        # user_info.get("picture",None)
        
        return APIResponse(status_code=200,detail="Successful Login",data=user)
    else:
        raise HTTPException(status_code=400,detail={"status": "failed", "message": "No user info found"})



@router.get("/",name="root",response_model_exclude={"data": {"__all__": {"password"}}}, response_model=APIResponse[List[UserOut]],response_model_exclude_none=True,dependencies=[Depends(verify_admin_token)])
async def list_users(start:int= 0, stop:int=100):
    items = await retrieve_users(start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model_exclude={"data": {"password"}},response_model=APIResponse[UserOut],dependencies=[Depends(verify_token_user_role)],response_model_exclude_none=True)
async def get_my_user_details(token:accessTokenOut = Depends(verify_token_user_role)):
    items = await retrieve_user_by_user_id(id=token.userId)
    return APIResponse(status_code=200, data=items, detail="users items fetched")

 


@router.post("/signup", response_model_exclude={"data": {"password"}},response_model=APIResponse[UserOut])
async def signup_new_user(user_data:UserBase):
    if len(user_data.password)<8:
        raise HTTPException(status_code=401,detail="Password too short")
    new_user = UserCreate(**user_data.model_dump())
    items = await add_user(user_data=new_user)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.post("/login",response_model_exclude={"data": {"password"}}, response_model=APIResponse[UserOut])
async def login_user(user_data:UserBase):
    if len(user_data.password)<8:
        raise HTTPException(status_code=401,detail="Password too short")
    items = await authenticate_user(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.post("/refesh",response_model_exclude={"data": {"password"}},response_model=APIResponse[UserOut],dependencies=[Depends(verify_token_to_refresh)])
async def refresh_user_tokens(user_data:UserRefresh,token:accessTokenOut = Depends(verify_token_to_refresh)):
    
    items= await refresh_user_tokens_reduce_number_of_logins(user_refresh_data=user_data,expired_access_token=token.accesstoken)

    return APIResponse(status_code=200, data=items, detail="users items fetched")


@router.delete("/account",dependencies=[Depends(verify_token_user_role)])
async def delete_user_account(token:accessTokenOut = Depends(verify_token_user_role)):
    result = await remove_user(user_id=token.userId)
    return result