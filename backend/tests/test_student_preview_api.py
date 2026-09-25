import io

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.models.student import Student
from app.routes.students import router


# =========================================================
# TEMPORARY DATABASE
# =========================================================

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

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# TEST FASTAPI APP
# =========================================================

app = FastAPI()

app.include_router(router)


# =========================================================
# DATABASE OVERRIDE
# =========================================================

def override_get_db():

    db = TestingSessionLocal()

    try:

        yield db

    finally:

        db.close()


app.dependency_overrides[
    get_db
] = override_get_db


client = TestClient(app)


# =========================================================
# TEST 1 - VALID CSV PREVIEW
# =========================================================

def test_valid_csv_preview():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
PRE001,Preview Student One,AI,2,false,,10
PRE002,Preview Student Two,DS,2,false,,5
PRE003,Preview Student Three,AI,3,true,,15
"""

    response = client.post(
        "/students/preview-csv",
        files={
            "file": (
                "students.csv",
                io.BytesIO(
                    csv_content.encode("utf-8")
                ),
                "text/csv"
            )
        }
    )

    print("\n======================================")
    print("VALID CSV PREVIEW TEST")
    print("======================================")

    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.json()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["total_rows"] == 3

    assert data["valid_count"] == 3

    assert data["error_count"] == 0

    assert data["duplicate_count"] == 0

    assert data["can_import"] is True

    assert len(data["students"]) == 3

    # -----------------------------------------------------
    # Verify NOTHING was inserted
    # -----------------------------------------------------

    db = TestingSessionLocal()

    try:

        students = (
            db.query(Student)
            .filter(
                Student.student_id.in_([
                    "PRE001",
                    "PRE002",
                    "PRE003"
                ])
            )
            .all()
        )

        assert len(students) == 0

        print(
            "✓ Preview completed without "
            "database insertion"
        )

    finally:

        db.close()


# =========================================================
# TEST 2 - INVALID CSV PREVIEW
# =========================================================

def test_invalid_csv_preview():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
PREBAD001,Bad Student,AI,abc,false,,10
"""

    response = client.post(
        "/students/preview-csv",
        files={
            "file": (
                "students.csv",
                io.BytesIO(
                    csv_content.encode("utf-8")
                ),
                "text/csv"
            )
        }
    )

    print("\n======================================")
    print("INVALID CSV PREVIEW TEST")
    print("======================================")

    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.json()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False

    assert data["total_rows"] == 1

    assert data["valid_count"] == 0

    assert data["error_count"] == 1

    assert data["duplicate_count"] == 0

    assert data["can_import"] is False

    assert len(data["students"]) == 0

    print(
        "✓ Invalid CSV preview rejected correctly"
    )


# =========================================================
# TEST 3 - DUPLICATE PREVIEW
# =========================================================

def test_duplicate_csv_preview():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
PREDUP001,Student One,AI,2,false,,10
PREDUP001,Student Duplicate,DS,2,false,,5
"""

    response = client.post(
        "/students/preview-csv",
        files={
            "file": (
                "students.csv",
                io.BytesIO(
                    csv_content.encode("utf-8")
                ),
                "text/csv"
            )
        }
    )

    print("\n======================================")
    print("DUPLICATE CSV PREVIEW TEST")
    print("======================================")

    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.json()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False

    assert data["total_rows"] == 2

    assert data["valid_count"] == 1

    assert data["error_count"] == 0

    assert data["duplicate_count"] == 1

    assert data["can_import"] is False

    print(
        "✓ Duplicate detected during preview"
    )


# =========================================================
# TEST 4 - EXISTING DATABASE STUDENT
# =========================================================

def test_existing_student_preview():

    db = TestingSessionLocal()

    try:

        existing_student = Student(
            student_id="PREEXIST001",
            name="Existing Student",
            programme="AI",
            year=2,
            special_needs=False,
            conflict_exams=None,
            priority_score=10
        )

        db.add(existing_student)

        db.commit()

    finally:

        db.close()

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
PREEXIST001,Another Student,DS,2,false,,5
"""

    response = client.post(
        "/students/preview-csv",
        files={
            "file": (
                "students.csv",
                io.BytesIO(
                    csv_content.encode("utf-8")
                ),
                "text/csv"
            )
        }
    )

    print("\n======================================")
    print("EXISTING STUDENT PREVIEW TEST")
    print("======================================")

    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.json()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False

    assert data["valid_count"] == 0

    assert data["duplicate_count"] == 1

    assert data["can_import"] is False

    print(
        "✓ Existing student detected "
        "during preview"
    )


# =========================================================
# CLEANUP
# =========================================================

def teardown_module():

    Base.metadata.drop_all(
        bind=engine
    )