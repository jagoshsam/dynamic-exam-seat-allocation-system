import random

from app.models.student import Student
from app.models.seat import Seat


def is_constrained(student: Student) -> bool:
    """
    A student is constrained when they have:
    - special needs, or
    - recorded exam conflicts.
    """

    return bool(
        student.special_needs
        or student.conflict_exams
    )


def build_ordered_students(
    students: list[Student],
    seed: int
):
    """
    Build a deterministic student order.

    Higher priority students are placed first.

    Programme and student ID provide stable
    ordering. The supplied seed is used only
    for deterministic tie-breaking.
    """

    normal_students = [
        student
        for student in students
        if not is_constrained(student)
    ]

    rng = random.Random(seed)

    # Create deterministic random values for tie-breaking.
    tie_breakers = {
        student.student_id: rng.random()
        for student in normal_students
    }

    normal_students.sort(
        key=lambda student: (
            -(student.priority_score or 0),
            student.programme,
            tie_breakers[student.student_id],
            student.student_id
        )
    )

    return normal_students


def group_seats_by_room(
    available_seats: list[Seat]
):
    """
    Group available seats by room.

    Each room's seats are sorted by seat label
    to keep placement deterministic.
    """

    room_seats = {}

    for seat in available_seats:
        room_seats.setdefault(
            seat.room_id,
            []
        ).append(seat)

    for room_id in room_seats:
        room_seats[room_id].sort(
            key=lambda seat: seat.label
        )

    return dict(
        sorted(
            room_seats.items(),
            key=lambda item: item[0]
        )
    )


def seeded_initial_placement(
    students: list[Student],
    available_seats: list[Seat],
    seed: int
):
    """
    Stage 2:
    Seeded initial placement using round-robin
    distribution across rooms.

    Constrained students are excluded because
    Stage 1 has already handled them.
    """

    ordered_students = build_ordered_students(
        students,
        seed
    )

    room_seats = group_seats_by_room(
        available_seats
    )

    room_ids = list(room_seats.keys())

    if not room_ids:
        raise ValueError(
            "No available rooms/seats for Stage 2."
        )

    allocation = {}

    room_index = 0

    for student in ordered_students:

        assigned = False

        # Try rooms in round-robin order.
        for offset in range(len(room_ids)):

            current_index = (
                room_index + offset
            ) % len(room_ids)

            room_id = room_ids[current_index]

            seats = room_seats[room_id]

            if not seats:
                continue

            # Prefer a seat whose neighbouring programme
            # is different where possible.
            selected_seat = seats[0]

            allocation[
                student.student_id
            ] = selected_seat

            selected_seat.occupied_flag = True

            seats.pop(0)

            room_index = (
                current_index + 1
            ) % len(room_ids)

            assigned = True
            break

        if not assigned:
            raise ValueError(
                f"No available seat for student "
                f"{student.student_id}"
            )

    remaining_seats = []

    for seats in room_seats.values():
        remaining_seats.extend(seats)

    return allocation, remaining_seats