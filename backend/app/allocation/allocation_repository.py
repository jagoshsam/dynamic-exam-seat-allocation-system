from sqlalchemy.orm import Session

from app.models.allocation import AllocationRecord
from app.models.audit import AuditLog


def save_allocation(
    db: Session,
    exam,
    allocation: dict,
    students: list,
    seed: int,
    assigned_by: str = "system",
    reason: str = "initial allocation"
):
    """
    Save the final seating allocation into
    the AllocationRecord table.
    """

    students_by_student_id = {
        student.student_id: student
        for student in students
    }

    records = []

    for student_id, seat in allocation.items():

        student = students_by_student_id.get(student_id)

        if student is None:
            raise ValueError(
                f"Student not found: {student_id}"
            )

        if student.id is None:
            raise ValueError(
                f"Student database ID is missing: {student_id}"
            )

        if seat.id is None:
            raise ValueError(
                f"Seat database ID is missing: {seat.seat_id}"
            )

        if exam.id is None:
            raise ValueError(
                f"Exam database ID is missing: {exam.exam_id}"
            )

        record = AllocationRecord(
            exam_id=exam.id,
            student_id=student.id,
            seat_id=seat.id,
            seed=seed,
            assigned_by=assigned_by,
            reason=reason
        )

        db.add(record)
        records.append(record)

    db.commit()

    for record in records:
        db.refresh(record)

    return records


def update_allocation_records(
    db: Session,
    exam,
    changes,
    students: list,
    seat_lookup: dict,
    seed: int,
    assigned_by: str = "system"
):
    """
    Persist Stage 4 delta-reallocation changes.

    Existing AllocationRecord rows are updated when a student
    changes seats.

    If a student receives a completely new allocation, a new
    AllocationRecord is created.

    If an allocation is removed, the existing record is deleted.
    """

    if exam.id is None:
        raise ValueError(
            f"Exam database ID is missing: {exam.exam_id}"
        )

    students_by_student_id = {
        student.student_id: student
        for student in students
    }

    records = []

    for change in changes:

        student = students_by_student_id.get(
            change.student_id
        )

        if student is None:
            raise ValueError(
                f"Student not found: {change.student_id}"
            )

        if student.id is None:
            raise ValueError(
                f"Student database ID is missing: "
                f"{change.student_id}"
            )

        # -----------------------------------------------------
        # Find the existing allocation record
        # -----------------------------------------------------

        record = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id,
                AllocationRecord.student_id == student.id
            )
            .first()
        )

        # -----------------------------------------------------
        # CASE 1
        # Student receives a new seat
        # -----------------------------------------------------

        if change.old_seat_id is None:

            if change.new_seat_id is None:
                continue

            new_seat = seat_lookup.get(
                change.new_seat_id
            )

            if new_seat is None:
                raise ValueError(
                    f"Seat not found: "
                    f"{change.new_seat_id}"
                )

            if new_seat.id is None:
                raise ValueError(
                    f"Seat database ID is missing: "
                    f"{change.new_seat_id}"
                )

            new_record = AllocationRecord(
                exam_id=exam.id,
                student_id=student.id,
                seat_id=new_seat.id,
                seed=seed,
                assigned_by=assigned_by,
                reason="delta reallocation"
            )

            db.add(new_record)
            records.append(new_record)

        # -----------------------------------------------------
        # CASE 2
        # Student's allocation is removed
        # -----------------------------------------------------

        elif change.new_seat_id is None:

            if record is not None:
                db.delete(record)

        # -----------------------------------------------------
        # CASE 3
        # Student changes from one seat to another
        # -----------------------------------------------------

        else:

            new_seat = seat_lookup.get(
                change.new_seat_id
            )

            if new_seat is None:
                raise ValueError(
                    f"Seat not found: "
                    f"{change.new_seat_id}"
                )

            if new_seat.id is None:
                raise ValueError(
                    f"Seat database ID is missing: "
                    f"{change.new_seat_id}"
                )

            if record is None:
                raise ValueError(
                    f"Existing allocation record not found "
                    f"for student: {change.student_id}"
                )

            record.seat_id = new_seat.id
            record.seed = seed
            record.assigned_by = assigned_by
            record.reason = "delta reallocation"

            records.append(record)

    db.commit()

    for record in records:
        db.refresh(record)

    return records


def create_audit_log(
    db: Session,
    action: str,
    entity: str,
    user: str,
    diff: str | None = None
):
    """
    Create an audit entry describing
    an allocation action.
    """

    audit = AuditLog(
        action=action,
        entity=entity,
        user=user,
        diff=diff
    )

    db.add(audit)

    db.commit()

    db.refresh(audit)

    return audit