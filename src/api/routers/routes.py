from fastapi import APIRouter
from src.api.routers import authentication_routes, user_routes


router = APIRouter()

router.include_router(
    authentication_routes.router, 
    tags=["Authentication"], 
    prefix="/auth",
    responses={404: {"description": "Not found"}}
)



router.include_router(
    user_routes.user_router, 
    tags=["Users"], 
    prefix="/users",
    responses={404: {"description": "Not found"}}
)
