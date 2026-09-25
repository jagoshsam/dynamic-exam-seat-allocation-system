from app.allocation.local_optimization import (
    seat_distance,
    are_adjacent,
    violates_hard_constraints,
    calculate_adjacency_penalty,
    calculate_room_balance_score,
    calculate_programme_dispersion_score,
    score_allocation,
    propose_swap,
    local_optimize,
)

from app.models.student import Student
from app.models.seat import Seat


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_student(
    student_id,
    programme="MSc AI",
    priority_score=0,
    special_needs=False,
):
    return Student(
        student_id=student_id,
        name=f"Student {student_id}",
        programme=programme,
        year=1,
        priority_score=priority_score,
        special_needs=special_needs,
        conflict_exams=None,
    )


def make_seat(
    seat_id,
    room_id,
    label,
    x,
    y,
    accessibility_flag=False,
):
    return Seat(
        seat_id=seat_id,
        label=label,
        x_coordinate=x,
        y_coordinate=y,
        accessibility_flag=accessibility_flag,
        occupied_flag=False,
        room_id=room_id,
    )


# ============================================================
# TEST 1
# SEAT DISTANCE
# ============================================================

def test_seat_distance():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    assert seat_distance(seat_a, seat_b) == 1


# ============================================================
# TEST 2
# SEATS IN DIFFERENT ROOMS
# ============================================================

def test_seat_distance_different_rooms():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R2-A1",
        room_id=2,
        label="A1",
        x=1,
        y=1,
    )

    assert seat_distance(seat_a, seat_b) == 999999


# ============================================================
# TEST 3
# ADJACENT SEATS
# ============================================================

def test_are_adjacent():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    assert are_adjacent(seat_a, seat_b) is True


# ============================================================
# TEST 4
# NON-ADJACENT SEATS
# ============================================================

def test_are_not_adjacent():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-B3",
        room_id=1,
        label="B3",
        x=3,
        y=2,
    )

    assert are_adjacent(seat_a, seat_b) is False


# ============================================================
# TEST 5
# SPECIAL NEEDS STUDENT MUST USE
# ACCESSIBILITY SEAT
# ============================================================

def test_special_needs_hard_constraint():

    student = make_student(
        "STU001",
        special_needs=True,
    )

    students_by_id = {
        "STU001": student
    }

    normal_seat = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
        accessibility_flag=False,
    )

    allocation = {
        "STU001": normal_seat
    }

    assert violates_hard_constraints(
        allocation,
        students_by_id,
    ) is True


# ============================================================
# TEST 6
# VALID ACCESSIBILITY SEAT
# ============================================================

def test_accessibility_constraint_is_valid():

    student = make_student(
        "STU001",
        special_needs=True,
    )

    students_by_id = {
        "STU001": student
    }

    accessible_seat = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
        accessibility_flag=True,
    )

    allocation = {
        "STU001": accessible_seat
    }

    assert violates_hard_constraints(
        allocation,
        students_by_id,
    ) is False


# ============================================================
# TEST 7
# SAME PROGRAMME ADJACENCY
# ============================================================

def test_same_programme_adjacency_penalty():

    student_a = make_student(
        "STU001",
        programme="MSc AI",
    )

    student_b = make_student(
        "STU002",
        programme="MSc AI",
    )

    students_by_id = {
        "STU001": student_a,
        "STU002": student_b,
    }

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    penalty = calculate_adjacency_penalty(
        allocation,
        students_by_id,
    )

    assert penalty == 1


# ============================================================
# TEST 8
# DIFFERENT PROGRAMMES HAVE NO
# SAME-PROGRAMME ADJACENCY PENALTY
# ============================================================

def test_different_programmes_no_adjacency_penalty():

    student_a = make_student(
        "STU001",
        programme="MSc AI",
    )

    student_b = make_student(
        "STU002",
        programme="MSc DS",
    )

    students_by_id = {
        "STU001": student_a,
        "STU002": student_b,
    }

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    penalty = calculate_adjacency_penalty(
        allocation,
        students_by_id,
    )

    assert penalty == 0


# ============================================================
# TEST 9
# ROOM BALANCE SCORE
# ============================================================

def test_room_balance_score():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R2-A1",
        room_id=2,
        label="A1",
        x=1,
        y=1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    score = calculate_room_balance_score(
        allocation
    )

    assert score == 1.0


# ============================================================
# TEST 10
# EMPTY ALLOCATION ROOM BALANCE
# ============================================================

def test_empty_room_balance_score():

    score = calculate_room_balance_score({})

    assert score == 0.0


# ============================================================
# TEST 11
# PROGRAMME DISPERSION
# ============================================================

def test_programme_dispersion_score():

    student_a = make_student(
        "STU001",
        programme="MSc AI",
    )

    student_b = make_student(
        "STU002",
        programme="MSc AI",
    )

    students_by_id = {
        "STU001": student_a,
        "STU002": student_b,
    }

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R2-A1",
        room_id=2,
        label="A1",
        x=1,
        y=1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    score = calculate_programme_dispersion_score(
        allocation,
        students_by_id,
    )

    assert score == 2.0


# ============================================================
# TEST 12
# SWAP TWO STUDENTS
# ============================================================

def test_propose_swap():

    student_a_seat = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    student_b_seat = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    allocation = {
        "STU001": student_a_seat,
        "STU002": student_b_seat,
    }

    candidate = propose_swap(
        allocation,
        "STU001",
        "STU002",
    )

    assert candidate["STU001"].seat_id == "R1-A2"
    assert candidate["STU002"].seat_id == "R1-A1"


# ============================================================
# TEST 13
# ORIGINAL ALLOCATION MUST NOT CHANGE
# ============================================================

def test_propose_swap_does_not_modify_original():

    seat_a = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
    )

    seat_b = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    candidate = propose_swap(
        allocation,
        "STU001",
        "STU002",
    )

    assert allocation["STU001"].seat_id == "R1-A1"
    assert allocation["STU002"].seat_id == "R1-A2"

    assert candidate["STU001"].seat_id == "R1-A2"
    assert candidate["STU002"].seat_id == "R1-A1"


# ============================================================
# TEST 14
# SCORE EMPTY ALLOCATION
# ============================================================

def test_score_empty_allocation():

    score = score_allocation(
        {},
        {},
    )

    assert score == 0.0


# ============================================================
# TEST 15
# LOCAL OPTIMIZATION RETURNS VALID ALLOCATION
# ============================================================

def test_local_optimize_returns_valid_allocation():

    students = [
        make_student(
            "STU001",
            programme="MSc AI",
        ),
        make_student(
            "STU002",
            programme="MSc AI",
        ),
        make_student(
            "STU003",
            programme="MSc DS",
        ),
        make_student(
            "STU004",
            programme="MSc DS",
        ),
    ]

    students_by_id = {
        student.student_id: student
        for student in students
    }

    seats = [
        make_seat(
            "R1-A1",
            room_id=1,
            label="A1",
            x=1,
            y=1,
        ),
        make_seat(
            "R1-A2",
            room_id=1,
            label="A2",
            x=2,
            y=1,
        ),
        make_seat(
            "R2-A1",
            room_id=2,
            label="A1",
            x=1,
            y=1,
        ),
        make_seat(
            "R2-A2",
            room_id=2,
            label="A2",
            x=2,
            y=1,
        ),
    ]

    allocation = {
        "STU001": seats[0],
        "STU002": seats[1],
        "STU003": seats[2],
        "STU004": seats[3],
    }

    optimized = local_optimize(
        allocation,
        students_by_id,
        max_iterations=100,
    )

    assert len(optimized) == 4

    assigned_seat_ids = [
        seat.seat_id
        for seat in optimized.values()
    ]

    assert len(set(assigned_seat_ids)) == 4


# ============================================================
# TEST 16
# LOCAL OPTIMIZATION PRESERVES
# HARD CONSTRAINTS
# ============================================================

def test_local_optimize_preserves_hard_constraints():

    special_student = make_student(
        "STU001",
        programme="MSc AI",
        special_needs=True,
    )

    normal_student = make_student(
        "STU002",
        programme="MSc AI",
    )

    students_by_id = {
        "STU001": special_student,
        "STU002": normal_student,
    }

    accessible_seat = make_seat(
        "R1-A1",
        room_id=1,
        label="A1",
        x=1,
        y=1,
        accessibility_flag=True,
    )

    normal_seat = make_seat(
        "R1-A2",
        room_id=1,
        label="A2",
        x=2,
        y=1,
        accessibility_flag=False,
    )

    allocation = {
        "STU001": accessible_seat,
        "STU002": normal_seat,
    }

    optimized = local_optimize(
        allocation,
        students_by_id,
        max_iterations=100,
    )

    assert (
        optimized["STU001"].accessibility_flag
        is True
    )

    assert violates_hard_constraints(
        optimized,
        students_by_id,
    ) is False