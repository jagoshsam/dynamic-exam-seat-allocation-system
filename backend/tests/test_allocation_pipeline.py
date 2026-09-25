import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base

# Import all models so SQLAlchemy knows about every table.
from app.models.student import Student
from app.models.room import Room
from app.models.seat import Seat
from app.models.exam import ExamSession
from app.models.allocation import AllocationRecord
from app.models.audit import AuditLog

from app.allocation.allocation_pipeline import AllocationPipeline
from app.allocation.allocation_service import AllocationService


# =========================================================
# HELPER FUNCTION
# =========================================================

def create_test_database():
    """
    Create a completely temporary in-memory database.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        }
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    return engine, TestingSessionLocal


# =========================================================
# HELPER FUNCTION
# =========================================================

def create_test_data(db):
    """
    Create temporary room, seats, students and exam.

    This data exists only inside the temporary database.
    """

    # -----------------------------------------------------
    # ROOM
    # -----------------------------------------------------

    room = Room(
        room_id="R001",
        building="Test Block",
        floor=1,
        capacity=4
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    # -----------------------------------------------------
    # SEATS
    # -----------------------------------------------------

    seats = [
        Seat(
            seat_id="R001-S01",
            label="A1",
            x_coordinate=1,
            y_coordinate=1,
            accessibility_flag=True,
            occupied_flag=False,
            room_id=room.id
        ),
        Seat(
            seat_id="R001-S02",
            label="A2",
            x_coordinate=2,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room.id
        ),
        Seat(
            seat_id="R001-S03",
            label="A3",
            x_coordinate=3,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room.id
        ),
        Seat(
            seat_id="R001-S04",
            label="A4",
            x_coordinate=4,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room.id
        )
    ]

    db.add_all(seats)
    db.commit()

    # -----------------------------------------------------
    # STUDENTS
    # -----------------------------------------------------

    students = [
        Student(
            student_id="TEST001",
            name="Test Student 1",
            programme="AI",
            year=2,
            special_needs=True,
            conflict_exams=None,
            priority_score=10
        ),
        Student(
            student_id="TEST002",
            name="Test Student 2",
            programme="DS",
            year=2,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        ),
        Student(
            student_id="TEST003",
            name="Test Student 3",
            programme="AI",
            year=2,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        )
    ]

    db.add_all(students)
    db.commit()

    # -----------------------------------------------------
    # EXAM
    # -----------------------------------------------------

    exam = ExamSession(
        exam_id="TEST-EXAM-001",
        course_code="TEST101",
        exam_datetime=datetime(
            2026,
            9,
            20,
            10,
            0
        ),
        duration=180,
        allowed_rooms=json.dumps(
            ["R001"]
        ),
        proctoring_level="standard"
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    return room, seats, students, exam


# =========================================================
# TEST 1
# REAL ALLOCATION PIPELINE
# =========================================================

def test_real_allocation_pipeline():
    """
    Test:

    Stage 0 - Preprocessing
    Stage 1 - Constrained Placement
    Stage 2 - Seeded Placement
    Stage 3 - Local Optimization
    """

    engine, TestingSessionLocal = create_test_database()

    db = TestingSessionLocal()

    try:

        room, seats, students, exam = create_test_data(db)

        # -------------------------------------------------
        # RUN PIPELINE
        # -------------------------------------------------

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation = result["allocation"]

        print("\n======================================")
        print("REAL ALLOCATION PIPELINE TEST")
        print("======================================")

        print(
            f"Exam: {exam.exam_id}"
        )

        print(
            f"Students allocated: {len(allocation)}"
        )

        print("\nFinal allocation:")

        for student_id, seat in allocation.items():
            print(
                f"  {student_id} -> {seat.seat_id}"
            )

        # -------------------------------------------------
        # VERIFY NUMBER OF ALLOCATIONS
        # -------------------------------------------------

        assert len(allocation) == len(students)

        print(
            "\n✓ Every student received an allocation"
        )

        # -------------------------------------------------
        # VERIFY NO DUPLICATE SEATS
        # -------------------------------------------------

        allocated_seat_ids = [
            seat.seat_id
            for seat in allocation.values()
        ]

        assert len(allocated_seat_ids) == len(
            set(allocated_seat_ids)
        )

        print(
            "✓ No two students share the same seat"
        )

        # -------------------------------------------------
        # VERIFY SPECIAL NEEDS
        # -------------------------------------------------

        constrained_seat = allocation["TEST001"]

        assert constrained_seat.accessibility_flag is True

        print(
            "✓ Special-needs student received "
            "an accessibility seat"
        )

        # -------------------------------------------------
        # VERIFY SEED
        # -------------------------------------------------

        assert result["seed"] == 42

        print(
            "✓ Deterministic seed preserved"
        )

        # -------------------------------------------------
        # VERIFY ROOM
        # -------------------------------------------------

        for seat in allocation.values():
            assert seat.room_id == room.id

        print(
            "✓ All allocations are inside "
            "the allowed examination room"
        )

        print(
            "\n✓ REAL PIPELINE TEST PASSED"
        )

    finally:

        db.close()
        Base.metadata.drop_all(bind=engine)


# =========================================================
# TEST 2
# DETERMINISTIC ALLOCATION
# =========================================================

def test_allocation_is_deterministic():
    """
    Verify that identical inputs and identical seed
    produce the same allocation.
    """

    def run_test_pipeline():

        engine, TestingSessionLocal = create_test_database()

        db = TestingSessionLocal()

        try:

            room, seats, students, exam = create_test_data(db)

            pipeline = AllocationPipeline(db)

            result = pipeline.run(
                exam=exam,
                students=students,
                seed=42,
                max_iterations=100
            )

            allocation = {
                student_id: seat.seat_id
                for student_id, seat
                in result["allocation"].items()
            }

            return allocation

        finally:

            db.close()
            Base.metadata.drop_all(bind=engine)

    # -----------------------------------------------------
    # RUN TWICE
    # -----------------------------------------------------

    first_allocation = run_test_pipeline()

    second_allocation = run_test_pipeline()

    print("\n======================================")
    print("DETERMINISTIC ALLOCATION TEST")
    print("======================================")

    print(
        "First allocation:"
    )

    print(
        first_allocation
    )

    print(
        "\nSecond allocation:"
    )

    print(
        second_allocation
    )

    # -----------------------------------------------------
    # VERIFY SAME RESULT
    # -----------------------------------------------------

    assert first_allocation == second_allocation

    print(
        "\n✓ Same input + same seed "
        "produced the same allocation"
    )


# =========================================================
# TEST 3
# DATABASE PERSISTENCE
# =========================================================

def test_allocation_persistence():
    """
    Verify that:

    Final allocation
        ↓
    AllocationRecord
        ↓
    AuditLog

    are correctly persisted.
    """

    engine, TestingSessionLocal = create_test_database()

    db = TestingSessionLocal()

    try:

        # -------------------------------------------------
        # CREATE TEST DATA
        # -------------------------------------------------

        room, seats, students, exam = create_test_data(db)

        # -------------------------------------------------
        # RUN ALLOCATION PIPELINE
        # -------------------------------------------------

        pipeline = AllocationPipeline(db)

        result = pipeline.run(
            exam=exam,
            students=students,
            seed=42,
            max_iterations=100
        )

        allocation = result["allocation"]

        # -------------------------------------------------
        # SAVE FINAL ALLOCATION
        # -------------------------------------------------

        service = AllocationService(db)

        records = service.save_final_allocation(
            exam=exam,
            allocation=allocation,
            students=students,
            seed=42,
            assigned_by="test",
            reason="integration test"
        )

        print("\n======================================")
        print("DATABASE PERSISTENCE TEST")
        print("======================================")

        print(
            f"Allocation records created: {len(records)}"
        )

        # -------------------------------------------------
        # VERIFY ALLOCATION RECORD COUNT
        # -------------------------------------------------

        saved_records = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id
            )
            .all()
        )

        assert len(saved_records) == len(students)

        print(
            "✓ Allocation records saved correctly"
        )

        # -------------------------------------------------
        # VERIFY EACH RECORD
        # -------------------------------------------------

        for record in saved_records:

            assert record.exam_id == exam.id
            assert record.student_id is not None
            assert record.seat_id is not None
            assert record.seed == 42
            assert record.assigned_by == "test"
            assert record.reason == "integration test"

        print(
            "✓ Allocation record fields are correct"
        )

        # -------------------------------------------------
        # VERIFY AUDIT LOG
        # -------------------------------------------------

        audit_logs = (
            db.query(AuditLog)
            .filter(
                AuditLog.entity == f"exam:{exam.exam_id}"
            )
            .all()
        )

        assert len(audit_logs) == 1

        audit = audit_logs[0]

        assert audit.action == "CREATE_ALLOCATION"
        assert audit.user == "test"

        assert audit.diff == (
            f"Created {len(students)} "
            f"allocation records"
        )

        print(
            "✓ Audit log created correctly"
        )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print(
            "\n✓ DATABASE PERSISTENCE TEST PASSED"
        )

    finally:

        db.close()
        Base.metadata.drop_all(bind=engine)