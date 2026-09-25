from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.student import Student

from app.services.student_import import (
    validate_student_csv,
)


# =========================================================
# HELPER - TEMPORARY DATABASE
# =========================================================

def create_test_database():

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

    Base.metadata.create_all(
        bind=engine
    )

    return engine, TestingSessionLocal


# =========================================================
# TEST 1 - VALID CSV
# =========================================================

def test_valid_student_csv():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
TEST001,Student One,AI,2,false,,10
TEST002,Student Two,DS,2,false,,5
TEST003,Student Three,AI,2,true,,15
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("VALID STUDENT CSV TEST")
        print("======================================")

        print(
            f"Valid students: "
            f"{len(result.valid_students)}"
        )

        print(
            f"Errors: "
            f"{len(result.errors)}"
        )

        print(
            f"Duplicates: "
            f"{len(result.duplicates)}"
        )

        assert result.is_valid is True

        assert len(
            result.valid_students
        ) == 3

        assert len(
            result.errors
        ) == 0

        assert len(
            result.duplicates
        ) == 0

        assert (
            result.valid_students[0]["student_id"]
            == "TEST001"
        )

        assert (
            result.valid_students[2]["special_needs"]
            is True
        )

        print(
            "✓ Valid CSV accepted correctly"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )


# =========================================================
# TEST 2 - MISSING REQUIRED COLUMN
# =========================================================

def test_missing_required_column():

    csv_content = """student_id,name,programme,special_needs
TEST001,Student One,AI,false
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("MISSING COLUMN TEST")
        print("======================================")

        print(
            "Errors:",
            result.errors
        )

        assert result.is_valid is False

        assert len(
            result.errors
        ) == 1

        assert (
            "year"
            in result.errors[0]
        )

        print(
            "✓ Missing column detected correctly"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )


# =========================================================
# TEST 3 - DUPLICATE STUDENT ID
# =========================================================

def test_duplicate_student_id():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
TEST001,Student One,AI,2,false,,10
TEST001,Student Duplicate,DS,2,false,,5
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("DUPLICATE STUDENT TEST")
        print("======================================")

        print(
            "Duplicates:",
            result.duplicates
        )

        assert result.is_valid is False

        assert len(
            result.duplicates
        ) == 1

        assert (
            "TEST001"
            in result.duplicates[0]
        )

        print(
            "✓ Duplicate student ID detected"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )


# =========================================================
# TEST 4 - INVALID YEAR
# =========================================================

def test_invalid_year():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
TEST001,Student One,AI,abc,false,,10
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("INVALID YEAR TEST")
        print("======================================")

        print(
            "Errors:",
            result.errors
        )

        assert result.is_valid is False

        assert len(
            result.errors
        ) == 1

        assert (
            "year must be an integer"
            in result.errors[0]
        )

        print(
            "✓ Invalid year detected correctly"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )


# =========================================================
# TEST 5 - EXISTING DATABASE STUDENT
# =========================================================

def test_existing_database_student():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
TEST001,Student One,AI,2,false,,10
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        # -------------------------------------------------
        # Add an existing student to TEMPORARY database
        # -------------------------------------------------

        existing_student = Student(
            student_id="TEST001",
            name="Existing Student",
            programme="AI",
            year=2,
            special_needs=False,
            conflict_exams=None,
            priority_score=5
        )

        db.add(existing_student)
        db.commit()

        # -------------------------------------------------
        # Validate CSV
        # -------------------------------------------------

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("EXISTING DATABASE STUDENT TEST")
        print("======================================")

        print(
            "Duplicates:",
            result.duplicates
        )

        assert result.is_valid is False

        assert len(
            result.duplicates
        ) == 1

        assert (
            "already exists in database"
            in result.duplicates[0]
        )

        print(
            "✓ Existing database student detected"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )


# =========================================================
# TEST 6 - INVALID BOOLEAN
# =========================================================

def test_invalid_boolean():

    csv_content = """student_id,name,programme,year,special_needs,conflict_exams,priority_score
TEST001,Student One,AI,2,maybe,,10
"""

    engine, TestingSessionLocal = (
        create_test_database()
    )

    db = TestingSessionLocal()

    try:

        result = validate_student_csv(
            csv_content,
            db
        )

        print("\n======================================")
        print("INVALID BOOLEAN TEST")
        print("======================================")

        print(
            "Errors:",
            result.errors
        )

        assert result.is_valid is False

        assert len(
            result.errors
        ) == 1

        assert (
            "special_needs must be true/false"
            in result.errors[0]
        )

        print(
            "✓ Invalid boolean detected correctly"
        )

    finally:

        db.close()

        Base.metadata.drop_all(
            bind=engine
        )