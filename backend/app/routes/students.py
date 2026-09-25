from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response
)

import csv
from io import StringIO

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.student import Student

from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentImportResponse,
    StudentPreviewResponse
)

from app.services.student_import import (
    validate_student_csv,
    import_students
)


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# =========================================================
# CREATE SINGLE STUDENT
# =========================================================

@router.post(
    "/",
    response_model=StudentResponse
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student)
        .filter(
            Student.student_id
            == student.student_id
        )
        .first()
    )

    if existing_student is not None:

        raise HTTPException(
            status_code=409,
            detail=(
                f"Student already exists: "
                f"{student.student_id}"
            )
        )

    new_student = Student(
        student_id=student.student_id,
        name=student.name,
        programme=student.programme,
        year=student.year,
        special_needs=student.special_needs,
        conflict_exams=student.conflict_exams,
        priority_score=student.priority_score
    )

    db.add(new_student)

    db.commit()

    db.refresh(new_student)

    return new_student


# =========================================================
# GET ALL STUDENTS
# =========================================================

@router.get(
    "/",
    response_model=list[StudentResponse]
)
def get_students(
    db: Session = Depends(get_db)
):

    return (
        db.query(Student)
        .order_by(Student.student_id)
        .all()
    )


# =========================================================
# EXPORT STUDENTS TO CSV
# =========================================================

@router.get(
    "/export-csv"
)
def export_students_csv(
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Get students from database
    # -----------------------------------------------------

    students = (
        db.query(Student)
        .order_by(Student.student_id)
        .all()
    )

    # -----------------------------------------------------
    # Create CSV in memory
    # -----------------------------------------------------

    output = StringIO()

    writer = csv.writer(output)

    # -----------------------------------------------------
    # CSV HEADER
    # -----------------------------------------------------

    writer.writerow([
        "student_id",
        "name",
        "programme",
        "year",
        "special_needs",
        "conflict_exams",
        "priority_score"
    ])

    # -----------------------------------------------------
    # WRITE STUDENT DATA
    # -----------------------------------------------------

    for student in students:

        writer.writerow([
            student.student_id,
            student.name,
            student.programme,
            student.year,
            student.special_needs,
            student.conflict_exams or "",
            student.priority_score
        ])

    # -----------------------------------------------------
    # RETURN CSV FILE
    # -----------------------------------------------------

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="students_export.csv"'
            )
        }
    )


# =========================================================
# PREVIEW STUDENTS FROM CSV
# =========================================================

@router.post(
    "/preview-csv",
    response_model=StudentPreviewResponse
)
async def preview_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is missing"
        )

    # -----------------------------------------------------
    # Check extension
    # -----------------------------------------------------

    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    # -----------------------------------------------------
    # Read CSV
    # -----------------------------------------------------

    try:

        file_bytes = await file.read()

        csv_content = file_bytes.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail=(
                "CSV file must use UTF-8 encoding"
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unable to read CSV file: "
                f"{str(exc)}"
            )
        )

    # -----------------------------------------------------
    # Validate CSV
    # -----------------------------------------------------

    result = validate_student_csv(
        csv_content,
        db
    )

    # -----------------------------------------------------
    # Calculate total rows
    # -----------------------------------------------------

    total_rows = (
        len(result.valid_students)
        + len(result.errors)
        + len(result.duplicates)
    )

    # -----------------------------------------------------
    # Convert valid students to response objects
    # -----------------------------------------------------

    preview_students = []

    for student in result.valid_students:

        preview_students.append(
            StudentCreate(
                **student
            )
        )

    # -----------------------------------------------------
    # Determine whether import is allowed
    # -----------------------------------------------------

    can_import = result.is_valid

    # -----------------------------------------------------
    # Return appropriate message
    # -----------------------------------------------------

    if can_import:

        message = (
            "CSV validation successful. "
            "No students were inserted."
        )

    else:

        message = (
            "CSV validation failed. "
            "No students were inserted."
        )

    # -----------------------------------------------------
    # Return preview response
    # -----------------------------------------------------

    return StudentPreviewResponse(
        success=result.is_valid,
        message=message,
        total_rows=total_rows,
        valid_count=len(
            result.valid_students
        ),
        error_count=len(
            result.errors
        ),
        duplicate_count=len(
            result.duplicates
        ),
        can_import=can_import,
        errors=result.errors,
        duplicates=result.duplicates,
        students=preview_students
    )


# =========================================================
# IMPORT STUDENTS FROM CSV
# =========================================================

@router.post(
    "/import-csv",
    response_model=StudentImportResponse
)
async def import_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Check file type
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is missing"
        )

    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    # -----------------------------------------------------
    # Read file
    # -----------------------------------------------------

    try:

        file_bytes = await file.read()

        csv_content = file_bytes.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail=(
                "CSV file must use UTF-8 encoding"
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unable to read CSV file: "
                f"{str(exc)}"
            )
        )

    # -----------------------------------------------------
    # Validate CSV
    # -----------------------------------------------------

    result = validate_student_csv(
        csv_content,
        db
    )

    # -----------------------------------------------------
    # Do NOT insert anything if validation fails
    # -----------------------------------------------------

    if not result.is_valid:

        return StudentImportResponse(
            success=False,
            message=(
                "Student import failed. "
                "No students were inserted."
            ),
            imported_count=0,
            error_count=len(
                result.errors
            ),
            duplicate_count=len(
                result.duplicates
            ),
            errors=result.errors,
            duplicates=result.duplicates
        )

    # -----------------------------------------------------
    # Import validated students
    # -----------------------------------------------------

    try:

        imported_students = import_students(
            db,
            result.valid_students
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to import students: "
                f"{str(exc)}"
            )
        )

    # -----------------------------------------------------
    # Success
    # -----------------------------------------------------

    return StudentImportResponse(
        success=True,
        message=(
            "Students imported successfully"
        ),
        imported_count=len(
            imported_students
        ),
        error_count=0,
        duplicate_count=0,
        errors=[],
        duplicates=[]
    )