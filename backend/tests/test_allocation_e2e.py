import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app


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
# OVERRIDE DATABASE DEPENDENCY
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

    # Start every test with a completely fresh database.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Save any dependency overrides that existed before
    # this test.
    original_overrides = app.dependency_overrides.copy()

    # Use this test module's database.
    app.dependency_overrides[get_db] = override_get_db

    try:

        with TestClient(app) as test_client:
            yield test_client

    finally:

        # Restore previous dependency overrides.
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

        # Remove test tables.
        Base.metadata.drop_all(bind=engine)


# ============================================================
# CLEAN DATABASE
# ============================================================

def clear_database():

    db = TestingSessionLocal()

    try:

        from app.models.audit import AuditLog
        from app.models.allocation import AllocationRecord
        from app.models.seat import Seat
        from app.models.student import Student
        from app.models.exam import ExamSession
        from app.models.room import Room

        # Delete dependent records first.

        db.query(AuditLog).delete()

        db.query(AllocationRecord).delete()

        db.query(Seat).delete()

        db.query(Student).delete()

        db.query(ExamSession).delete()

        db.query(Room).delete()

        db.commit()

    finally:
        db.close()


# ============================================================
# TEST 1
# COMPLETE API WORKFLOW
# ============================================================

def test_complete_allocation_api_workflow(client):

    clear_database()

    # --------------------------------------------------------
    # STEP 1
    # CREATE ROOM
    # --------------------------------------------------------

    room_response = client.post(
        "/rooms/",
        json={
            "room_id": "ROOM-API-01",
            "building": "Main Building",
            "floor": 1,
            "capacity": 4
        }
    )

    # Current room API returns 200 OK.
    assert room_response.status_code == 200

    room = room_response.json()

    assert room["room_id"] == "ROOM-API-01"

    room_database_id = room["id"]

    # --------------------------------------------------------
    # STEP 2
    # GENERATE SEATS
    # --------------------------------------------------------

    seat_response = client.post(
        f"/seats/generate/{room_database_id}",
        json={
            "rows": 2,
            "columns": 2
        }
    )

    assert seat_response.status_code == 200

    seats = seat_response.json()

    assert len(seats) == 4

    # --------------------------------------------------------
    # IMPORTANT:
    # Mark one seat as accessible for the special-needs
    # student used in this test.
    # --------------------------------------------------------

    db = TestingSessionLocal()

    try:

        from app.models.seat import Seat

        accessible_seat = (
            db.query(Seat)
            .filter(
                Seat.room_id == room_database_id
            )
            .order_by(Seat.id)
            .first()
        )

        assert accessible_seat is not None

        accessible_seat.accessibility_flag = True

        db.commit()

    finally:
        db.close()

    # --------------------------------------------------------
    # STEP 3
    # CREATE STUDENTS
    # --------------------------------------------------------

    students = [
        {
            "student_id": "API-STU001",
            "name": "API Student One",
            "programme": "MSc AI",
            "year": 1,
            "special_needs": True,
            "conflict_exams": None,
            "priority_score": 10
        },
        {
            "student_id": "API-STU002",
            "name": "API Student Two",
            "programme": "MSc DS",
            "year": 1,
            "special_needs": False,
            "conflict_exams": None,
            "priority_score": 5
        },
        {
            "student_id": "API-STU003",
            "name": "API Student Three",
            "programme": "MSc CS",
            "year": 1,
            "special_needs": False,
            "conflict_exams": None,
            "priority_score": 5
        },
        {
            "student_id": "API-STU004",
            "name": "API Student Four",
            "programme": "MSc AI",
            "year": 1,
            "special_needs": False,
            "conflict_exams": None,
            "priority_score": 5
        }
    ]

    for student in students:

        response = client.post(
            "/students/",
            json=student
        )

        # Current student API may use 200 OK.
        assert response.status_code in (200, 201)

    # --------------------------------------------------------
    # STEP 4
    # CREATE EXAM
    # --------------------------------------------------------

    exam_response = client.post(
        "/exams/",
        json={
            "exam_id": "API-EXAM-001",
            "course_code": "AI101",
            "exam_datetime": "2026-10-01T10:00:00",
            "duration": 120,
            "allowed_rooms": '["ROOM-API-01"]',
            "proctoring_level": "standard"
        }
    )

    # Accept the status currently used by the exam API.
    assert exam_response.status_code in (200, 201)

    exam = exam_response.json()

    assert exam["exam_id"] == "API-EXAM-001"

    # --------------------------------------------------------
    # STEP 5
    # RUN ALLOCATION
    # --------------------------------------------------------

    allocation_response = client.post(
        "/allocations/run/API-EXAM-001",
        json={
            "student_ids": [
                "API-STU001",
                "API-STU002",
                "API-STU003",
                "API-STU004"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test-system"
        }
    )

    assert allocation_response.status_code == 200

    allocation_data = allocation_response.json()

    assert allocation_data["exam_id"] == "API-EXAM-001"

    assert allocation_data["seed"] == 42

    assert allocation_data["allocation_count"] == 4

    assert len(
        allocation_data["allocations"]
    ) == 4

    # --------------------------------------------------------
    # STEP 6
    # CHECK UNIQUE SEATS
    # --------------------------------------------------------

    assigned_seats = [
        item["seat_id"]
        for item in allocation_data["allocations"]
    ]

    assert len(
        set(assigned_seats)
    ) == 4

    # --------------------------------------------------------
    # STEP 7
    # VERIFY SPECIAL-NEEDS STUDENT
    # --------------------------------------------------------

    special_student_allocation = next(
        item
        for item in allocation_data["allocations"]
        if item["student_id"] == "API-STU001"
    )

    db = TestingSessionLocal()

    try:

        from app.models.seat import Seat

        special_student_seat = (
            db.query(Seat)
            .filter(
                Seat.seat_id
                == special_student_allocation["seat_id"]
            )
            .first()
        )

        assert special_student_seat is not None

        assert (
            special_student_seat.accessibility_flag
            is True
        )

    finally:
        db.close()

    # --------------------------------------------------------
    # STEP 8
    # GET SAVED ALLOCATION
    # --------------------------------------------------------

    saved_response = client.get(
        "/allocations/API-EXAM-001"
    )

    assert saved_response.status_code == 200

    saved_data = saved_response.json()

    assert saved_data["exam_id"] == "API-EXAM-001"

    assert saved_data["allocation_count"] == 4

    assert len(
        saved_data["allocations"]
    ) == 4


# ============================================================
# TEST 2
# ALLOCATION CANNOT BE RUN TWICE
# ============================================================

def test_allocation_cannot_be_run_twice(client):

    clear_database()

    # --------------------------------------------------------
    # CREATE ROOM
    # --------------------------------------------------------

    room_response = client.post(
        "/rooms/",
        json={
            "room_id": "ROOM-DUP-01",
            "building": "Main Building",
            "floor": 1,
            "capacity": 2
        }
    )

    assert room_response.status_code == 200

    room_id = room_response.json()["id"]

    # --------------------------------------------------------
    # GENERATE SEATS
    # --------------------------------------------------------

    seat_response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 1,
            "columns": 2
        }
    )

    assert seat_response.status_code == 200

    # --------------------------------------------------------
    # CREATE STUDENTS
    # --------------------------------------------------------

    for student_id in [
        "DUP-STU001",
        "DUP-STU002"
    ]:

        response = client.post(
            "/students/",
            json={
                "student_id": student_id,
                "name": f"Student {student_id}",
                "programme": "MSc AI",
                "year": 1,
                "special_needs": False,
                "conflict_exams": None,
                "priority_score": 0
            }
        )

        assert response.status_code in (200, 201)

    # --------------------------------------------------------
    # CREATE EXAM
    # --------------------------------------------------------

    exam_response = client.post(
        "/exams/",
        json={
            "exam_id": "DUP-EXAM-001",
            "course_code": "AI101",
            "exam_datetime": "2026-10-02T10:00:00",
            "duration": 120,
            "allowed_rooms": '["ROOM-DUP-01"]',
            "proctoring_level": "standard"
        }
    )

    assert exam_response.status_code in (200, 201)

    # --------------------------------------------------------
    # FIRST ALLOCATION
    # --------------------------------------------------------

    first_response = client.post(
        "/allocations/run/DUP-EXAM-001",
        json={
            "student_ids": [
                "DUP-STU001",
                "DUP-STU002"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test-system"
        }
    )

    assert first_response.status_code == 200

    # --------------------------------------------------------
    # SECOND ALLOCATION
    # --------------------------------------------------------

    second_response = client.post(
        "/allocations/run/DUP-EXAM-001",
        json={
            "student_ids": [
                "DUP-STU001",
                "DUP-STU002"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test-system"
        }
    )

    # Existing allocation must prevent a second full run.
    assert second_response.status_code == 409


# ============================================================
# TEST 3
# MISSING STUDENT IS REJECTED
# ============================================================

def test_missing_student_is_rejected(client):

    clear_database()

    # --------------------------------------------------------
    # CREATE ROOM
    # --------------------------------------------------------

    room_response = client.post(
        "/rooms/",
        json={
            "room_id": "ROOM-MISSING-01",
            "building": "Main Building",
            "floor": 1,
            "capacity": 2
        }
    )

    assert room_response.status_code == 200

    room_id = room_response.json()["id"]

    # --------------------------------------------------------
    # GENERATE SEATS
    # --------------------------------------------------------

    seat_response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 1,
            "columns": 2
        }
    )

    assert seat_response.status_code == 200

    # --------------------------------------------------------
    # CREATE EXAM
    # --------------------------------------------------------

    exam_response = client.post(
        "/exams/",
        json={
            "exam_id": "MISSING-EXAM-001",
            "course_code": "AI101",
            "exam_datetime": "2026-10-03T10:00:00",
            "duration": 120,
            "allowed_rooms": '["ROOM-MISSING-01"]',
            "proctoring_level": "standard"
        }
    )

    assert exam_response.status_code in (200, 201)

    # --------------------------------------------------------
    # TRY ALLOCATION WITH NON-EXISTENT STUDENT
    # --------------------------------------------------------

    response = client.post(
        "/allocations/run/MISSING-EXAM-001",
        json={
            "student_ids": [
                "DOES-NOT-EXIST"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test-system"
        }
    )

    assert response.status_code == 404

    body = response.json()

    assert "missing_student_ids" in body["detail"]

    assert (
        "DOES-NOT-EXIST"
        in body["detail"]["missing_student_ids"]
    )


# ============================================================
# TEST 4
# NON-EXISTENT EXAM IS REJECTED
# ============================================================

def test_nonexistent_exam_is_rejected(client):

    clear_database()

    response = client.post(
        "/allocations/run/DOES-NOT-EXIST",
        json={
            "student_ids": [
                "STU001"
            ],
            "seed": 42,
            "max_iterations": 100,
            "assigned_by": "test-system"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Exam not found: DOES-NOT-EXIST"
    )