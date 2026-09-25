from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    user = Column(String, nullable=False)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    diff = Column(Text, nullable=True)