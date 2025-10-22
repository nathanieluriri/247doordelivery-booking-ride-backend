# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from security.tokens import validate_admin_accesstoken_otp
from security.encrypting_jwt import decode_jwt_token,decode_jwt_token_without_expiration,JWTPayload
from repositories.tokens_repo import get_access_tokens,get_access_tokens_no_date_check
from schemas.tokens_schema import refreshedToken,accessTokenOut
from services.admin_service import retrieve_admin_by_admin_id
from services.driver_service import retrieve_driver_by_driver_id
from services.user_service import retrieve_user_by_user_id


token_auth_scheme = HTTPBearer()

async def verify_token_user_role(token: str = Depends(token_auth_scheme))->accessTokenOut:
    try:
        decoded_token =decode_jwt_token(token=token.credentials)
        result = await get_access_tokens(accessToken=decoded_token.access_token)
        USER = await retrieve_user_by_user_id(id=decoded_token.user_id)
        if USER and result!=None:
            return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token :{e}"
        )    
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    else:
        return result
            
            
            
async def verify_token_driver_role(token: str = Depends(token_auth_scheme))->accessTokenOut:
    try:
        decoded_token =decode_jwt_token(token=token.credentials)
        result = await get_access_tokens(accessToken=decoded_token.access_token)
        driver = await retrieve_driver_by_driver_id(id=decoded_token.user_id)
        if driver and result!=None:
            return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token :{e}"
        )    
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
   
            
            


           
async def verify_token_to_refresh(token: str = Depends(token_auth_scheme)):
    
    try:
        decoded_token =decode_jwt_token(token=token.credentials,allow_expired=True)
        result = await get_access_tokens_no_date_check(accessToken=decoded_token.access_token) 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        ) 
    
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    else:
        return result
        
        
      
async def verify_admin_token(token: str = Depends(token_auth_scheme)):
    from repositories.tokens_repo import get_admin_access_tokens
    
    try:
        decoded_token = decode_jwt_token(token=token.credentials)
     
        result = await get_admin_access_tokens(accessToken=decoded_token.access_token)

        if result==None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token"
            )
        elif result=="inactive":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin Token hasn't been activated"
            )
        elif isinstance(result, accessTokenOut):
            
            decoded_access_token = decode_jwt_token(token=token.credentials)
            return decoded_access_token
    except TypeError as e:
        print(e)
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
    
    

async def verify_any_token(token:str=Depends(token_auth_scheme)):
    decoded_token = decode_jwt_token(token=token.credentials)
    if isinstance(decoded_token,JWTPayload):
        
        if decoded_token.user_type =='ADMIN':
            return await verify_admin_token(token=token)
        elif decoded_token.user_type =='USER':
            return await verify_token_user_role(token=token)
        elif decoded_token.user_type =='DRIVER':
            return await verify_token_driver_role(token=token)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token Type"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )