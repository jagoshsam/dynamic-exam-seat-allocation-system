from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.seat import Seat


class HardConstraintViolation(Exception):
    """Raised when a required constrained placement is impossible."""
    pass


def is_constrained(student: Student) -> bool:
    """
    A student is constrained when they have:
    - special accessibility requirements, or
    - exam conflicts recorded.
    """

    has_special_needs = bool(student.special_needs)
    has_conflicts = bool(student.conflict_exams)

    return has_special_needs or has_conflicts


def sort_constrained_students(students):
    """
    Deterministic ordering.

    Higher priority first, followed by stable
    programme and student ID ordering.
    """

    constrained = [
        student
        for student in students
        if is_constrained(student)
    ]

    constrained.sort(
        key=lambda student: (
            -(student.priority_score or 0),
            student.programme,
            student.student_id
        )
    )

    return constrained


def select_seat_for_constrained(
    student: Student,
    available_seats: list[Seat]
):
    """
    Select a suitable seat deterministically.

    Students with special needs require an
    accessibility seat.

    Selection:
        1. lowest room ID
        2. lowest seat label
    """

    suitable_seats = available_seats

    if student.special_needs:
        suitable_seats = [
            seat
            for seat in available_seats
            if seat.accessibility_flag
        ]

    suitable_seats = sorted(
        suitable_seats,
        key=lambda seat: (
            seat.room_id,
            seat.label
        )
    )

    if not suitable_seats:
        raise HardConstraintViolation(
            f"No suitable seat available for student "
            f"{student.student_id}"
        )

    return suitable_seats[0]


def place_constrained_students(
    students: list[Student],
    available_seats: list[Seat]
):
    """
    Stage 1:
    Place constrained students before normal students.
    """

    constrained_students = sort_constrained_students(students)

    allocation = {}

    remaining_seats = list(available_seats)

    for student in constrained_students:

        seat = select_seat_for_constrained(
            student,
            remaining_seats
        )

        allocation[student.student_id] = seat

        remaining_seats.remove(seat)

        seat.occupied_flag = True

    return allocation, remaining_seats