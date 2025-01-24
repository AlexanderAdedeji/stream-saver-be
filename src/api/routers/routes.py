from fastapi import APIRouter
from src.api.routers import authentication_routes, download_routes, user_routes
from src.api.routers.stream_savers import stream_savers


router = APIRouter()

router.include_router(
    authentication_routes.router, 
    tags=["Authentication"], 
    prefix="/auth",
    responses={404: {"description": "Not found"}}
)

router.include_router(
    download_routes.router,
    tags=["Download"],
    prefix="/download",
    responses={404: {"description": "Not found"}}
)


router.include_router(
    stream_savers.router,
    tags=["Stream Savers"],
    prefix="/stream-savers",
    responses={404: {"description": "Not found"}}
)
router.include_router(
    user_routes.user_router, 
    tags=["Users"], 
    prefix="/users",
    responses={404: {"description": "Not found"}}
)
