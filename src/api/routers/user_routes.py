from fastapi import APIRouter



user_router = APIRouter()

@user_router.get("/users")
async def get_users():
    return {"message": "Hello World"}

