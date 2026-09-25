from app.allocation.seeded_placement import (
    is_constrained,
    build_ordered_students,
    group_seats_by_room,
    seeded_initial_placement,
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
    conflict_exams=None,
):
    return Student(
        student_id=student_id,
        name=f"Student {student_id}",
        programme=programme,
        year=1,
        priority_score=priority_score,
        special_needs=special_needs,
        conflict_exams=conflict_exams,
    )


def make_seat(
    seat_id,
    room_id,
    label,
):
    return Seat(
        seat_id=seat_id,
        label=label,
        x_coordinate=1,
        y_coordinate=1,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room_id,
    )


# ============================================================
# TEST 1
# NORMAL STUDENT IS NOT CONSTRAINED
# ============================================================

def test_normal_student_is_not_constrained():

    student = make_student(
        "STU001"
    )

    assert is_constrained(student) is False


# ============================================================
# TEST 2
# SPECIAL NEEDS STUDENT IS CONSTRAINED
# ============================================================

def test_special_needs_student_is_constrained():

    student = make_student(
        "STU001",
        special_needs=True
    )

    assert is_constrained(student) is True


# ============================================================
# TEST 3
# CONFLICT STUDENT IS CONSTRAINED
# ============================================================

def test_conflict_student_is_constrained():

    student = make_student(
        "STU001",
        conflict_exams="EXAM-002"
    )

    assert is_constrained(student) is True


# ============================================================
# TEST 4
# SEEDED ORDER IS DETERMINISTIC
# ============================================================

def test_seeded_order_is_deterministic():

    students_one = [
        make_student("STU001"),
        make_student("STU002"),
        make_student("STU003"),
        make_student("STU004"),
    ]

    students_two = [
        make_student("STU001"),
        make_student("STU002"),
        make_student("STU003"),
        make_student("STU004"),
    ]

    order_one = build_ordered_students(
        students_one,
        seed=42
    )

    order_two = build_ordered_students(
        students_two,
        seed=42
    )

    ids_one = [
        student.student_id
        for student in order_one
    ]

    ids_two = [
        student.student_id
        for student in order_two
    ]

    assert ids_one == ids_two


# ============================================================
# TEST 5
# CONSTRAINED STUDENTS ARE EXCLUDED
# ============================================================

def test_constrained_students_are_excluded():

    normal_student = make_student(
        "STU001"
    )

    constrained_student = make_student(
        "STU002",
        special_needs=True
    )

    result = build_ordered_students(
        [
            normal_student,
            constrained_student
        ],
        seed=42
    )

    ids = [
        student.student_id
        for student in result
    ]

    assert "STU001" in ids
    assert "STU002" not in ids


# ============================================================
# TEST 6
# HIGHER PRIORITY STUDENT COMES FIRST
# ============================================================

def test_higher_priority_student_comes_first():

    low_priority = make_student(
        "STU001",
        priority_score=10
    )

    high_priority = make_student(
        "STU002",
        priority_score=50
    )

    result = build_ordered_students(
        [
            low_priority,
            high_priority
        ],
        seed=42
    )

    assert result[0].student_id == "STU002"


# ============================================================
# TEST 7
# GROUP SEATS BY ROOM
# ============================================================

def test_group_seats_by_room():

    seat_a2 = make_seat(
        "R1-A2",
        1,
        "A2"
    )

    seat_a1 = make_seat(
        "R1-A1",
        1,
        "A1"
    )

    seat_b1 = make_seat(
        "R2-B1",
        2,
        "B1"
    )

    result = group_seats_by_room(
        [
            seat_a2,
            seat_b1,
            seat_a1
        ]
    )

    assert list(result.keys()) == [1, 2]

    assert result[1][0].seat_id == "R1-A1"
    assert result[1][1].seat_id == "R1-A2"

    assert result[2][0].seat_id == "R2-B1"


# ============================================================
# TEST 8
# ROUND-ROBIN ALLOCATION ACROSS ROOMS
# ============================================================

def test_round_robin_allocation():

    students = [
        make_student(
            "STU001",
            programme="MSc AI"
        ),
        make_student(
            "STU002",
            programme="MSc DS"
        ),
        make_student(
            "STU003",
            programme="MSc CS"
        ),
        make_student(
            "STU004",
            programme="MSc AI"
        ),
    ]

    seats = [
        make_seat(
            "R1-A1",
            1,
            "A1"
        ),
        make_seat(
            "R1-A2",
            1,
            "A2"
        ),
        make_seat(
            "R2-A1",
            2,
            "A1"
        ),
        make_seat(
            "R2-A2",
            2,
            "A2"
        ),
    ]

    allocation, remaining = seeded_initial_placement(
        students,
        seats,
        seed=42
    )

    # Four students should receive four seats.
    assert len(allocation) == 4

    # Collect all assigned seat IDs.
    assigned_seats = [
        seat.seat_id
        for seat in allocation.values()
    ]

    # Every student must receive a different seat.
    assert len(set(assigned_seats)) == 4

    # Both rooms must be used.
    room_ids = {
        seat.room_id
        for seat in allocation.values()
    }

    assert room_ids == {1, 2}

    # All available seats should have been consumed.
    assert remaining == []