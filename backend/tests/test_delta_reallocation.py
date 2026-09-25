from app.allocation.delta_reallocation import (
    identify_affected_students,
    collect_available_seats,
    preserve_unaffected_allocations,
    build_delta_allocation,
    generate_delta_changes,
)

from app.models.student import Student
from app.models.seat import Seat


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_student(
    student_id,
    programme="MSc AI",
):
    return Student(
        student_id=student_id,
        name=f"Student {student_id}",
        programme=programme,
        year=1,
        priority_score=0,
        special_needs=False,
        conflict_exams=None,
    )


def make_seat(
    seat_id,
    room_id,
    label,
    x,
    y,
):
    return Seat(
        seat_id=seat_id,
        label=label,
        x_coordinate=x,
        y_coordinate=y,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room_id,
    )


# ============================================================
# TEST 1
# IDENTIFY AFFECTED STUDENTS
# ============================================================

def test_identify_affected_students():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    seat_b = make_seat(
        "R1-A2",
        1,
        "A2",
        2,
        1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    affected = identify_affected_students(
        allocation,
        {"STU001"},
    )

    assert affected == ["STU001"]


# ============================================================
# TEST 2
# NO AFFECTED STUDENTS
# ============================================================

def test_no_affected_students():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    allocation = {
        "STU001": seat_a,
    }

    affected = identify_affected_students(
        allocation,
        set(),
    )

    assert affected == []


# ============================================================
# TEST 3
# COLLECT AVAILABLE SEATS
# ============================================================

def test_collect_available_seats():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    seat_b = make_seat(
        "R1-A2",
        1,
        "A2",
        2,
        1,
    )

    seat_c = make_seat(
        "R1-A3",
        1,
        "A3",
        3,
        1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    all_seats = [
        seat_a,
        seat_b,
        seat_c,
    ]

    available = collect_available_seats(
        allocation,
        {"STU001"},
        all_seats,
    )

    seat_ids = {
        seat.seat_id
        for seat in available
    }

    assert "R1-A1" in seat_ids
    assert "R1-A2" not in seat_ids
    assert "R1-A3" in seat_ids


# ============================================================
# TEST 4
# AFFECTED STUDENT'S OLD SEAT
# BECOMES AVAILABLE
# ============================================================

def test_affected_student_old_seat_becomes_available():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    allocation = {
        "STU001": seat_a,
    }

    available = collect_available_seats(
        allocation,
        {"STU001"},
        [seat_a],
    )

    assert len(available) == 1
    assert available[0].seat_id == "R1-A1"


# ============================================================
# TEST 5
# PRESERVE UNAFFECTED ALLOCATIONS
# ============================================================

def test_preserve_unaffected_allocations():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    seat_b = make_seat(
        "R1-A2",
        1,
        "A2",
        2,
        1,
    )

    seat_c = make_seat(
        "R1-A3",
        1,
        "A3",
        3,
        1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
        "STU003": seat_c,
    }

    result = preserve_unaffected_allocations(
        allocation,
        {"STU002"},
    )

    assert "STU001" in result
    assert "STU002" not in result
    assert "STU003" in result

    assert result["STU001"].seat_id == "R1-A1"
    assert result["STU003"].seat_id == "R1-A3"


# ============================================================
# TEST 6
# BUILD DELTA ALLOCATION
# ============================================================

def test_build_delta_allocation():

    seat_a = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    seat_b = make_seat(
        "R1-A2",
        1,
        "A2",
        2,
        1,
    )

    seat_c = make_seat(
        "R1-A3",
        1,
        "A3",
        3,
        1,
    )

    allocation = {
        "STU001": seat_a,
        "STU002": seat_b,
    }

    replacement = {
        "STU002": seat_c,
    }

    result = build_delta_allocation(
        allocation,
        {"STU002"},
        replacement,
    )

    assert result["STU001"].seat_id == "R1-A1"
    assert result["STU002"].seat_id == "R1-A3"


# ============================================================
# TEST 7
# GENERATE DELTA CHANGE
# ============================================================

def test_generate_delta_changes():

    old_seat = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    new_seat = make_seat(
        "R1-A2",
        1,
        "A2",
        2,
        1,
    )

    student = make_student("STU001")

    old_allocation = {
        "STU001": old_seat,
    }

    new_allocation = {
        "STU001": new_seat,
    }

    students_by_id = {
        "STU001": student,
    }

    changes = generate_delta_changes(
        old_allocation,
        new_allocation,
        students_by_id,
    )

    assert len(changes) == 1

    change = changes[0]

    assert change.student_id == "STU001"
    assert change.old_seat_id == "R1-A1"
    assert change.new_seat_id == "R1-A2"
    assert change.reason == "delta reallocation"


# ============================================================
# TEST 8
# UNCHANGED STUDENT PRODUCES NO CHANGE
# ============================================================

def test_unchanged_student_produces_no_change():

    seat = make_seat(
        "R1-A1",
        1,
        "A1",
        1,
        1,
    )

    student = make_student("STU001")

    allocation = {
        "STU001": seat,
    }

    students_by_id = {
        "STU001": student,
    }

    changes = generate_delta_changes(
        allocation,
        allocation,
        students_by_id,
    )

    assert changes == []