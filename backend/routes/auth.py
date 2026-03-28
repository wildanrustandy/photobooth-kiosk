from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.auth import (
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceHeartbeatResponse,
    AdminLoginRequest,
    AdminLoginResponse,
)
from services.auth_service import AuthService
from utils.security import verify_device_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/device/register", response_model=DeviceRegisterResponse)
async def register_device(
    request: DeviceRegisterRequest = None, db: AsyncSession = Depends(get_db)
):
    """
    Register a new device and return device credentials.
    If device_name is provided, it will be stored for identification.
    """
    device_name = request.device_name if request else None
    result = await AuthService.register_device(db, device_name)
    return result


@router.get("/device/assignment")
async def check_assignment(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if device is assigned to a booth.
    Returns booth info if assigned, null otherwise.
    """
    token = credentials.credentials
    payload = verify_device_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired device token",
        )

    device_id = payload.get("device_id")
    result = await AuthService.check_assignment(db, device_id)
    return result


@router.post("/device/heartbeat", response_model=DeviceHeartbeatResponse)
async def device_heartbeat(
    device_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Update device heartbeat and check if still active.
    This endpoint should be called periodically by the kiosk client.
    """
    result = await AuthService.heartbeat(db, device_id)
    return result


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate admin user and return JWT token.
    """
    result = await AuthService.admin_login(db, request.username, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return result
