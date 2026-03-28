from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from models.device_session import DeviceSession
from models.booth import Booth
from models.admin_user import AdminUser
from utils.security import (
    generate_device_id,
    generate_device_token,
    create_device_jwt,
    create_admin_jwt,
    verify_password,
)


class AuthService:
    @staticmethod
    async def register_device(db: AsyncSession, device_name: str = None) -> dict:
        """Register a new device and return device credentials."""
        device_id = generate_device_id()
        device_token = generate_device_token()

        # Create device session
        device_session = DeviceSession(
            device_id=device_id,
            device_name=device_name,
            session_token=device_token,
            is_active=True,
        )

        db.add(device_session)
        await db.commit()
        await db.refresh(device_session)

        # Check if device is assigned to a booth
        result = await db.execute(select(Booth).where(Booth.device_id == device_id))
        booth = result.scalar_one_or_none()

        # Create JWT token
        jwt_token = create_device_jwt(
            device_id=device_id, booth_id=str(booth.id) if booth else None
        )

        return {
            "device_id": device_id,
            "device_token": jwt_token,
            "status": "assigned" if booth else "unassigned",
            "booth": {
                "id": str(booth.id),
                "name": booth.name,
                "location": booth.location,
                "config": booth.config,
            }
            if booth
            else None,
        }

    @staticmethod
    async def heartbeat(db: AsyncSession, device_id: str) -> dict:
        """Update device heartbeat and check if still active."""
        result = await db.execute(
            select(DeviceSession).where(DeviceSession.device_id == device_id)
        )
        device_session = result.scalar_one_or_none()

        if not device_session:
            return {"active": False, "message": "Device not found"}

        if not device_session.is_active:
            return {"active": False, "message": "Device session is not active"}

        # Update heartbeat
        device_session.last_heartbeat = datetime.utcnow()
        await db.commit()

        # Get booth info if assigned
        booth = None
        if device_session.booth_id:
            result = await db.execute(
                select(Booth).where(Booth.id == device_session.booth_id)
            )
            booth = result.scalar_one_or_none()

        return {
            "active": True,
            "booth": {
                "id": str(booth.id),
                "name": booth.name,
                "location": booth.location,
                "config": booth.config,
            }
            if booth
            else None,
        }

    @staticmethod
    async def admin_login(
        db: AsyncSession, username: str, password: str
    ) -> dict | None:
        """Authenticate admin user and return JWT token."""
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            return None

        if not verify_password(password, admin.password_hash):
            return None

        if not admin.is_active:
            return None

        # Update last login
        admin.last_login = datetime.utcnow()
        await db.commit()

        # Create JWT token
        jwt_token = create_admin_jwt(
            admin_id=str(admin.id), username=admin.username, role=admin.role
        )

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours
            "admin": {
                "id": str(admin.id),
                "username": admin.username,
                "role": admin.role,
            },
        }

    @staticmethod
    async def kick_device(db: AsyncSession, device_id: str) -> bool:
        """Deactivate a device session (kick from booth)."""
        result = await db.execute(
            select(DeviceSession).where(DeviceSession.device_id == device_id)
        )
        device_session = result.scalar_one_or_none()

        if device_session:
            device_session.is_active = False
            await db.commit()
            return True

        return False
