from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.exam import ExamSession
from app.schemas.exam import ExamCreate, ExamResponse

import csv
from io import StringIO


router = APIRouter(
    prefix="/exams",
    tags=["Exams"]
)


# ============================================================
# CREATE EXAM SESSION
# ============================================================

@router.post("/", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    db: Session = Depends(get_db)
):
    # Check for duplicate exam ID
    existing = db.query(ExamSession).filter(
        ExamSession.exam_id == exam.exam_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Exam ID already exists"
        )

    new_exam = ExamSession(
        exam_id=exam.exam_id,
        course_code=exam.course_code,
        exam_datetime=exam.exam_datetime,
        duration=exam.duration,
        allowed_rooms=exam.allowed_rooms,
        proctoring_level=exam.proctoring_level
    )

    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    return new_exam


# ============================================================
# GET ALL EXAM SESSIONS
# ============================================================

@router.get("/", response_model=list[ExamResponse])
def get_exams(
    db: Session = Depends(get_db)
):
    return (
        db.query(ExamSession)
        .order_by(ExamSession.exam_datetime)
        .all()
    )


# ============================================================
# EXPORT EXAM SESSIONS TO CSV
# ============================================================

@router.get("/export-csv")
def export_exams_csv(
    db: Session = Depends(get_db)
):
    exams = (
        db.query(ExamSession)
        .order_by(ExamSession.exam_datetime)
        .all()
    )

    output = StringIO()

    writer = csv.writer(output)

    # CSV column headers
    writer.writerow([
        "exam_id",
        "course_code",
        "exam_datetime",
        "duration",
        "allowed_rooms",
        "proctoring_level"
    ])

    # Export actual database records
    for exam in exams:
        writer.writerow([
            exam.exam_id,
            exam.course_code,
            exam.exam_datetime,
            exam.duration,
            exam.allowed_rooms,
            exam.proctoring_level
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="exams_export.csv"'
        }
    )


# ============================================================
# GET SINGLE EXAM SESSION
# ============================================================

@router.get(
    "/{exam_id}",
    response_model=ExamResponse
)
def get_exam(
    exam_id: str,
    db: Session = Depends(get_db)
):
    exam = db.query(ExamSession).filter(
        ExamSession.exam_id == exam_id
    ).first()

    if not exam:
        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    return exam


# ============================================================
# DELETE EXAM SESSION
# ============================================================

@router.delete("/{exam_id}")
def delete_exam(
    exam_id: str,
    db: Session = Depends(get_db)
):
    exam = db.query(ExamSession).filter(
        ExamSession.exam_id == exam_id
    ).first()

    if not exam:
        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    db.delete(exam)
    db.commit()

    return {
        "message": f"Exam deleted: {exam_id}"
    }