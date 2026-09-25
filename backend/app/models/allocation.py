from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class AllocationRecord(Base):
    __tablename__ = "allocation_records"

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(
        Integer,
        ForeignKey("exam_sessions.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    seat_id = Column(
        Integer,
        ForeignKey("seats.id"),
        nullable=False
    )

    seed = Column(Integer, nullable=False)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    assigned_by = Column(String, nullable=False)
    reason = Column(String, nullable=True)

    exam = relationship("ExamSession")
    student = relationship("Student")
    seat = relationship("Seat")