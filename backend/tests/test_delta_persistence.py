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
# HELPER
# ============================================================

def create_test_data(db):

    room = Room(
        room_id="ROOM-01",
        building="Main Building",
        floor=1,
        capacity=4,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    seat_1 = Seat(
        seat_id="ROOM-01-A1",
        label="A1",
        x_coordinate=1,
        y_coordinate=1,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room.id,
    )

    seat_2 = Seat(
        seat_id="ROOM-01-A2",
        label="A2",
        x_coordinate=2,
        y_coordinate=1,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room.id,
    )

    seat_3 = Seat(
        seat_id="ROOM-01-A3",
        label="A3",
        x_coordinate=3,
        y_coordinate=1,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room.id,
    )

    seat_4 = Seat(
        seat_id="ROOM-01-A4",
        label="A4",
        x_coordinate=4,
        y_coordinate=1,
        accessibility_flag=False,
        occupied_flag=False,
        room_id=room.id,
    )

    db.add_all([
        seat_1,
        seat_2,
        seat_3,
        seat_4,
    ])

    student_1 = Student(
        student_id="STU001",
        name="Student One",
        programme="MSc AI",
        year=1,
        special_needs=False,
        conflict_exams=None,
        priority_score=0,
    )

    student_2 = Student(
        student_id="STU002",
        name="Student Two",
        programme="MSc DS",
        year=1,
        special_needs=False,
        conflict_exams=None,
        priority_score=0,
    )

    db.add_all([
        student_1,
        student_2,
    ])

    exam = ExamSession(
        exam_id="EXAM001",
        course_code="AI101",
        exam_datetime=datetime(
            2026,
            10,
            1,
            10,
            0
        ),
        duration=120,
        allowed_rooms='["ROOM-01"]',
        proctoring_level="standard",
    )

    db.add(exam)

    db.commit()

    db.refresh(student_1)
    db.refresh(student_2)
    db.refresh(exam)

    return {
        "room": room,
        "seats": [
            seat_1,
            seat_2,
            seat_3,
            seat_4,
        ],
        "students": [
            student_1,
            student_2,
        ],
        "exam": exam,
    }


# ============================================================
# TEST 1
# UPDATE EXISTING ALLOCATION RECORD
# ============================================================

def test_delta_persistence_updates_existing_record():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        exam = data["exam"]
        students = data["students"]
        seats = data["seats"]

        # -----------------------------------------------------
        # Existing allocation:
        #
        # STU001 -> A1
        # STU002 -> A2
        # -----------------------------------------------------

        record_1 = AllocationRecord(
            exam_id=exam.id,
            student_id=students[0].id,
            seat_id=seats[0].id,
            seed=42,
            assigned_by="system",
            reason="initial allocation",
        )

        record_2 = AllocationRecord(
            exam_id=exam.id,
            student_id=students[1].id,
            seat_id=seats[1].id,
            seed=42,
            assigned_by="system",
            reason="initial allocation",
        )

        db.add_all([
            record_1,
            record_2,
        ])

        db.commit()

        # -----------------------------------------------------
        # STU001 changes from A1 -> A3
        # -----------------------------------------------------

        from app.allocation.delta_reallocation import DeltaChange

        changes = [
            DeltaChange(
                student_id="STU001",
                old_seat_id="ROOM-01-A1",
                new_seat_id="ROOM-01-A3",
                reason="delta reallocation",
            )
        ]

        service = AllocationService(db)

        service.save_delta_reallocation(
            exam=exam,
            changes=changes,
            students=students,
            all_seats=seats,
            seed=42,
            user="admin",
        )

        updated_record = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id,
                AllocationRecord.student_id == students[0].id,
            )
            .first()
        )

        assert updated_record is not None

        assert (
            updated_record.seat_id
            == seats[2].id
        )

        assert updated_record.reason == "delta reallocation"

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 2
# UNAFFECTED STUDENT REMAINS UNCHANGED
# ============================================================

def test_unaffected_student_remains_unchanged():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        exam = data["exam"]
        students = data["students"]
        seats = data["seats"]

        record_1 = AllocationRecord(
            exam_id=exam.id,
            student_id=students[0].id,
            seat_id=seats[0].id,
            seed=42,
            assigned_by="system",
            reason="initial allocation",
        )

        record_2 = AllocationRecord(
            exam_id=exam.id,
            student_id=students[1].id,
            seat_id=seats[1].id,
            seed=42,
            assigned_by="system",
            reason="initial allocation",
        )

        db.add_all([
            record_1,
            record_2,
        ])

        db.commit()

        from app.allocation.delta_reallocation import DeltaChange

        changes = [
            DeltaChange(
                student_id="STU001",
                old_seat_id="ROOM-01-A1",
                new_seat_id="ROOM-01-A3",
                reason="delta reallocation",
            )
        ]

        service = AllocationService(db)

        service.save_delta_reallocation(
            exam=exam,
            changes=changes,
            students=students,
            all_seats=seats,
            seed=42,
            user="admin",
        )

        unaffected_record = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id,
                AllocationRecord.student_id == students[1].id,
            )
            .first()
        )

        assert unaffected_record is not None

        assert (
            unaffected_record.seat_id
            == seats[1].id
        )

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 3
# AUDIT LOG IS CREATED
# ============================================================

def test_delta_reallocation_creates_audit_log():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        exam = data["exam"]
        students = data["students"]
        seats = data["seats"]

        record = AllocationRecord(
            exam_id=exam.id,
            student_id=students[0].id,
            seat_id=seats[0].id,
            seed=42,
            assigned_by="system",
            reason="initial allocation",
        )

        db.add(record)
        db.commit()

        from app.allocation.delta_reallocation import DeltaChange

        changes = [
            DeltaChange(
                student_id="STU001",
                old_seat_id="ROOM-01-A1",
                new_seat_id="ROOM-01-A3",
                reason="delta reallocation",
            )
        ]

        service = AllocationService(db)

        service.save_delta_reallocation(
            exam=exam,
            changes=changes,
            students=students,
            all_seats=seats,
            seed=42,
            user="admin",
        )

        audit = (
            db.query(AuditLog)
            .filter(
                AuditLog.action
                == "DELTA_REALLOCATION"
            )
            .first()
        )

        assert audit is not None

        assert audit.entity == "exam:EXAM001"
        assert audit.user == "admin"

        assert "STU001" in audit.diff
        assert "ROOM-01-A1" in audit.diff
        assert "ROOM-01-A3" in audit.diff

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 4
# NEW ALLOCATION RECORD CAN BE CREATED
# ============================================================

def test_new_delta_allocation_creates_record():

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        data = create_test_data(db)

        exam = data["exam"]
        students = data["students"]
        seats = data["seats"]

        from app.allocation.delta_reallocation import DeltaChange

        changes = [
            DeltaChange(
                student_id="STU001",
                old_seat_id=None,
                new_seat_id="ROOM-01-A3",
                reason="new allocation",
            )
        ]

        service = AllocationService(db)

        service.save_delta_reallocation(
            exam=exam,
            changes=changes,
            students=students,
            all_seats=seats,
            seed=42,
            user="admin",
        )

        record = (
            db.query(AllocationRecord)
            .filter(
                AllocationRecord.exam_id == exam.id,
                AllocationRecord.student_id == students[0].id,
            )
            .first()
        )

        assert record is not None

        assert (
            record.seat_id
            == seats[2].id
        )

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)