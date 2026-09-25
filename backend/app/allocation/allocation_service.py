from sqlalchemy.orm import Session

from app.models.exam import ExamSession
from app.models.student import Student

from app.allocation.preprocessor import AllocationPreprocessor

from app.allocation.constrained_placement import (
    place_constrained_students,
)

from app.allocation.seeded_placement import (
    seeded_initial_placement,
)

from app.allocation.local_optimization import (
    local_optimize,
)

from app.allocation.delta_reallocation import (
    identify_affected_students,
    collect_available_seats,
    build_delta_allocation,
    generate_delta_changes,
)

from app.allocation.allocation_repository import (
    save_allocation,
    update_allocation_records,
    create_audit_log,
)


class AllocationService:

    def __init__(self, db: Session):
        self.db = db
        self.preprocessor = AllocationPreprocessor(db)

    # =========================================================
    # STAGE 0 - PREPROCESSING
    # =========================================================

    def prepare_allocation(
        self,
        exam: ExamSession,
        students: list[Student]
    ):
        """
        Stage 0:
        Prepare and validate allocation inputs.
        """

        return self.preprocessor.preprocess(
            exam,
            students
        )

    # =========================================================
    # STAGE 1 - CONSTRAINED PLACEMENT
    # =========================================================

    def constrained_placement(
        self,
        students: list[Student],
        available_seats
    ):
        """
        Stage 1:
        Place constrained students first.
        """

        return place_constrained_students(
            students,
            available_seats
        )

    # =========================================================
    # STAGE 2 - SEEDED INITIAL PLACEMENT
    # =========================================================

    def seeded_placement(
        self,
        students: list[Student],
        available_seats,
        seed: int
    ):
        """
        Stage 2:
        Perform deterministic seeded
        round-robin placement.
        """

        return seeded_initial_placement(
            students,
            available_seats,
            seed
        )

    # =========================================================
    # STAGE 3 - LOCAL OPTIMIZATION
    # =========================================================

    def optimize(
        self,
        allocation,
        students: list[Student],
        max_iterations: int = 100
    ):
        """
        Stage 3:
        Improve the allocation using
        bounded local optimization.
        """

        students_by_id = {
            student.student_id: student
            for student in students
        }

        return local_optimize(
            allocation,
            students_by_id,
            max_iterations
        )

    # =========================================================
    # STAGE 4 - DELTA REALLOCATION
    # =========================================================

    def delta_reallocate(
        self,
        allocation,
        students: list[Student],
        all_seats,
        changed_student_ids: set[str],
        replacement_allocation: dict
    ):
        """
        Stage 4:
        Reallocate only affected students
        while preserving unaffected allocations.
        """

        affected_students = set(
            identify_affected_students(
                allocation,
                changed_student_ids
            )
        )

        available_seats = collect_available_seats(
            allocation,
            affected_students,
            all_seats
        )

        new_allocation = build_delta_allocation(
            allocation,
            affected_students,
            replacement_allocation
        )

        students_by_id = {
            student.student_id: student
            for student in students
        }

        changes = generate_delta_changes(
            allocation,
            new_allocation,
            students_by_id
        )

        return {
            "allocation": new_allocation,
            "available_seats": available_seats,
            "affected_students": affected_students,
            "changes": changes
        }

    # =========================================================
    # PERSIST FINAL ALLOCATION
    # =========================================================

    def save_final_allocation(
        self,
        exam: ExamSession,
        allocation,
        students: list[Student],
        seed: int,
        assigned_by: str = "system",
        reason: str = "initial allocation"
    ):
        """
        Save the final allocation into the database
        and create an audit log entry.
        """

        records = save_allocation(
            self.db,
            exam,
            allocation,
            students,
            seed,
            assigned_by,
            reason
        )

        create_audit_log(
            self.db,
            action="CREATE_ALLOCATION",
            entity=f"exam:{exam.exam_id}",
            user=assigned_by,
            diff=(
                f"Created {len(records)} "
                f"allocation records"
            )
        )

        return records

    # =========================================================
    # PERSIST DELTA REALLOCATION
    # =========================================================

    def save_delta_reallocation(
        self,
        exam: ExamSession,
        changes,
        students: list[Student],
        all_seats,
        seed: int,
        user: str = "system"
    ):
        """
        Persist Stage 4 delta-reallocation changes.

        The database AllocationRecord table is updated
        to reflect the new seat assignments.

        Every actual change also receives an audit entry.
        """

        seat_lookup = {
            seat.seat_id: seat
            for seat in all_seats
        }

        records = update_allocation_records(
            self.db,
            exam,
            changes,
            students,
            seat_lookup,
            seed,
            user
        )

        for change in changes:

            diff = (
                f"student={change.student_id}; "
                f"old_seat={change.old_seat_id}; "
                f"new_seat={change.new_seat_id}; "
                f"reason={change.reason}"
            )

            create_audit_log(
                self.db,
                action="DELTA_REALLOCATION",
                entity=f"exam:{exam.exam_id}",
                user=user,
                diff=diff
            )

        return records

    # =========================================================
    # RECORD DELTA CHANGES ONLY
    # =========================================================

    def record_delta_changes(
        self,
        exam: ExamSession,
        changes,
        user: str = "system"
    ):
        """
        Create audit log entries for Stage 4
        delta reallocation changes.

        This method records audit information only.
        It does not modify AllocationRecord rows.
        """

        for change in changes:

            diff = (
                f"student={change.student_id}; "
                f"old_seat={change.old_seat_id}; "
                f"new_seat={change.new_seat_id}; "
                f"reason={change.reason}"
            )

            create_audit_log(
                self.db,
                action="DELTA_REALLOCATION",
                entity=f"exam:{exam.exam_id}",
                user=user,
                diff=diff
            )

        return changes