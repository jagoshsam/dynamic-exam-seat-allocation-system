from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.exam import ExamSession
from app.models.student import Student
from app.models.seat import Seat
from app.models.allocation import AllocationRecord

from app.allocation.allocation_pipeline import AllocationPipeline
from app.allocation.allocation_service import AllocationService

from app.schemas.allocation import (
    AllocationRunRequest,
    AllocationRunResponse,
    AllocationItemResponse,
    SavedAllocationResponse,
)


router = APIRouter(
    prefix="/allocations",
    tags=["Allocations"]
)


# =========================================================
# DELTA REALLOCATION REQUEST
# =========================================================

class DeltaReallocationRequest(BaseModel):
    student_id: str = Field(
        min_length=1,
        description="Student whose seat should be changed"
    )

    new_seat_id: str = Field(
        min_length=1,
        description="Replacement seat ID"
    )

    seed: int = Field(
        default=42,
        description="Deterministic reallocation seed"
    )

    assigned_by: str = Field(
        default="system",
        min_length=1,
        description="User performing the reallocation"
    )


# =========================================================
# RUN ALLOCATION
# =========================================================

@router.post(
    "/run/{exam_id}",
    response_model=AllocationRunResponse
)
def run_allocation(
    exam_id: str,
    request: AllocationRunRequest,
    db: Session = Depends(get_db)
):
    """
    Run the complete allocation pipeline.

    Stages:
    0. Preprocessing
    1. Constrained placement
    2. Seeded placement
    3. Local optimization

    The final allocation is persisted
    and an audit log is created.
    """

    # =====================================================
    # 1. FIND EXAM
    # =====================================================

    exam = (
        db.query(ExamSession)
        .filter(
            ExamSession.exam_id == exam_id
        )
        .first()
    )

    if exam is None:
        raise HTTPException(
            status_code=404,
            detail=f"Exam not found: {exam_id}"
        )

    # =====================================================
    # 2. FIND STUDENTS
    # =====================================================

    students = (
        db.query(Student)
        .filter(
            Student.student_id.in_(
                request.student_ids
            )
        )
        .all()
    )

    # =====================================================
    # 3. VERIFY STUDENTS
    # =====================================================

    found_student_ids = {
        student.student_id
        for student in students
    }

    missing_student_ids = [
        student_id
        for student_id in request.student_ids
        if student_id not in found_student_ids
    ]

    if missing_student_ids:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Some students were not found",
                "missing_student_ids": missing_student_ids
            }
        )

    # =====================================================
    # 4. CHECK FOR EXISTING ALLOCATION
    # =====================================================

    existing_allocation = (
        db.query(AllocationRecord)
        .filter(
            AllocationRecord.exam_id == exam.id
        )
        .first()
    )

    if existing_allocation is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Allocation already exists for exam: "
                f"{exam_id}. "
                f"Use delta reallocation for changes."
            )
        )

    # =====================================================
    # 5. RUN ALLOCATION PIPELINE
    # =====================================================

    try:

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=request.seed,
            max_iterations=request.max_iterations
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Allocation failed: {str(exc)}"
        )

    allocation = result["allocation"]

    # =====================================================
    # 6. SAVE FINAL ALLOCATION
    # =====================================================

    try:

        service = AllocationService(db)

        service.save_final_allocation(
            exam=exam,
            allocation=allocation,
            students=students,
            seed=request.seed,
            assigned_by=request.assigned_by,
            reason="initial allocation"
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save allocation: {str(exc)}"
        )

    # =====================================================
    # 7. BUILD RESPONSE
    # =====================================================

    students_by_id = {
        student.student_id: student
        for student in students
    }

    response_items = []

    for student_id, seat in allocation.items():

        student = students_by_id.get(student_id)

        if student is None:
            continue

        response_items.append(
            AllocationItemResponse(
                student_id=student.student_id,
                student_name=student.name,
                seat_id=seat.seat_id,
                seat_label=seat.label,
                room_id=seat.room.room_id
            )
        )

    # =====================================================
    # 8. RETURN RESULT
    # =====================================================

    return AllocationRunResponse(
        exam_id=exam.exam_id,
        seed=request.seed,
        allocation_count=len(response_items),
        allocations=response_items
    )


# =========================================================
# GET SAVED ALLOCATION
# =========================================================

@router.get(
    "/{exam_id}",
    response_model=SavedAllocationResponse
)
def get_allocation(
    exam_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve the saved allocation for an examination.
    """

    # =====================================================
    # 1. FIND EXAM
    # =====================================================

    exam = (
        db.query(ExamSession)
        .filter(
            ExamSession.exam_id == exam_id
        )
        .first()
    )

    if exam is None:
        raise HTTPException(
            status_code=404,
            detail=f"Exam not found: {exam_id}"
        )

    # =====================================================
    # 2. GET ALLOCATION RECORDS
    # =====================================================

    records = (
        db.query(AllocationRecord)
        .filter(
            AllocationRecord.exam_id == exam.id
        )
        .all()
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No allocation found for exam: {exam_id}"
        )

    # =====================================================
    # 3. BUILD RESPONSE
    # =====================================================

    response_items = []

    for record in records:

        student = record.student
        seat = record.seat

        response_items.append(
            AllocationItemResponse(
                student_id=student.student_id,
                student_name=student.name,
                seat_id=seat.seat_id,
                seat_label=seat.label,
                room_id=seat.room.room_id
            )
        )

    # =====================================================
    # 4. RETURN SAVED ALLOCATION
    # =====================================================

    return SavedAllocationResponse(
        exam_id=exam.exam_id,
        allocation_count=len(response_items),
        allocations=response_items
    )


# =========================================================
# DELTA REALLOCATION
# =========================================================

@router.post(
    "/delta/{exam_id}"
)
def delta_reallocation(
    exam_id: str,
    request: DeltaReallocationRequest,
    db: Session = Depends(get_db)
):
    """
    Perform a minimal-delta seat reallocation.

    Only the affected student and any students required
    by the delta allocation logic are changed.

    The resulting changes are persisted and recorded
    in the audit log.
    """

    # =====================================================
    # 1. FIND EXAM
    # =====================================================

    exam = (
        db.query(ExamSession)
        .filter(
            ExamSession.exam_id == exam_id
        )
        .first()
    )

    if exam is None:
        raise HTTPException(
            status_code=404,
            detail=f"Exam not found: {exam_id}"
        )

    # =====================================================
    # 2. GET EXISTING ALLOCATION
    # =====================================================

    records = (
        db.query(AllocationRecord)
        .filter(
            AllocationRecord.exam_id == exam.id
        )
        .all()
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No allocation found for exam: {exam_id}"
        )

    # =====================================================
    # 3. FIND REQUESTED STUDENT
    # =====================================================

    student = (
        db.query(Student)
        .filter(
            Student.student_id == request.student_id
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail=f"Student not found: {request.student_id}"
        )

    # =====================================================
    # 4. BUILD CURRENT ALLOCATION
    # =====================================================

    allocation = {}

    for record in records:

        if record.student is None:
            continue

        if record.seat is None:
            continue

        allocation[
            record.student.student_id
        ] = record.seat

    # =====================================================
    # 5. VERIFY STUDENT HAS AN ALLOCATION
    # =====================================================

    if request.student_id not in allocation:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Student {request.student_id} "
                f"does not have an allocation for exam: {exam_id}"
            )
        )

    old_seat = allocation[
        request.student_id
    ]

    # =====================================================
    # 6. FIND NEW SEAT
    # =====================================================

    new_seat = (
        db.query(Seat)
        .filter(
            Seat.seat_id == request.new_seat_id
        )
        .first()
    )

    if new_seat is None:
        raise HTTPException(
            status_code=404,
            detail=f"Seat not found: {request.new_seat_id}"
        )

    # =====================================================
    # 7. CHECK SAME SEAT
    # =====================================================

    if old_seat.seat_id == new_seat.seat_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Student {request.student_id} "
                f"is already assigned to seat {request.new_seat_id}"
            )
        )

    # =====================================================
    # 8. CHECK SEAT IS NOT ALREADY ALLOCATED
    # =====================================================

    occupied_by = None

    for student_id, seat in allocation.items():

        if seat.seat_id == new_seat.seat_id:
            occupied_by = student_id
            break

    if occupied_by is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Replacement seat is already allocated",
                "seat_id": request.new_seat_id,
                "allocated_to": occupied_by
            }
        )

    # =====================================================
    # 9. GET ALL SEATS
    # =====================================================

    all_seats = (
        db.query(Seat)
        .order_by(Seat.id)
        .all()
    )

    # =====================================================
    # 10. BUILD REPLACEMENT ALLOCATION
    # =====================================================

    replacement_allocation = {
        request.student_id: new_seat
    }

    changed_student_ids = [
        request.student_id
    ]

    # =====================================================
    # 11. RUN DELTA ALLOCATION
    # =====================================================

    try:

        service = AllocationService(db)

        result = service.delta_reallocate(
            allocation=allocation,
            students=(
                db.query(Student)
                .filter(
                    Student.student_id.in_(
                        allocation.keys()
                    )
                )
                .all()
            ),
            all_seats=all_seats,
            changed_student_ids=changed_student_ids,
            replacement_allocation=replacement_allocation
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Delta reallocation failed: {str(exc)}"
        )

    # =====================================================
    # 12. GET GENERATED CHANGES
    # =====================================================

    changes = result["changes"]

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="No allocation changes were generated."
        )

    # =====================================================
    # 13. PERSIST DELTA CHANGES
    # =====================================================

    try:

        service.save_delta_reallocation(
            exam=exam,
            changes=changes,
            students=(
                db.query(Student)
                .filter(
                    Student.student_id.in_(
                        allocation.keys()
                    )
                )
                .all()
            ),
            all_seats=all_seats,
            seed=request.seed,
            user=request.assigned_by
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save delta reallocation: "
                f"{str(exc)}"
            )
        )

    # =====================================================
    # 14. BUILD RESPONSE
    # =====================================================

    response_changes = []

    for change in changes:

        response_changes.append(
            {
                "student_id": change.student_id,
                "old_seat_id": change.old_seat_id,
                "new_seat_id": change.new_seat_id,
                "reason": change.reason
            }
        )

    # =====================================================
    # 15. RETURN RESULT
    # =====================================================

    return {
        "success": True,
        "exam_id": exam.exam_id,
        "seed": request.seed,
        "changed_count": len(response_changes),
        "changes": response_changes
    }