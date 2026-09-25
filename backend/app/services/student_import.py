import csv
import io

from sqlalchemy.orm import Session

from app.models.student import Student


REQUIRED_COLUMNS = {
    "student_id",
    "name",
    "programme",
    "year"
}


# =========================================================
# RESULT CLASS
# =========================================================

class StudentImportResult:

    def __init__(self):

        self.valid_students = []

        self.errors = []

        self.duplicates = []

    @property
    def is_valid(self):

        return (
            len(self.errors) == 0
            and len(self.duplicates) == 0
        )


# =========================================================
# BOOLEAN PARSER
# =========================================================

def parse_boolean(
    value,
    field_name,
    row_number
):

    if value is None:

        return False

    value = str(value).strip().lower()

    if value in {
        "true",
        "1",
        "yes",
        "y"
    }:

        return True

    if value in {
        "false",
        "0",
        "no",
        "n",
        ""
    }:

        return False

    raise ValueError(
        f"Row {row_number}: "
        f"{field_name} must be true/false"
    )


# =========================================================
# INTEGER PARSER
# =========================================================

def parse_integer(
    value,
    field_name,
    row_number
):

    try:

        return int(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            f"Row {row_number}: "
            f"{field_name} must be an integer"
        )


# =========================================================
# STUDENT ROW VALIDATION
# =========================================================

def validate_student_row(
    row,
    row_number
):

    student_id = str(
        row.get(
            "student_id",
            ""
        )
    ).strip()

    name = str(
        row.get(
            "name",
            ""
        )
    ).strip()

    programme = str(
        row.get(
            "programme",
            ""
        )
    ).strip()

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    if not student_id:

        raise ValueError(
            f"Row {row_number}: "
            f"student_id is required"
        )

    if not name:

        raise ValueError(
            f"Row {row_number}: "
            f"name is required"
        )

    if not programme:

        raise ValueError(
            f"Row {row_number}: "
            f"programme is required"
        )

    # -----------------------------------------------------
    # Year
    # -----------------------------------------------------

    year = parse_integer(
        row.get("year"),
        "year",
        row_number
    )

    if year < 1:

        raise ValueError(
            f"Row {row_number}: "
            f"year must be greater than 0"
        )

    # -----------------------------------------------------
    # Special needs
    # -----------------------------------------------------

    special_needs = parse_boolean(
        row.get(
            "special_needs",
            "false"
        ),
        "special_needs",
        row_number
    )

    # -----------------------------------------------------
    # Conflict exams
    # -----------------------------------------------------

    conflict_exams = str(
        row.get(
            "conflict_exams",
            ""
        )
    ).strip()

    if not conflict_exams:

        conflict_exams = None

    # -----------------------------------------------------
    # Priority score
    # -----------------------------------------------------

    priority_value = row.get(
        "priority_score",
        0
    )

    if str(priority_value).strip() == "":

        priority_score = 0

    else:

        priority_score = parse_integer(
            priority_value,
            "priority_score",
            row_number
        )

    # -----------------------------------------------------
    # Return validated student
    # -----------------------------------------------------

    return {

        "student_id": student_id,

        "name": name,

        "programme": programme,

        "year": year,

        "special_needs": special_needs,

        "conflict_exams": conflict_exams,

        "priority_score": priority_score
    }


# =========================================================
# CSV VALIDATION
# =========================================================

def validate_student_csv(
    csv_content: str,
    db: Session | None = None
):

    result = StudentImportResult()

    try:

        reader = csv.DictReader(
            io.StringIO(
                csv_content.strip()
            )
        )

    except Exception as exc:

        result.errors.append(
            f"Unable to read CSV: {exc}"
        )

        return result

    # -----------------------------------------------------
    # Check headers
    # -----------------------------------------------------

    if reader.fieldnames is None:

        result.errors.append(
            "CSV file does not contain headers"
        )

        return result

    actual_columns = {
        column.strip()
        for column in reader.fieldnames
        if column
    }

    missing_columns = (
        REQUIRED_COLUMNS
        - actual_columns
    )

    if missing_columns:

        result.errors.append(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

        return result

    # -----------------------------------------------------
    # Process rows
    # -----------------------------------------------------

    seen_student_ids = set()

    for row_number, row in enumerate(
        reader,
        start=2
    ):

        try:

            student = validate_student_row(
                row,
                row_number
            )

            student_id = student[
                "student_id"
            ]

            # ---------------------------------------------
            # Duplicate inside CSV
            # ---------------------------------------------

            if student_id in seen_student_ids:

                result.duplicates.append(
                    f"Row {row_number}: "
                    f"duplicate student_id "
                    f"{student_id}"
                )

                continue

            seen_student_ids.add(
                student_id
            )

            # ---------------------------------------------
            # Check database
            # ---------------------------------------------

            if db is not None:

                existing_student = (
                    db.query(Student)
                    .filter(
                        Student.student_id
                        == student_id
                    )
                    .first()
                )

                if existing_student is not None:

                    result.duplicates.append(
                        f"Row {row_number}: "
                        f"student_id "
                        f"{student_id} "
                        f"already exists in database"
                    )

                    continue

            result.valid_students.append(
                student
            )

        except ValueError as exc:

            result.errors.append(
                str(exc)
            )

    return result


# =========================================================
# INSERT VALIDATED STUDENTS
# =========================================================

def import_students(
    db: Session,
    validated_students: list[dict]
):

    students = []

    try:

        for student_data in validated_students:

            student = Student(
                student_id=student_data[
                    "student_id"
                ],

                name=student_data[
                    "name"
                ],

                programme=student_data[
                    "programme"
                ],

                year=student_data[
                    "year"
                ],

                special_needs=student_data[
                    "special_needs"
                ],

                conflict_exams=student_data[
                    "conflict_exams"
                ],

                priority_score=student_data[
                    "priority_score"
                ]
            )

            db.add(student)

            students.append(
                student
            )

        db.commit()

        for student in students:

            db.refresh(student)

        return students

    except Exception:

        db.rollback()

        raise