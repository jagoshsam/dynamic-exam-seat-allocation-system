from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    student_id: str
    name: str
    programme: str
    year: int
    special_needs: bool = False
    conflict_exams: str | None = None
    priority_score: int = 0


class StudentResponse(StudentCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class StudentImportResponse(BaseModel):
    success: bool
    message: str
    imported_count: int
    error_count: int
    duplicate_count: int
    errors: list[str]
    duplicates: list[str]


class StudentPreviewResponse(BaseModel):
    success: bool
    message: str
    total_rows: int
    valid_count: int
    error_count: int
    duplicate_count: int
    can_import: bool
    errors: list[str]
    duplicates: list[str]
    students: list[StudentCreate]