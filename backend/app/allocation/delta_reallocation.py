from dataclasses import dataclass

from app.models.student import Student
from app.models.seat import Seat


@dataclass
class DeltaChange:
    student_id: str
    old_seat_id: str | None
    new_seat_id: str | None
    reason: str


def identify_affected_students(
    allocation: dict,
    changed_student_ids: set[str]
):
    """
    Identify students whose existing allocation
    is affected by a requested change.
    """

    return [
        student_id
        for student_id in allocation.keys()
        if student_id in changed_student_ids
    ]


def collect_available_seats(
    allocation: dict,
    affected_student_ids: set[str],
    all_seats: list[Seat]
):
    """
    Collect seats that can be reused during
    delta reallocation.

    Seats belonging to affected students become
    available again.

    Seats belonging to unaffected students remain
    protected.
    """

    affected_seats = set()

    for student_id in affected_student_ids:
        if student_id in allocation:
            affected_seats.add(
                allocation[student_id]
            )

    available_seats = []

    for seat in all_seats:

        # Seat was previously assigned to an
        # affected student.
        if seat in affected_seats:
            available_seats.append(seat)
            continue

        # Check whether an unaffected student
        # currently occupies this seat.
        occupied_by_unaffected = any(
            allocated_seat is seat
            for student_id, allocated_seat in allocation.items()
            if student_id not in affected_student_ids
        )

        if not occupied_by_unaffected:
            available_seats.append(seat)

    return available_seats


def preserve_unaffected_allocations(
    allocation: dict,
    affected_student_ids: set[str]
):
    """
    Keep all allocations belonging to students
    who are not affected by the change.
    """

    return {
        student_id: seat
        for student_id, seat in allocation.items()
        if student_id not in affected_student_ids
    }


def build_delta_allocation(
    allocation: dict,
    affected_student_ids: set[str],
    replacement_allocation: dict
):
    """
    Build the new allocation by:

    1. Preserving unaffected students.
    2. Removing affected allocations.
    3. Applying replacement allocations.
    """

    result = preserve_unaffected_allocations(
        allocation,
        affected_student_ids
    )

    for student_id, seat in replacement_allocation.items():
        result[student_id] = seat

    return result


def generate_delta_changes(
    old_allocation: dict,
    new_allocation: dict,
    students_by_id: dict[str, Student]
):
    """
    Generate an audit-friendly list of changes
    between the old and new allocation.
    """

    changes = []

    student_ids = (
        set(old_allocation.keys())
        | set(new_allocation.keys())
    )

    for student_id in sorted(student_ids):

        old_seat = old_allocation.get(student_id)
        new_seat = new_allocation.get(student_id)

        old_seat_id = (
            old_seat.seat_id
            if old_seat is not None
            else None
        )

        new_seat_id = (
            new_seat.seat_id
            if new_seat is not None
            else None
        )

        # Nothing changed.
        if old_seat_id == new_seat_id:
            continue

        # New student allocation.
        if old_seat_id is None:
            reason = "new allocation"

        # Student removed from allocation.
        elif new_seat_id is None:
            reason = "allocation removed"

        # Student moved to another seat.
        else:
            reason = "delta reallocation"

        changes.append(
            DeltaChange(
                student_id=student_id,
                old_seat_id=old_seat_id,
                new_seat_id=new_seat_id,
                reason=reason
            )
        )

    return changes