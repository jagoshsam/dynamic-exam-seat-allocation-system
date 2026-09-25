from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db

from app.models.exam import ExamSession
from app.models.student import Student
from app.models.room import Room
from app.models.seat import Seat
from app.models.allocation import AllocationRecord
from app.models.audit import AuditLog


# ============================================================
# TEST DATABASE
# ============================================================

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# DATABASE OVERRIDE
# ============================================================

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# TEST CLIENT FIXTURE
# ============================================================

@pytest.fixture()
def client():
    """
    Create a clean database and temporarily override
    the application's database dependency.

    The original dependency overrides are restored after
    every test so this test module cannot affect other
    test modules.
    """

    # Start with a completely clean database.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Save any existing overrides.
    original_overrides = app.dependency_overrides.copy()

    # Apply this test module's database.
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client

    finally:
        # Restore the overrides that existed before this test.
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

        # Remove test database tables.
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST DATA HELPER
# ============================================================

def create_test_environment():
    db = TestingSessionLocal()

    # --------------------------------------------------------
    # Create exam
    # --------------------------------------------------------

    exam = ExamSession(
        exam_id="EXAM-API-001",
        course_code="CS501",
        exam_datetime=datetime(2026, 10, 5, 9, 0),
        duration=180,
        allowed_rooms="TEST-R101",
        proctoring_level="standard"
    )

    db.add(exam)

    # --------------------------------------------------------
    # Create room
    # --------------------------------------------------------

    room = Room(
        room_id="TEST-R101",
        building="Test Building",
        floor=1,
        capacity=10
    )

    db.add(room)

    # --------------------------------------------------------
    # Create students
    # --------------------------------------------------------

    students = [
        Student(
            student_id="STU001",
            name="Student One",
            programme="MSc AI",
            year=1,
            special_needs=False,
            priority_score=0
        ),
        Student(
            student_id="STU002",
            name="Student Two",
            programme="MSc AI",
            year=1,
            special_needs=False,
            priority_score=0
        ),
        Student(
            student_id="STU003",
            name="Student Three",
            programme="MSc DS",
            year=1,
            special_needs=False,
            priority_score=0
        )
    ]

    db.add_all(students)

    db.commit()

    db.refresh(exam)
    db.refresh(room)

    # --------------------------------------------------------
    # Create seats
    # --------------------------------------------------------

    seats = []

    for number in range(1, 6):

        seat = Seat(
            seat_id=f"TEST-R101-A{number}",
            label=f"A{number}",
            x_coordinate=number,
            y_coordinate=1,
            accessibility_flag=False,
            occupied_flag=False,
            room_id=room.id
        )

        db.add(seat)
        seats.append(seat)

    db.commit()

    db.close()


# ============================================================
# TEST 1 — SUCCESSFUL ALLOCATION
# ============================================================

def test_run_allocation_success(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [
                "STU001",
                "STU002",
                "STU003"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exam_id"] == "EXAM-API-001"
    assert data["seed"] == 42
    assert data["allocation_count"] == 3

    assert len(data["allocations"]) == 3


# ============================================================
# TEST 2 — ALLOCATION IS PERSISTED
# ============================================================

def test_allocation_is_persisted(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [
                "STU001",
                "STU002",
                "STU003"
            ],
            "seed": 42,
            "assigned_by": "test"
        }
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    try:
        records = (
            db.query(AllocationRecord)
            .all()
        )

        assert len(records) == 3

    finally:
        db.close()


# ============================================================
# TEST 3 — GET SAVED ALLOCATION
# ============================================================

def test_get_saved_allocation(client):

    create_test_environment()

    run_response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [
                "STU001",
                "STU002",
                "STU003"
            ],
            "seed": 42,
            "assigned_by": "test"
        }
    )

    assert run_response.status_code == 200

    response = client.get(
        "/allocations/EXAM-API-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exam_id"] == "EXAM-API-001"
    assert data["allocation_count"] == 3
    assert len(data["allocations"]) == 3


# ============================================================
# TEST 4 — MISSING EXAM
# ============================================================

def test_run_allocation_missing_exam(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/DOES-NOT-EXIST",
        json={
            "student_ids": [
                "STU001"
            ],
            "seed": 42
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Exam not found: DOES-NOT-EXIST"
    )


# ============================================================
# TEST 5 — MISSING STUDENT
# ============================================================

def test_run_allocation_missing_student(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [
                "STU001",
                "STU999"
            ],
            "seed": 42
        }
    )

    assert response.status_code == 404

    detail = response.json()["detail"]

    assert detail["message"] == (
        "Some students were not found"
    )

    assert "STU999" in detail["missing_student_ids"]


# ============================================================
# TEST 6 — DUPLICATE ALLOCATION
# ============================================================

def test_duplicate_allocation(client):

    create_test_environment()

    request_data = {
        "student_ids": [
            "STU001",
            "STU002",
            "STU003"
        ],
        "seed": 42,
        "assigned_by": "test"
    }

    first_response = client.post(
        "/allocations/run/EXAM-API-001",
        json=request_data
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/allocations/run/EXAM-API-001",
        json=request_data
    )

    assert second_response.status_code == 409

    assert "Allocation already exists" in (
        second_response.json()["detail"]
    )


# ============================================================
# TEST 7 — AUDIT LOG CREATED
# ============================================================

def test_allocation_creates_audit_log(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [
                "STU001",
                "STU002",
                "STU003"
            ],
            "seed": 42,
            "assigned_by": "test"
        }
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    try:
        logs = (
            db.query(AuditLog)
            .filter(
                AuditLog.action == "CREATE_ALLOCATION"
            )
            .all()
        )

        assert len(logs) == 1

        assert logs[0].entity == (
            "exam:EXAM-API-001"
        )

        assert logs[0].user == "test"

    finally:
        db.close()


# ============================================================
# TEST 8 — INVALID EMPTY STUDENT LIST
# ============================================================

def test_empty_student_list(client):

    create_test_environment()

    response = client.post(
        "/allocations/run/EXAM-API-001",
        json={
            "student_ids": [],
            "seed": 42
        }
    )

    assert response.status_code == 422