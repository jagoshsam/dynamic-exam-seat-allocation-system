from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExamCreate(BaseModel):
    exam_id: str = Field(min_length=1)
    course_code: str = Field(min_length=1)
    exam_datetime: datetime
    duration: int = Field(gt=0)
    allowed_rooms: str = Field(min_length=1)
    proctoring_level: str = Field(min_length=1)


class ExamResponse(ExamCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)