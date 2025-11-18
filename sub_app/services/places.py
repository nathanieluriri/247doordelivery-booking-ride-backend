import httpx
import os
import json
import redis
from dotenv import load_dotenv
from core.redis_cache import cache_db
from schemas.response_schema import APIResponse
from fastapi import HTTPException
import math
load_dotenv()

# Google API setup
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/place"
EARTH_RADIUS_KM = 6371
 

# Cache TTL: 14 days in seconds
CACHE_TTL = 14 * 24 * 60 * 60  # 1209600 seconds


async def get_autocomplete(input_text: str, country: str | None = None):
    """Fetch autocomplete suggestions from cache or Google Places API."""
    cache_key = f"autocomplete:{country or 'any'}:{input_text.lower().strip()}"

    # ✅ Check cache first
    cached_data = cache_db.get(cache_key)
    if cached_data:
        results = json.loads(cached_data)
        return APIResponse(
            data=results,
            detail="Successfully retrieved place data from cache",
            status_code=200
        )

    # 🔍 Not in cache — fetch from Google Places Autocomplete API
    params = {"input": input_text, "key": API_KEY}
    if country:
        params["components"] = f"country:{country}"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/autocomplete/json", params=params)
        data = response.json()

    if data.get("status") != "OK":
        raise HTTPException(
            status_code=500,
            detail={"error": data.get("error_message", data.get("status"))}
        )

    predictions = data.get("predictions", [])
    results = []

    # 🔍 Get details for each place to enrich with lat/lng, name, etc.
    async with httpx.AsyncClient() as client:
        for p in predictions:
            place_id = p["place_id"]

            # Fetch details for each autocomplete result
            details_params = {"place_id": place_id, "key": API_KEY}
            details_response = await client.get(f"{BASE_URL}/details/json", params=details_params)
            details_data = details_response.json()

            if details_data.get("status") != "OK":
                continue

            result = details_data.get("result", {})

            enriched_place = {
                "place_id": place_id,
                "description": p["description"],
                "name": result.get("name", p.get("structured_formatting", {}).get("main_text")),
                "address": result.get("formatted_address", p["description"]),
                "lat": result.get("geometry", {}).get("location", {}).get("lat"),
                "lng": result.get("geometry", {}).get("location", {}).get("lng"),
                "types": result.get("types", []),
                "rating": result.get("rating"),
                "user_ratings_total": result.get("user_ratings_total"),
                "icon": result.get("icon"),
            }
            results.append(enriched_place)

    # 💾 Store in Redis (cache enriched results)
    cache_db.setex(cache_key, CACHE_TTL, json.dumps(results))

    return APIResponse(
        data=results,
        detail="Successfully retrieved place data",
        status_code=200
    )


async def get_place_details(place_id: str):
    """Fetch detailed place info from cache or Google Places API."""
    cache_key = f"place_details:{place_id}"

    # ✅ Check cache first
    cached_data = cache_db.get(cache_key)
    if cached_data:
        result_data = json.loads(cached_data)
        return APIResponse(
            data=result_data,
            detail="Successfully retrieved place data from cache",
            status_code=200
        )

    # 🔍 Not in cache — fetch from Google
    params = {"place_id": place_id, "key": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/details/json", params=params)
        data = response.json()

    if data.get("status") != "OK":
        raise HTTPException(
            status_code=500,
            detail={"error": data.get("error_message", data.get("status"))}
        )

    result = data.get("result", {})

    result_data = {
        "place_id": place_id,
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "lat": result.get("geometry", {}).get("location", {}).get("lat"),
        "lng": result.get("geometry", {}).get("location", {}).get("lng"),
        "phone_number": result.get("formatted_phone_number"),
        "website": result.get("website"),
        "types": result.get("types", []),
        "rating": result.get("rating"),
        "user_ratings_total": result.get("user_ratings_total"),
        "icon": result.get("icon"),
        "opening_hours": result.get("opening_hours", {}).get("weekday_text"),
    }

    # 💾 Cache result
    cache_db.setex(cache_key, CACHE_TTL, json.dumps(result_data))

    return APIResponse(
        data=result_data,
        detail="Successfully retrieved place data",
        status_code=200
    )



async def get_place_details(place_id: str):
    """Fetch detailed place info from cache or Google Places API."""
    cache_key = f"place_details:{place_id}"

    # ✅ Check cache first
    cached_data = cache_db.get(cache_key)
    if cached_data:
        result_data= json.loads(cached_data)
        response = APIResponse(data=result_data,detail="Successfully retrieved place data from cache",status_code=200)
        return response

    # 🔍 Not in cache — fetch from Google
    params = {"place_id": place_id, "key": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/details/json", params=params)
        data = response.json()

    if data.get("status") != "OK":
        raise HTTPException(status_code=500,detail={"error": data.get("error_message", data.get("status"))}) 

    result = data.get("result",None)
    print(result)
     
    result_data = {
        "name": result.get("name",None),
        "address": result.get("formatted_address",None),
        "lat": result.get('geometry', {}).get('location', {}).get('lat'),
        "lng": result.get('geometry', {}).get('location', {}).get('lng'),
    }
    

    # 💾 Store in Redis
    cache_db.setex(cache_key, CACHE_TTL, json.dumps(result_data))
    response = APIResponse(data=result_data,detail="Successfully retrieved place data",status_code=200)
    return result_data


 


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two coordinates in kilometers."""
    # Convert degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


async def get_place_lat_lng(place_id: str) -> tuple[float, float]:
    """Fetch latitude and longitude for a place_id from cache or Google API."""
    cache_key = f"place_coords:{place_id}"

    # ✅ Check cache first
    cached_data = cache_db.get(cache_key)
    if cached_data:
        coords = json.loads(cached_data)
        return coords["lat"], coords["lng"]

    # 🔍 Fetch from Google Places API
    params = {"place_id": place_id, "key": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/details/json", params=params)
        data = response.json()

    if data.get("status") != "OK":
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve place details for {place_id}: {data.get('status')}"
        )

    result = data.get("result", {})
    lat = result.get("geometry", {}).get("location", {}).get("lat")
    lng = result.get("geometry", {}).get("location", {}).get("lng")

    if lat is None or lng is None:
        raise HTTPException(status_code=404, detail=f"Coordinates not found for place_id {place_id}")

    # 💾 Cache coordinates
    cache_db.setex(cache_key, CACHE_TTL, json.dumps({"lat": lat, "lng": lng}))
    return lat, lng


async def get_distance_between_places(place_id_1: str, place_id_2: str):
    """Calculate the distance (in km) between two Google Place IDs."""
    cache_key = f"distance:{place_id_1}:{place_id_2}"

    # ✅ Check cache first
    cached_data = cache_db.get(cache_key)
    if cached_data:
        data = json.loads(cached_data)
        return APIResponse(
            data=data,
            detail="Successfully retrieved distance from cache",
            status_code=200
        )

    # 🔍 Fetch coordinates for both places
    lat1, lon1 = await get_place_lat_lng(place_id_1)
    lat2, lon2 = await get_place_lat_lng(place_id_2)

    # 📏 Calculate distance
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)

    result = {
        "from_place_id": place_id_1,
        "to_place_id": place_id_2,
        "distance_km": round(distance_km, 3),
        "distance_miles": round(distance_km * 0.621371, 3)
    }

    # 💾 Cache result
    cache_db.setex(cache_key, CACHE_TTL, json.dumps(result))

    return APIResponse(
        data=result,
        detail="Successfully calculated distance",
        status_code=200
    )
