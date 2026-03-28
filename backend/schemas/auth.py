from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceRegisterRequest(BaseModel):
    device_name: Optional[str] = None


class DeviceRegisterResponse(BaseModel):
    device_id: str
    device_token: str
    status: str  # "unassigned" or "assigned"
    booth: Optional[dict] = None


class DeviceHeartbeatResponse(BaseModel):
    active: bool
    booth: Optional[dict] = None
    message: Optional[str] = None


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: dict


class TokenVerifyResponse(BaseModel):
    valid: bool
    device_id: Optional[str] = None
    booth_id: Optional[str] = None
    expires_at: Optional[datetime] = None
