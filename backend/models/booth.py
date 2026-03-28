from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base


class Booth(Base):
    __tablename__ = "booths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    location = Column(String(255), nullable=True)
    device_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    current_session_id = Column(UUID(as_uuid=True), nullable=True)
    config = Column(
        JSON,
        default=lambda: {
            "price_per_print": 35000,
            "timer_default": 5,
            "max_print": 10,
            "filters": ["normal", "grayscale", "sepia", "vintage", "bright"],
        },
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)

    # Relationships
    device_sessions = relationship(
        "DeviceSession", back_populates="booth", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="booth", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Booth {self.name}>"
