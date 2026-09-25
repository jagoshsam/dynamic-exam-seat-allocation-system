from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.room import Room
from app.models.seat import Seat


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


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ============================================================
# HELPER
# ============================================================

def create_test_room():
    db = TestingSessionLocal()

    room = Room(
        room_id="TEST-R101",
        building="Test Building",
        floor=1,
        capacity=30
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    room_id = room.id

    db.close()

    return room_id


# ============================================================
# CLEAN DATABASE BEFORE EACH TEST
# ============================================================

def setup_function():
    db = TestingSessionLocal()

    db.query(Seat).delete()
    db.query(Room).delete()

    db.commit()
    db.close()


# ============================================================
# TEST 1 — CREATE SEAT
# ============================================================

def test_create_seat():

    room_id = create_test_room()

    response = client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["seat_id"] == "TEST-R101-S01"
    assert data["label"] == "A1"
    assert data["room_id"] == room_id
    assert data["accessibility_flag"] is False
    assert data["occupied_flag"] is False


# ============================================================
# TEST 2 — DUPLICATE SEAT ID
# ============================================================

def test_duplicate_seat_id():

    room_id = create_test_room()

    seat_data = {
        "seat_id": "TEST-R101-S01",
        "label": "A1",
        "x_coordinate": 1,
        "y_coordinate": 1,
        "accessibility_flag": False,
        "occupied_flag": False,
        "room_id": room_id
    }

    first_response = client.post(
        "/seats/",
        json=seat_data
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/seats/",
        json=seat_data
    )

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == "Seat ID already exists"


# ============================================================
# TEST 3 — ROOM DOES NOT EXIST
# ============================================================

def test_create_seat_with_invalid_room():

    response = client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R999-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": 99999
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Room not found"


# ============================================================
# TEST 4 — GET ALL SEATS
# ============================================================

def test_get_all_seats():

    room_id = create_test_room()

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S02",
            "label": "A2",
            "x_coordinate": 2,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    response = client.get("/seats/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["seat_id"] == "TEST-R101-S01"
    assert data[1]["seat_id"] == "TEST-R101-S02"


# ============================================================
# TEST 5 — GET SINGLE SEAT
# ============================================================

def test_get_single_seat():

    room_id = create_test_room()

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    response = client.get(
        "/seats/TEST-R101-S01"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["seat_id"] == "TEST-R101-S01"


# ============================================================
# TEST 6 — GET NON-EXISTING SEAT
# ============================================================

def test_get_non_existing_seat():

    response = client.get(
        "/seats/DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Seat not found"


# ============================================================
# TEST 7 — GET ROOM SEATS
# ============================================================

def test_get_room_seats():

    room_id = create_test_room()

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S02",
            "label": "A2",
            "x_coordinate": 2,
            "y_coordinate": 1,
            "accessibility_flag": True,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    response = client.get(
        f"/seats/room/{room_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["room_id"] == room_id
    assert data[1]["room_id"] == room_id


# ============================================================
# TEST 8 — DELETE SEAT
# ============================================================

def test_delete_seat():

    room_id = create_test_room()

    client.post(
        "/seats/",
        json={
            "seat_id": "TEST-R101-S01",
            "label": "A1",
            "x_coordinate": 1,
            "y_coordinate": 1,
            "accessibility_flag": False,
            "occupied_flag": False,
            "room_id": room_id
        }
    )

    response = client.delete(
        "/seats/TEST-R101-S01"
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Seat deleted: TEST-R101-S01"
    )

    get_response = client.get(
        "/seats/TEST-R101-S01"
    )

    assert get_response.status_code == 404

# ============================================================
# TEST 9 — GENERATE SEATS
# ============================================================

def test_generate_seats():

    room_id = create_test_room()

    response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 3,
            "columns": 4
        }
    )

    assert response.status_code == 200

    data = response.json()

    # 3 rows × 4 columns = 12 seats
    assert len(data) == 12

    assert data[0]["seat_id"] == "TEST-R101-A1"
    assert data[0]["label"] == "A1"
    assert data[0]["x_coordinate"] == 1
    assert data[0]["y_coordinate"] == 1

    assert data[3]["seat_id"] == "TEST-R101-A4"
    assert data[4]["seat_id"] == "TEST-R101-B1"

    assert all(
        seat["room_id"] == room_id
        for seat in data
    )


# ============================================================
# TEST 10 — GENERATION EXCEEDS ROOM CAPACITY
# ============================================================

def test_generate_seats_exceeds_capacity():

    room_id = create_test_room()

    response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 6,
            "columns": 6
        }
    )

    # 6 × 6 = 36
    # Room capacity = 30
    assert response.status_code == 400

    assert "room capacity is 30" in response.json()["detail"]


# ============================================================
# TEST 11 — GENERATE SEATS FOR INVALID ROOM
# ============================================================

def test_generate_seats_invalid_room():

    response = client.post(
        "/seats/generate/99999",
        json={
            "rows": 3,
            "columns": 4
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Room not found"


# ============================================================
# TEST 12 — PREVENT DUPLICATE GENERATION
# ============================================================

def test_generate_seats_twice():

    room_id = create_test_room()

    first_response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 3,
            "columns": 4
        }
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/seats/generate/{room_id}",
        json={
            "rows": 3,
            "columns": 4
        }
    )

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "Seats already exist for this room"
    )