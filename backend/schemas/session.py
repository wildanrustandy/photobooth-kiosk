from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SessionCreate(BaseModel):
    print_count: int = 1
    filter: str = "normal"
    timer: int = 5


class SessionResponse(BaseModel):
    id: str
    booth_id: str
    device_id: str
    status: str
    print_count: int
    total_price: Optional[Decimal] = None
    filter: str
    timer: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    status: Optional[str] = None
    print_count: Optional[int] = None
    total_price: Optional[Decimal] = None
    filter: Optional[str] = None
    timer: Optional[int] = None
