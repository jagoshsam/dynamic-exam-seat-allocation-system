import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.exam import ExamSession


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

    # Start every test with a completely fresh database.
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
        # Restore previous dependency overrides.
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

        # Remove test tables.
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST 1 — CREATE EXAM
# ============================================================

def test_create_exam(client):

    response = client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 180,
            "allowed_rooms": "R101,R102",
            "proctoring_level": "standard"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exam_id"] == "EXAM-001"
    assert data["course_code"] == "CS501"
    assert data["duration"] == 180
    assert data["allowed_rooms"] == "R101,R102"
    assert data["proctoring_level"] == "standard"


# ============================================================
# TEST 2 — DUPLICATE EXAM ID
# ============================================================

def test_duplicate_exam_id(client):

    exam_data = {
        "exam_id": "EXAM-001",
        "course_code": "CS501",
        "exam_datetime": "2026-10-05T09:00:00",
        "duration": 180,
        "allowed_rooms": "R101,R102",
        "proctoring_level": "standard"
    }

    first_response = client.post(
        "/exams/",
        json=exam_data
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/exams/",
        json=exam_data
    )

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "Exam ID already exists"
    )


# ============================================================
# TEST 3 — GET ALL EXAMS
# ============================================================

def test_get_all_exams(client):

    client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 180,
            "allowed_rooms": "R101,R102",
            "proctoring_level": "standard"
        }
    )

    client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-002",
            "course_code": "CS502",
            "exam_datetime": "2026-10-06T09:00:00",
            "duration": 120,
            "allowed_rooms": "R103",
            "proctoring_level": "strict"
        }
    )

    response = client.get("/exams/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["exam_id"] == "EXAM-001"
    assert data[1]["exam_id"] == "EXAM-002"


# ============================================================
# TEST 4 — GET SINGLE EXAM
# ============================================================

def test_get_single_exam(client):

    client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 180,
            "allowed_rooms": "R101,R102",
            "proctoring_level": "standard"
        }
    )

    response = client.get(
        "/exams/EXAM-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exam_id"] == "EXAM-001"
    assert data["course_code"] == "CS501"


# ============================================================
# TEST 5 — GET NON-EXISTING EXAM
# ============================================================

def test_get_non_existing_exam(client):

    response = client.get(
        "/exams/DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Exam not found"


# ============================================================
# TEST 6 — DELETE EXAM
# ============================================================

def test_delete_exam(client):

    client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 180,
            "allowed_rooms": "R101,R102",
            "proctoring_level": "standard"
        }
    )

    response = client.delete(
        "/exams/EXAM-001"
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Exam deleted: EXAM-001"
    )

    get_response = client.get(
        "/exams/EXAM-001"
    )

    assert get_response.status_code == 404


# ============================================================
# TEST 7 — INVALID DURATION
# ============================================================

def test_invalid_duration(client):

    response = client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 0,
            "allowed_rooms": "R101",
            "proctoring_level": "standard"
        }
    )

    assert response.status_code == 422


# ============================================================
# TEST 8 — REQUIRED FIELD VALIDATION
# ============================================================

def test_missing_required_field(client):

    response = client.post(
        "/exams/",
        json={
            "exam_id": "EXAM-001",
            "course_code": "CS501",
            "exam_datetime": "2026-10-05T09:00:00",
            "duration": 180,
            "allowed_rooms": "R101"
        }
    )

    assert response.status_code == 422