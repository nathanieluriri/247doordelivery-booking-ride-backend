# ============================================================================
#FARE SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-10-23 01:59:11 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time
from schemas.vehicle import VehicleBase
class FareBase(BaseModel):
    # Add other fields here
    vehicle:VehicleBase
    pricing_variable:int = Field(description="should be in a percentage it takes the percentage of the total and then it adds it to the price for each fare")
     
    pass

class FareCreate(FareBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class FareUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class FareOut(FareBase):
    # Add other fields here 
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    
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