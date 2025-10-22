# ============================================================================
#DRIVER SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-10-21 00:17:46 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time
from security.hash import hash_password

class DriverBase(BaseModel):
    # Add other fields here 
    email:EmailStr
    password:str | bytes
    pass

class DriverCreate(DriverBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    @model_validator(mode='after')
    def obscure_password(self):
        self.password=hash_password(self.password)
        return self
class DriverUpdate(BaseModel):
    # Add other fields here
    isActive: Optional[bool]=None
    isProfileComplete:Optional[bool]=None
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class DriverOut(DriverBase):
    # Add other fields here 
    id: Optional[str] =None
    isActive: Optional[bool]=Field(default=False)
    isProfileComplete:Optional[bool]=Field(default=False)
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    refresh_token: Optional[str] =None
    access_token:Optional[str]=None
    @model_validator(mode='before')
    def set_dynamic_values(cls,values):
        values['id']= str(values.get('_id'))
        return values
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        
        
class DriverRefresh(BaseModel):
    # Add other fields here 
    refresh_token:str
    pass
