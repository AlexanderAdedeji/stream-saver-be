from fastapi import APIRouter
from src.api.routers import authentication_routes, facebook_routes, youtube_routes, user_routes
from src.api.routers import instagram_routes


router = APIRouter()

router.include_router(
    authentication_routes.router, 
    tags=["Authentication"], 
    prefix="/auth",
    responses={404: {"description": "Not found"}}
)

router.include_router(
    youtube_routes.router,
    tags=["youtube"],
    prefix="/youtube",
    responses={404: {"description": "Not found"}}
)


router.include_router(
    instagram_routes.router,
    tags=["Instagram"],
    prefix="/instagram",
    responses={404: {"description": "Not found"}}
)
router.include_router(
    user_routes.user_router, 
    tags=["Users"], 
    prefix="/users",
    responses={404: {"description": "Not found"}}
)


router.include_router(
    facebook_routes.router, 
    tags=["Facebook"], 
    prefix="/facebook",
    responses={404: {"description": "Not found"}}
)
