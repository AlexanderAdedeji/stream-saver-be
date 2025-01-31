from fastapi import APIRouter
from slowapi.util import get_remote_address
from slowapi import Limiter
from src.commonLib.utils.logger_config import logger

# Import API routers
from src.api.routers import (
    authentication_routes,
    facebook_routes,
    youtube_routes,
    user_routes,
    instagram_routes,
)


router = APIRouter()

# Initialize Limiter (for rate-limiting)
limiter = Limiter(key_func=get_remote_address)

# List of all routers for dynamic inclusion
api_routes = [
    {"router": authentication_routes.router, "prefix": "/auth", "tag": "Authentication"},
    {"router": youtube_routes.router, "prefix": "/youtube", "tag": "YouTube"},
    {"router": instagram_routes.router, "prefix": "/instagram", "tag": "Instagram"},
    {"router": user_routes.user_router, "prefix": "/users", "tag": "Users"},
    {"router": facebook_routes.router, "prefix": "/facebook", "tag": "Facebook"},
]

# Dynamically register routers
for route in api_routes:
    router.include_router(
        route["router"],
        prefix=route["prefix"],
        tags=[route["tag"]],
        responses={404: {"description": "Not found"}},
    )
    logger.info(f" Registered route: {route['prefix']} under {route['tag']}")


@router.get("/health-check")
@limiter.limit("5/minute") 
async def health_check():
    return {"status": "OK"}
