from app.allocation.constrained_placement import (
    HardConstraintViolation,
    is_constrained,
    sort_constrained_students,
    select_seat_for_constrained,
    place_constrained_students,
)
from app.models.student import Student
from app.models.seat import Seat


def make_student(
    student_id,
    special_needs=False,
    conflict_exams=None,
    priority_score=0,
    programme="MSc AI"
):
    return Student(
        student_id=student_id,
        name=f"Student {student_id}",
        programme=programme,
        year=1,
        special_needs=special_needs,
        conflict_exams=conflict_exams,
        priority_score=priority_score,
    )


def make_seat(
    seat_id,
    room_id,
    label,
    accessibility=False
):
    return Seat(
        seat_id=seat_id,
        label=label,
        x_coordinate=1,
        y_coordinate=1,
        accessibility_flag=accessibility,
        occupied_flag=False,
        room_id=room_id,
    )


# ============================================================
# TEST 1 — SPECIAL NEEDS STUDENT IS CONSTRAINED
# ============================================================

def test_special_needs_student_is_constrained():

    student = make_student(
        "STU001",
        special_needs=True
    )

    assert is_constrained(student) is True


# ============================================================
# TEST 2 — CONFLICT STUDENT IS CONSTRAINED
# ============================================================

def test_conflict_student_is_constrained():

    student = make_student(
        "STU002",
        conflict_exams="EXAM-002"
    )

    assert is_constrained(student) is True


# ============================================================
# TEST 3 — NORMAL STUDENT IS NOT CONSTRAINED
# ============================================================

def test_normal_student_is_not_constrained():

    student = make_student("STU003")

    assert is_constrained(student) is False


# ============================================================
# TEST 4 — CONSTRAINED STUDENTS SORT BY PRIORITY
# ============================================================

def test_sort_constrained_students():

    low_priority = make_student(
        "STU001",
        special_needs=True,
        priority_score=10
    )

    high_priority = make_student(
        "STU002",
        special_needs=True,
        priority_score=50
    )

    normal_student = make_student(
        "STU003",
        priority_score=100
    )

    result = sort_constrained_students([
        low_priority,
        high_priority,
        normal_student,
    ])

    assert len(result) == 2
    assert result[0].student_id == "STU002"
    assert result[1].student_id == "STU001"


# ============================================================
# TEST 5 — SPECIAL NEEDS GET ACCESSIBLE SEAT
# ============================================================

def test_special_needs_get_accessible_seat():

    student = make_student(
        "STU001",
        special_needs=True
    )

    normal_seat = make_seat(
        "A1",
        1,
        "A1",
        accessibility=False
    )

    accessible_seat = make_seat(
        "A2",
        1,
        "A2",
        accessibility=True
    )

    selected = select_seat_for_constrained(
        student,
        [
            normal_seat,
            accessible_seat
        ]
    )

    assert selected is accessible_seat


# ============================================================
# TEST 6 — NO ACCESSIBLE SEAT RAISES ERROR
# ============================================================

def test_no_accessible_seat_raises_error():

    student = make_student(
        "STU001",
        special_needs=True
    )

    normal_seat = make_seat(
        "A1",
        1,
        "A1",
        accessibility=False
    )

    try:
        select_seat_for_constrained(
            student,
            [normal_seat]
        )

        assert False, "Expected HardConstraintViolation"

    except HardConstraintViolation as exc:

        assert "STU001" in str(exc)


# ============================================================
# TEST 7 — CONSTRAINED PLACEMENT REMOVES USED SEAT
# ============================================================

def test_constrained_placement_removes_used_seat():

    student = make_student(
        "STU001",
        special_needs=True
    )

    accessible_seat = make_seat(
        "A1",
        1,
        "A1",
        accessibility=True
    )

    normal_seat = make_seat(
        "A2",
        1,
        "A2",
        accessibility=False
    )

    allocation, remaining = place_constrained_students(
        [student],
        [
            accessible_seat,
            normal_seat
        ]
    )

    assert allocation["STU001"] is accessible_seat
    assert accessible_seat not in remaining
    assert normal_seat in remaining
    assert accessible_seat.occupied_flag is True


# ============================================================
# TEST 8 — MULTIPLE CONSTRAINED STUDENTS GET DIFFERENT SEATS
# ============================================================

def test_multiple_constrained_students_get_different_seats():

    student_one = make_student(
        "STU001",
        special_needs=True
    )

    student_two = make_student(
        "STU002",
        special_needs=True
    )

    seat_one = make_seat(
        "A1",
        1,
        "A1",
        accessibility=True
    )

    seat_two = make_seat(
        "A2",
        1,
        "A2",
        accessibility=True
    )

    allocation, remaining = place_constrained_students(
        [
            student_one,
            student_two
        ],
        [
            seat_one,
            seat_two
        ]
    )

    assert len(allocation) == 2

    assert allocation["STU001"] is not allocation["STU002"]

    assert len(remaining) == 0