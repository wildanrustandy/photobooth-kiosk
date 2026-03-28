from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base


class DeviceSession(Base):
    __tablename__ = "device_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booth_id = Column(
        UUID(as_uuid=True), ForeignKey("booths.id", ondelete="CASCADE"), nullable=True
    )
    device_id = Column(String(255), unique=True, nullable=False)
    device_name = Column(String(255), nullable=True)
    session_token = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booth = relationship("Booth", back_populates="device_sessions")

    def __repr__(self):
        return f"<DeviceSession {self.device_id}>"
