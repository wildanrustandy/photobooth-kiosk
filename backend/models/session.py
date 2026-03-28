from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booth_id = Column(
        UUID(as_uuid=True), ForeignKey("booths.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(String(255), nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, paid, completed, cancelled
    print_count = Column(Integer, default=1)
    total_price = Column(Numeric(10, 2), nullable=True)
    filter = Column(String(50), default="normal")
    timer = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    booth = relationship("Booth", back_populates="sessions")
    payment = relationship(
        "Payment", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    photos = relationship(
        "Photo", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Session {self.id}>"
