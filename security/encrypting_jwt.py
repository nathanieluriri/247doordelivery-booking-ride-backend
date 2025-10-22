import jwt
import datetime
from dotenv import load_dotenv
import os
from pydantic import BaseModel,ValidationError
from datetime import datetime, timedelta
from authlib.jose import jwt, JoseError


# Secret key for signing (use env var in production)
SECRET_KEY = "super-secure-secret-key"
ALGORITHM = "HS256"

# Token lifetime (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60
load_dotenv()




# ---------------------------
# JWT Schema
# ---------------------------
class JWTPayload(BaseModel):
    access_token: str
    user_id: str
    user_type: str
    is_activated: bool
    exp: datetime
    iat: datetime
    

# ---------------------------
# Create Token
# ---------------------------
def create_jwt_token(
    access_token: str,
    user_id: str,
    user_type: str,
    is_activated: bool,
    role:str="member"
) -> str:
    """Generate a secure JWT token with a signed payload."""
    header = {"alg": ALGORITHM}
    
    payload = JWTPayload(
        access_token=access_token,
        user_id=user_id,
        user_type=user_type,
        is_activated=is_activated,
        exp=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        iat=datetime.utcnow(),
    ).model_dump()
    payload["role"]=role
    token = jwt.encode(header, payload, SECRET_KEY)
    return token.decode() if isinstance(token, bytes) else token




async def create_jwt_admin_token(token: str,userId:str):
    return create_jwt_token(access_token=token,user_id=userId,user_type="ADMIN",is_activated=True,role="admin")
 



# ---------------------------
# Decode Token
# ---------------------------
def decode_jwt_token(token: str, allow_expired: bool = False) -> JWTPayload:
    """Decode a JWT token and return a validated JWTPayload object."""
    try:
        claims = jwt.decode(token, SECRET_KEY)
        if not allow_expired:
            claims.validate()  # checks expiration
        return JWTPayload(**claims)
    except JoseError as e:
        raise ValueError(f"Invalid or tampered token: {str(e)}")
    except ValidationError as e:
        raise ValueError(f"Invalid token schema: {str(e)}")
    

async def decode_jwt_token_without_expiration(token: str):
    """Decode a JWT token even if it has expired."""
    return decode_jwt_token(token, allow_expired=True)












