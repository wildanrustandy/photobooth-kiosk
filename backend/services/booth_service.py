from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional
import uuid
from models.booth import Booth
from models.device_session import DeviceSession
from schemas.booth import BoothCreate, BoothUpdate, BoothConfigUpdate


class BoothService:
    @staticmethod
    async def get_all_booths(db: AsyncSession) -> List[Booth]:
        """Get all booths."""
        result = await db.execute(select(Booth).order_by(Booth.created_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def get_booth_by_id(db: AsyncSession, booth_id: str) -> Optional[Booth]:
        """Get booth by ID."""
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_booth(db: AsyncSession, booth_data: BoothCreate) -> Booth:
        """Create a new booth."""
        default_config = {
            "price_per_print": 35000,
            "timer_default": 5,
            "max_print": 10,
            "filters": ["normal", "grayscale", "sepia", "vintage", "bright"],
            "payment_timeout": 5,
        }

        booth = Booth(
            name=booth_data.name,
            location=booth_data.location,
            config=booth_data.config if booth_data.config else default_config,
        )

        db.add(booth)
        await db.commit()
        await db.refresh(booth)
        return booth

    @staticmethod
    async def update_booth(
        db: AsyncSession, booth_id: str, booth_data: BoothUpdate
    ) -> Optional[Booth]:
        """Update booth."""
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        booth = result.scalar_one_or_none()

        if not booth:
            return None

        if booth_data.name is not None:
            booth.name = booth_data.name
        if booth_data.location is not None:
            booth.location = booth_data.location
        if booth_data.is_active is not None:
            booth.is_active = booth_data.is_active

        booth.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(booth)
        return booth

    @staticmethod
    async def update_booth_config(
        db: AsyncSession, booth_id: str, config_data: BoothConfigUpdate
    ) -> Optional[Booth]:
        """Update booth configuration."""
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        booth = result.scalar_one_or_none()

        if not booth:
            return None

        current_config = booth.config.copy() if booth.config else {}

        if config_data.price_per_print is not None:
            current_config["price_per_print"] = config_data.price_per_print
        if config_data.timer_default is not None:
            current_config["timer_default"] = config_data.timer_default
        if config_data.max_print is not None:
            current_config["max_print"] = config_data.max_print
        if config_data.filters is not None:
            current_config["filters"] = config_data.filters
        if config_data.payment_timeout is not None:
            current_config["payment_timeout"] = config_data.payment_timeout

        booth.config = current_config
        booth.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(booth)
        return booth

    @staticmethod
    async def assign_device_to_booth(
        db: AsyncSession, booth_id: str, device_id: str
    ) -> Optional[Booth]:
        """Assign a device to a booth."""
        # Check if booth exists
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        booth = result.scalar_one_or_none()

        if not booth:
            return None

        # Check if device exists
        result = await db.execute(
            select(DeviceSession).where(DeviceSession.device_id == device_id)
        )
        device_session = result.scalar_one_or_none()

        if not device_session:
            return None

        # Unassign device from any previous booth
        result = await db.execute(select(Booth).where(Booth.device_id == device_id))
        previous_booth = result.scalar_one_or_none()

        if previous_booth:
            previous_booth.device_id = None
            previous_booth.updated_at = datetime.utcnow()

        # Assign device to booth
        booth.device_id = device_id
        booth.updated_at = datetime.utcnow()

        # Update device session
        device_session.booth_id = booth.id

        await db.commit()
        await db.refresh(booth)
        return booth

    @staticmethod
    async def unassign_device(db: AsyncSession, booth_id: str) -> Optional[Booth]:
        """Unassign device from booth."""
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        booth = result.scalar_one_or_none()

        if not booth:
            return None

        if booth.device_id:
            # Update device session
            result = await db.execute(
                select(DeviceSession).where(DeviceSession.device_id == booth.device_id)
            )
            device_session = result.scalar_one_or_none()

            if device_session:
                device_session.booth_id = None

            booth.device_id = None
            booth.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(booth)

        return booth

    @staticmethod
    async def delete_booth(db: AsyncSession, booth_id: str) -> bool:
        """Delete booth."""
        result = await db.execute(select(Booth).where(Booth.id == uuid.UUID(booth_id)))
        booth = result.scalar_one_or_none()

        if not booth:
            return False

        await db.delete(booth)
        await db.commit()
        return True
