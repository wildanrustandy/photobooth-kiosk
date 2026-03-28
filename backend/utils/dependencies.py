from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.device_session import DeviceSession
from models.admin_user import AdminUser
from utils.security import verify_device_token, verify_admin_token

security = HTTPBearer()


async def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Dependency to extract device info from JWT token."""
    token = credentials.credentials
    payload = verify_device_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired device token",
        )

    # Check if device session is still active
    result = await db.execute(
        select(DeviceSession).where(DeviceSession.device_id == payload["device_id"])
    )
    device_session = result.scalar_one_or_none()

    if not device_session or not device_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device session is not active",
        )

    return {
        "device_id": payload["device_id"],
        "booth_id": payload.get("booth_id"),
        "device_session": device_session,
    }


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Dependency to extract admin info from JWT token."""
    token = credentials.credentials
    payload = verify_admin_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
        )

    # Check if admin exists and is active
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == payload["admin_id"])
    )
    admin = result.scalar_one_or_none()

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account is not active",
        )

    return {
        "admin_id": payload["admin_id"],
        "username": payload["username"],
        "role": payload["role"],
    }
