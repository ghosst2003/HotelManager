from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., max_length=100)
    role: str = Field(..., pattern="^(employee|finance|admin)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Orders ---

class OrderItemCreate(BaseModel):
    date: date
    room_count: int = 1
    cost_price: Decimal = Decimal("0")
    sale_price: Decimal = Decimal("0")
    salesperson: Optional[str] = None
    confirmation_number: Optional[str] = None
    remarks: Optional[str] = None


class OrderCreate(BaseModel):
    order_platform: str
    order_number: str
    room_name: str
    guest_name: str
    hotel_name: str
    guest_count: int = 1
    booking_date: date
    confirmation_number: Optional[str] = None
    order_status: str = "未处理"
    other_remarks: Optional[str] = None
    items: list[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    order_platform: Optional[str] = None
    order_number: Optional[str] = None
    room_name: Optional[str] = None
    guest_name: Optional[str] = None
    hotel_name: Optional[str] = None
    guest_count: Optional[int] = None
    booking_date: Optional[date] = None
    confirmation_number: Optional[str] = None
    order_status: Optional[str] = None
    other_remarks: Optional[str] = None
    salesperson: Optional[str] = None
    items: Optional[list[OrderItemCreate]] = None


class OrderItemResponse(OrderItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gross_profit: Decimal
    profit_margin: Decimal
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_platform: str
    order_number: str
    room_name: str
    guest_name: str
    salesperson: str
    hotel_name: str
    guest_count: int
    booking_date: date
    confirmation_number: Optional[str]
    order_status: str
    other_remarks: Optional[str]
    created_by: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []


# --- Pagination ---

class PageResponse(BaseModel, extra="allow"):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total: int
    page: int
    page_size: int
    items: list


# --- Logs ---

class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
