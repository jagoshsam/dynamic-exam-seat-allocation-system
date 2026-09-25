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
# TEMPORARY TEST DATABASE
# =========================================================
#
# StaticPool is important here.
#
# It ensures the same in-memory SQLite connection
# is shared by:
#
# 1. The test code
# 2. FastAPI
# 3. SQLAlchemy
#
# Therefore the "students" table remains available
# during API requests.
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


# Create all tables in the temporary database

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# TEST FASTAPI APPLICATION
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
# TEST 1 - SUCCESSFUL CSV IMPORT
# =========================================================

def test_successful_csv_import():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
API001,API Student One,AI,2,false,,10
API002,API Student Two,DS,2,false,,5
API003,API Student Three,AI,3,true,,15
"""

    response = client.post(
        "/students/import-csv",
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
    print("SUCCESSFUL CSV IMPORT TEST")
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

    assert data["imported_count"] == 3

    assert data["error_count"] == 0

    assert data["duplicate_count"] == 0

    # -----------------------------------------------------
    # Verify database
    # -----------------------------------------------------

    db = TestingSessionLocal()

    try:

        students = (
            db.query(Student)
            .filter(
                Student.student_id.in_([
                    "API001",
                    "API002",
                    "API003"
                ])
            )
            .all()
        )

        assert len(students) == 3

        print(
            "✓ 3 students inserted into "
            "temporary database"
        )

    finally:

        db.close()


# =========================================================
# TEST 2 - INVALID CSV MUST NOT INSERT ANYTHING
# =========================================================

def test_invalid_csv_no_database_insert():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
BAD001,Bad Student,AI,abc,false,,10
"""

    response = client.post(
        "/students/import-csv",
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
    print("INVALID CSV TEST")
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

    assert data["imported_count"] == 0

    assert data["error_count"] == 1

    # -----------------------------------------------------
    # Verify NOTHING was inserted
    # -----------------------------------------------------

    db = TestingSessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(
                Student.student_id
                == "BAD001"
            )
            .first()
        )

        assert student is None

        print(
            "✓ Invalid student was NOT inserted"
        )

    finally:

        db.close()


# =========================================================
# TEST 3 - DUPLICATE CSV STUDENT
# =========================================================

def test_duplicate_csv_student():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
DUP001,Student One,AI,2,false,,10
DUP001,Student Duplicate,DS,2,false,,5
"""

    response = client.post(
        "/students/import-csv",
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
    print("DUPLICATE CSV TEST")
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

    assert data["imported_count"] == 0

    assert data["duplicate_count"] == 1

    # -----------------------------------------------------
    # Verify neither duplicate row was inserted
    # -----------------------------------------------------

    db = TestingSessionLocal()

    try:

        students = (
            db.query(Student)
            .filter(
                Student.student_id
                == "DUP001"
            )
            .all()
        )

        assert len(students) == 0

        print(
            "✓ Duplicate CSV rejected "
            "without database insertion"
        )

    finally:

        db.close()


# =========================================================
# TEST 4 - EXISTING DATABASE STUDENT
# =========================================================

def test_existing_database_student():

    db = TestingSessionLocal()

    try:

        existing_student = Student(
            student_id="EXIST001",
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

    # -----------------------------------------------------
    # CSV attempts to import same student
    # -----------------------------------------------------

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
EXIST001,Another Student,DS,2,false,,5
"""

    response = client.post(
        "/students/import-csv",
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
    print("EXISTING DATABASE STUDENT TEST")
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

    assert data["imported_count"] == 0

    assert data["duplicate_count"] == 1

    print(
        "✓ Existing database student "
        "correctly rejected"
    )


# =========================================================
# TEST 5 - NON CSV FILE
# =========================================================

def test_non_csv_file_rejected():

    response = client.post(
        "/students/import-csv",
        files={
            "file": (
                "students.txt",
                io.BytesIO(
                    b"some text"
                ),
                "text/plain"
            )
        }
    )

    print("\n======================================")
    print("NON CSV FILE TEST")
    print("======================================")

    print(
        "Status:",
        response.status_code
    )

    print(
        "Response:",
        response.json()
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Only CSV files are allowed"
    )

    print(
        "✓ Non-CSV file rejected correctly"
    )


# =========================================================
# CLEANUP
# =========================================================

def teardown_module():

    Base.metadata.drop_all(
        bind=engine
    )