from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base

from app.models.student import Student
from app.models.room import Room
from app.models.seat import Seat
from app.models.exam import ExamSession
from app.models.allocation import AllocationRecord
from app.models.audit import AuditLog

from app.allocation.allocation_pipeline import AllocationPipeline
from app.allocation.allocation_service import AllocationService


# ============================================================
# TEST DATABASE
# ============================================================

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# TEST DATA
# ============================================================

def create_test_data(db):

    # ---------------------------------------------------------
    # ROOM 1
    # ---------------------------------------------------------

    room_1 = Room(
        room_id="ROOM-01",
        building="Main Building",
        floor=1,
        capacity=4
    )

    # ---------------------------------------------------------
    # ROOM 2
    # ---------------------------------------------------------

    room_2 = Room(
        room_id="ROOM-02",
        building="Main Building",
        floor=1,
        capacity=4
    )

    db.add_all([
        room_1,
        room_2
    ])

    db.commit()

    db.refresh(room_1)
    db.refresh(room_2)

    # ---------------------------------------------------------
    # SEATS
    # ---------------------------------------------------------

    seats = [
        Seat(
            seat_id="ROOM-01-A1",
            label="A1",
            x_coordinate=1,
            y_coordinate=1,
            accessibility_flag=True,
            occupied_flag=False,
            room_id=room_1.id
        ),

        Seat(
            seat_id="ROOM-01-A2",
            label="A2",
            x_coordinate=2,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_1.id
        ),

        Seat(
            seat_id="ROOM-01-A3",
            label="A3",
            x_coordinate=3,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_1.id
        ),

        Seat(
            seat_id="ROOM-01-A4",
            label="A4",
            x_coordinate=4,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_1.id
        ),

        Seat(
            seat_id="ROOM-02-A1",
            label="A1",
            x_coordinate=1,
            y_coordinate=1,
            accessibility_flag=True,
            occupied_flag=False,
            room_id=room_2.id
        ),

        Seat(
            seat_id="ROOM-02-A2",
            label="A2",
            x_coordinate=2,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_2.id
        ),

        Seat(
            seat_id="ROOM-02-A3",
            label="A3",
            x_coordinate=3,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_2.id
        ),

        Seat(
            seat_id="ROOM-02-A4",
            label="A4",
            x_coordinate=4,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room_2.id
        ),
    ]

    db.add_all(seats)

    # ---------------------------------------------------------
    # STUDENTS
    # ---------------------------------------------------------

    students = [
        Student(
            student_id="STU001",
            name="Student One",
            programme="MSc AI",
            year=1,
            special_needs=True,
            conflict_exams=None,
            priority_score=10
        ),

        Student(
            student_id="STU002",
            name="Student Two",
            programme="MSc AI",
            year=1,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        ),

        Student(
            student_id="STU003",
            name="Student Three",
            programme="MSc DS",
            year=1,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        ),

        Student(
            student_id="STU004",
            name="Student Four",
            programme="MSc CS",
            year=1,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        ),
    ]

    db.add_all(students)

    # ---------------------------------------------------------
    # EXAM
    # ---------------------------------------------------------

    exam = ExamSession(
        exam_id="EXAM-001",
        course_code="AI101",
        exam_datetime=datetime(
            2026,
            10,
            1,
            10,
            0
        ),
        duration=120,
        allowed_rooms='["ROOM-01", "ROOM-02"]',
        proctoring_level="standard"
    )

    db.add(exam)

    db.commit()

    for student in students:
        db.refresh(student)

    for seat in seats:
        db.refresh(seat)

    db.refresh(exam)

    return {
        "rooms": [
            room_1,
            room_2
        ],
        "seats": seats,
        "students": students,
        "exam": exam
    }


# ============================================================
# TEST 1
# COMPLETE PIPELINE
# ============================================================

def test_complete_allocation_pipeline():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        students = data["students"]
        exam = data["exam"]

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation = result["allocation"]

        # Four students must be allocated.
        assert len(allocation) == 4

        # Every student must have a seat.
        assert set(allocation.keys()) == {
            "STU001",
            "STU002",
            "STU003",
            "STU004"
        }

        # Every seat must be unique.
        seat_ids = [
            seat.seat_id
            for seat in allocation.values()
        ]

        assert len(set(seat_ids)) == 4

        # Special-needs student must have
        # an accessibility seat.
        special_student_seat = (
            allocation["STU001"]
        )

        assert (
            special_student_seat.accessibility_flag
            is True
        )

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 2
# SAVE FINAL ALLOCATION
# ============================================================

def test_save_final_allocation():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        students = data["students"]
        exam = data["exam"]

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation = result["allocation"]

        service = AllocationService(db)

        records = service.save_final_allocation(
            exam=exam,
            allocation=allocation,
            students=students,
            seed=42,
            assigned_by="system",
            reason="initial allocation"
        )

        assert len(records) == 4

        saved_records = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id
            )
            .all()
        )

        assert len(saved_records) == 4

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 3
# AUDIT LOG CREATED
# ============================================================

def test_allocation_creates_audit_log():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        students = data["students"]
        exam = data["exam"]

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        service = AllocationService(db)

        service.save_final_allocation(
            exam=exam,
            allocation=result["allocation"],
            students=students,
            seed=42,
            assigned_by="system",
            reason="initial allocation"
        )

        audit = (
            db.query(AuditLog)
            .filter(
                AuditLog.action
                == "CREATE_ALLOCATION"
            )
            .first()
        )

        assert audit is not None

        assert audit.entity == "exam:EXAM-001"

        assert audit.user == "system"

        assert "4 allocation records" in audit.diff

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 4
# COMPLETE PIPELINE IS DETERMINISTIC
# ============================================================

def test_pipeline_is_deterministic():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        students = data["students"]
        exam = data["exam"]

        pipeline = AllocationPipeline(db)

        result_one = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation_one = {
            student_id: seat.seat_id
            for student_id, seat
            in result_one["allocation"].items()
        }

        # Reset occupied flags before the second run.
        for seat in data["seats"]:
            seat.occupied_flag = False

        db.commit()

        result_two = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation_two = {
            student_id: seat.seat_id
            for student_id, seat
            in result_two["allocation"].items()
        }

        assert allocation_one == allocation_two

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)