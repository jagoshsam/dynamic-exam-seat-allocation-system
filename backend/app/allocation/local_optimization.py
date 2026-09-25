from collections import Counter

from app.models.student import Student
from app.models.seat import Seat


def seat_distance(seat_a: Seat, seat_b: Seat) -> int:
    """
    Manhattan distance between two seats.

    Used to determine whether two seats are adjacent
    or close to each other.
    """

    if seat_a.room_id != seat_b.room_id:
        return 999999

    return (
        abs(seat_a.x_coordinate - seat_b.x_coordinate)
        + abs(seat_a.y_coordinate - seat_b.y_coordinate)
    )


def are_adjacent(seat_a: Seat, seat_b: Seat) -> bool:
    """
    Two seats are considered adjacent when their
    Manhattan distance is 1.
    """

    return seat_distance(seat_a, seat_b) == 1


def violates_hard_constraints(
    allocation: dict,
    students_by_id: dict
) -> bool:
    """
    Check hard constraints that are currently
    represented in our allocation engine.

    Current check:
    - A student with special needs must remain
      in an accessibility seat.
    """

    for student_id, seat in allocation.items():

        student = students_by_id[student_id]

        if student.special_needs:
            if not seat.accessibility_flag:
                return True

    return False


def calculate_adjacency_penalty(
    allocation: dict,
    students_by_id: dict
) -> int:
    """
    Penalize adjacent students belonging to the
    same programme.
    """

    items = list(allocation.items())

    penalty = 0

    for i in range(len(items)):

        student_id_a, seat_a = items[i]
        student_a = students_by_id[student_id_a]

        for j in range(i + 1, len(items)):

            student_id_b, seat_b = items[j]
            student_b = students_by_id[student_id_b]

            if student_a.programme != student_b.programme:
                continue

            if are_adjacent(seat_a, seat_b):
                penalty += 1

    return penalty


def calculate_room_balance_score(
    allocation: dict
) -> float:
    """
    Reward balanced use of rooms.

    A perfectly balanced allocation receives
    a higher score than a heavily concentrated one.
    """

    if not allocation:
        return 0.0

    room_counts = Counter(
        seat.room_id
        for seat in allocation.values()
    )

    values = list(room_counts.values())

    average = sum(values) / len(values)

    deviation = sum(
        abs(value - average)
        for value in values
    )

    return 1.0 / (1.0 + deviation)


def calculate_programme_dispersion_score(
    allocation: dict,
    students_by_id: dict
) -> float:
    """
    Reward spreading programmes across rooms.
    """

    programme_rooms = {}

    for student_id, seat in allocation.items():

        student = students_by_id[student_id]

        programme_rooms.setdefault(
            student.programme,
            set()
        )

        programme_rooms[
            student.programme
        ].add(seat.room_id)

    if not programme_rooms:
        return 0.0

    total_rooms = sum(
        len(rooms)
        for rooms in programme_rooms.values()
    )

    return total_rooms / len(programme_rooms)


def score_allocation(
    allocation: dict,
    students_by_id: dict
) -> float:
    """
    Calculate the overall soft-constraint score.

    Higher score = better allocation.

    Current metrics:
    - programme dispersion
    - adjacency penalty
    - room utilization balance
    """

    dispersion = calculate_programme_dispersion_score(
        allocation,
        students_by_id
    )

    adjacency_penalty = calculate_adjacency_penalty(
        allocation,
        students_by_id
    )

    room_balance = calculate_room_balance_score(
        allocation
    )

    return (
        (dispersion * 1.0)
        + (room_balance * 1.0)
        - (adjacency_penalty * 1.0)
    )


def propose_swap(
    allocation: dict,
    student_id_a: str,
    student_id_b: str
):
    """
    Create a candidate allocation by swapping
    the seats of two students.
    """

    candidate = allocation.copy()

    seat_a = candidate[student_id_a]
    seat_b = candidate[student_id_b]

    candidate[student_id_a] = seat_b
    candidate[student_id_b] = seat_a

    return candidate


def local_optimize(
    allocation: dict,
    students_by_id: dict,
    max_iterations: int = 100
):
    """
    Stage 3:
    Bounded local optimization using student-seat swaps.

    A candidate is accepted only when:
    1. It does not violate hard constraints.
    2. Its score is better than the current allocation.
    """

    if not allocation:
        return allocation

    best = allocation.copy()

    best_score = score_allocation(
        best,
        students_by_id
    )

    student_ids = list(best.keys())

    for _ in range(max_iterations):

        improved = False

        for i in range(len(student_ids)):

            for j in range(i + 1, len(student_ids)):

                student_a = student_ids[i]
                student_b = student_ids[j]

                candidate = propose_swap(
                    best,
                    student_a,
                    student_b
                )

                if violates_hard_constraints(
                    candidate,
                    students_by_id
                ):
                    continue

                candidate_score = score_allocation(
                    candidate,
                    students_by_id
                )

                if candidate_score > best_score:

                    best = candidate
                    best_score = candidate_score

                    improved = True
                    break

            if improved:
                break

        if not improved:
            break

    return best