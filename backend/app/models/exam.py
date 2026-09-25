from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database.database import Base


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(String, unique=True, nullable=False, index=True)
    course_code = Column(String, nullable=False)

    exam_datetime = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)

    allowed_rooms = Column(Text, nullable=False)

    proctoring_level = Column(String, nullable=False)