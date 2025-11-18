from fastapi import Depends, FastAPI
from repositories.tokens_repo import get_access_tokens_no_date_check
from security.auth import verify_any_token
from security.encrypting_jwt import decode_jwt_token
from sub_app.api.places import router as google_places_router
import os
import time
import math
import redis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from limits import parse
from limits.storage import RedisStorage
from limits.strategies import FixedWindowRateLimiter
from typing import Tuple
from schemas.response_schema import APIResponse

# Redis config
redis_url = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") \
    or f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/0"

redis_client = redis.from_url(redis_url, decode_responses=True)

# Setup rate limiter
storage = RedisStorage(redis_url)
limiter = FixedWindowRateLimiter(storage)

RATE_LIMITS = {
    "annonymous": parse("20/minute"),
    "member": parse("60/minute"),
    "admin": parse("140/minute"),
}

# IP-based abuse threshold (e.g., 200 req/min hard block)
IP_BLOCK_THRESHOLD = parse("200/minute")
IP_BLOCK_DURATION = 60 * 60 * 24 * 14  # 14 days (in seconds)


async def get_user_type(request: Request) -> Tuple[str, str]:
    """
    Extract user identity (user_id) and type (role)
    Fallback to IP address for anonymous users.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        ip_address = request.headers.get("X-Forwarded-For", request.client.host)
        return ip_address, "annonymous"

    try:
        token = auth_header.split(" ")[1]
        decoded_token = decode_jwt_token(token=token, allow_expired=False)
        access_token = await get_access_tokens_no_date_check(accessToken=decoded_token.access_token)
        user_id = access_token.userId
        user_type = access_token.role or "annonymous"
        return user_id, user_type if user_type in RATE_LIMITS else "annonymous"
    except Exception:
        ip_address = request.headers.get("X-Forwarded-For", request.client.host)
        return ip_address, "annonymous"


class RateLimitingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # --- Step 1: Extract IP ---
        ip_address = request.headers.get("X-Forwarded-For", request.client.host)

        # --- Step 2: Check if IP is blocked ---
        if redis_client.sismember("blocked_ips", ip_address):
            return JSONResponse(
                status_code=403,
                content=APIResponse(
                    status_code=403,
                    detail="Your IP has been temporarily blocked due to excessive requests.",
                    data={"ip": ip_address},
                ).dict(),
            )

        # --- Step 3: Get user identity and type ---
        user_id, user_type = await get_user_type(request)
        rate_limit_rule = RATE_LIMITS[user_type]

        # --- Step 4: Apply normal rate limit ---
        allowed = limiter.hit(rate_limit_rule, user_id)
        reset_time, remaining = limiter.get_window_stats(rate_limit_rule, user_id)
        seconds_until_reset = max(math.ceil(reset_time - time.time()), 0)

        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={
                    "X-User-Id": user_id,
                    "X-User-Type": user_type,
                    "X-RateLimit-Limit": str(rate_limit_rule.amount),
                    "X-RateLimit-Remaining": str(max(remaining, 0)),
                    "X-RateLimit-Reset": str(seconds_until_reset),
                    "Retry-After": str(seconds_until_reset),
                },
                content=APIResponse(
                    status_code=429,
                    detail="Too Many Requests",
                    data={
                        "retry_after_seconds": seconds_until_reset,
                        "user_type": user_type,
                        "ip": ip_address,
                    },
                ).dict(),
            )

        # --- Step 5: Apply IP-level hard abuse detection ---
        ip_allowed = limiter.hit(IP_BLOCK_THRESHOLD, ip_address)
        if not ip_allowed:
            # Add to Redis blocked list for 14 days
            redis_client.sadd("blocked_ips", ip_address)
            redis_client.expire("blocked_ips", IP_BLOCK_DURATION)
            return JSONResponse(
                status_code=403,
                content=APIResponse(
                    status_code=403,
                    detail="IP temporarily blocked for excessive activity.",
                    data={"ip": ip_address, "block_duration_sec": IP_BLOCK_DURATION},
                ).dict(),
            )

        # --- Step 6: Continue normal flow ---
        response = await call_next(request)

        # Add headers to successful responses too
        response.headers["X-User-Id"] = user_id
        response.headers["X-User-Type"] = user_type
        response.headers["X-RateLimit-Limit"] = str(rate_limit_rule.amount)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Reset"] = str(seconds_until_reset)
        response.headers["X-IP"] = ip_address

        return response

app = FastAPI(title="Google Places API with Redis Cache For 247 Door Delivery",dependencies=[Depends(verify_any_token)])
app.add_middleware(RateLimitingMiddleware)
# Include routes
app.include_router(google_places_router, prefix="/places", tags=["Google Places"])
