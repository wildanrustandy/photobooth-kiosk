from schemas.auth import (
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceHeartbeatResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    TokenVerifyResponse,
)
from schemas.booth import (
    BoothCreate,
    BoothUpdate,
    BoothResponse,
    BoothAssignDevice,
    BoothConfigUpdate,
)
from schemas.session import SessionCreate, SessionResponse, SessionUpdate

__all__ = [
    # Auth
    "DeviceRegisterRequest",
    "DeviceRegisterResponse",
    "DeviceHeartbeatResponse",
    "AdminLoginRequest",
    "AdminLoginResponse",
    "TokenVerifyResponse",
    # Booth
    "BoothCreate",
    "BoothUpdate",
    "BoothResponse",
    "BoothAssignDevice",
    "BoothConfigUpdate",
    # Session
    "SessionCreate",
    "SessionResponse",
    "SessionUpdate",
]
