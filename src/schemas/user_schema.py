from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
from src.schemas.user_type_schema import UserTypeInDB


class UserBase(BaseModel):
    first_name: str
    last_name: str


class UserCreateForm(UserBase):
    email: EmailStr
    password: str


class UserCreate(UserCreateForm):
    user_type_id: str


class UserUpdate(UserBase):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    password: Optional[str] = None


class UserInLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None,


class UserWithToken(UserBase):
    email: EmailStr
    # user_type: UserTypeInDB       ##UnComment this when the user type is implemented
    token: str


class UserInResponse(UserBase):
    id: str
    is_active: bool
    email: EmailStr
    # user_type: UserTypeInDB       ##UnComment this when the user type is implemented
    verify_token: Optional[str] =None


class AllUsers(UserInResponse):

    date_created: datetime


class UserVerify(BaseModel):
    token: str


class ResetPasswordSchema(BaseModel):
    token: str
    password: str

