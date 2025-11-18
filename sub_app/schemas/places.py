from pydantic import BaseModel
from typing import Optional

# ---------- AUTOCOMPLETE ----------

class AutocompleteResponse(BaseModel):
    description: str
    name: str
    address: str
    place_id: str
    address: str
    lat: float
    lng: float

# ---------- PLACE DETAILS ----------

class PlaceDetailsResponse(BaseModel):
    name: str
    address: str
    lat: float
    lng: float


# ---------- ERROR MODEL ----------

class ErrorResponse(BaseModel):
    error: str
