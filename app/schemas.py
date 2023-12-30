from pydantic import BaseModel, EmailStr, conint, FileUrl
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, File
# a class on how our post should look like
# our schema
# we use the basemodel to model what our schema look like,
# just like we modelled our tables from models.py


class ItemBase(BaseModel):
    name: str
    description: str
    price: int
    # image: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class OrderBase(BaseModel):
    id: int


class CustomerBase(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime


class OrderOut(BaseModel):
    orderitem_id: int
    order_id: int
    item_id: int
    item_name: str
    item_image: str
    quantity: int
    total_price: int
    order_date: datetime

    class Config:
        orm_mode = True


class HistoryOut(BaseModel):
    cu_history: str
    created_at: str

    class Config:
        orm_mode = True


class History(BaseModel):
    data: str

# schema for profle response


class Profile(CustomerBase):
    customer_id: int
    phone_number: int
    city: str
    region: str

    class Config:
        orm_mode = True

# view customer full profile


class CustomerOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: int
    city: str
    region: str
    created_at: datetime

    class Config:
        orm_mode = True


class UnverifiedCustomers(BaseModel):
    id: int
    is_verified: bool


# view admin profile
class AdminOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# response after creating a customer


class Response(BaseModel):
    status: str
    data: str

    class Config:
        orm_mode = True


class _Response(BaseModel):
    status: str
    data: str
    history: str

    class Config:
        orm_mode = True


class CodeResponse(BaseModel):
    status: str
    data: str
    code: str
    id: int

    class Config:
        orm_mode = True


class ResendResponse(BaseModel):
    status: str
    data: str
    code: str
    email: EmailStr

    class Config:
        orm_mode = True


class Item(ItemBase):
    id: int
    image: str
    admin_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# schema for customer profile


class ProfileCreate(BaseModel):
    phone_number: int
    city: str
    region: str


class AdminCreate(BaseModel):
    username: str
    email: EmailStr  # ensures the email is valid
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordEdit(BaseModel):
    password: str


class OrderCreate(BaseModel):
    pass


class EmailCheck(BaseModel):
    email: EmailStr


class CodeCheck(BaseModel):
    code: str


class IdCheck(BaseModel):
    id: int

# schema for customer


class CustomerCreate(BaseModel):
    username: str
    email: EmailStr  # ensures the email is valid
    password: str


class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

# schema for the token


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):  # schema for tokendata
    id: Optional[str] = None
