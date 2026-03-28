from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class BoothCreate(BaseModel):
    name: str
    location: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class BoothUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class BoothConfigUpdate(BaseModel):
    price_per_print: Optional[int] = None
    timer_default: Optional[int] = None
    max_print: Optional[int] = None
    filters: Optional[list] = None
    payment_timeout: Optional[int] = None  # Payment timeout in minutes (3 or 5)


class BoothAssignDevice(BaseModel):
    device_id: str


class BoothResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    device_id: Optional[str] = None
    is_active: bool
    config: Dict[str, Any]
    created_at: datetime
    last_active_at: Optional[datetime] = None
    current_session_id: Optional[str] = None

    class Config:
        from_attributes = True
