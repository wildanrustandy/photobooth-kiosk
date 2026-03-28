from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionResponse(BaseModel):
    id: str
    session_id: str
    reference_id: Optional[str] = None
    booth_id: str
    booth_name: str
    amount: float
    print_count: int
    status: str
    payment_method: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class TransactionFilter(BaseModel):
    booth_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
