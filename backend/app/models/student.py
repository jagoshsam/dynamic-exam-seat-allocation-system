from sqlalchemy import Column, Integer, String, Boolean, Text

from app.database.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    programme = Column(
        String,
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )

    special_needs = Column(
        Boolean,
        default=False
    )

    conflict_exams = Column(
        Text,
        nullable=True
    )

    priority_score = Column(
        Integer,
        default=0
    )