import json

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.room import Room
from app.models.seat import Seat
from app.models.exam import ExamSession


class AllocationPreprocessor:

    def __init__(self, db: Session):
        self.db = db

    def validate_exam(self, exam: ExamSession):
        if exam is None:
            raise ValueError("Exam session not found.")

        if not exam.exam_id:
            raise ValueError("Exam ID is required.")

        if not exam.course_code:
            raise ValueError("Course code is required.")

        if exam.duration <= 0:
            raise ValueError("Exam duration must be greater than zero.")

        if not exam.allowed_rooms:
            raise ValueError("At least one allowed room is required.")

    def parse_allowed_rooms(self, allowed_rooms: str):
        """
        Supports either:

        JSON:
        ["A101", "A102"]

        or comma-separated:
        A101,A102
        """

        if not allowed_rooms:
            return []

        try:
            parsed = json.loads(allowed_rooms)

            if isinstance(parsed, list):
                return [str(room).strip() for room in parsed]

        except json.JSONDecodeError:
            pass

        return [
            room.strip()
            for room in allowed_rooms.split(",")
            if room.strip()
        ]

    def get_allowed_rooms(self, exam: ExamSession):
        room_ids = self.parse_allowed_rooms(exam.allowed_rooms)

        if not room_ids:
            raise ValueError("No allowed rooms configured for this exam.")

        rooms = (
            self.db.query(Room)
            .filter(Room.room_id.in_(room_ids))
            .all()
        )

        found_room_ids = {room.room_id for room in rooms}

        missing_rooms = [
            room_id
            for room_id in room_ids
            if room_id not in found_room_ids
        ]

        if missing_rooms:
            raise ValueError(
                f"Allowed rooms not found: {missing_rooms}"
            )

        return rooms

    def get_available_seats(self, rooms):
        room_ids = [room.id for room in rooms]

        seats = (
            self.db.query(Seat)
            .filter(
                Seat.room_id.in_(room_ids),
                Seat.occupied_flag == False
            )
            .all()
        )

        return seats

    def calculate_student_priority(self, student: Student):
        """
        Current priority calculation.

        The current Student model provides:
        - special_needs
        - priority_score

        Conflict-based priority will be added when
        conflict_exams is added to the Student model.
        """

        priority = student.priority_score or 0

        if student.special_needs:
            priority += 100

        return priority

    def get_ordered_students(self, students):
        students_with_priority = []

        for student in students:
            priority = self.calculate_student_priority(student)

            students_with_priority.append(
                (
                    student,
                    priority
                )
            )

        students_with_priority.sort(
            key=lambda item: (
                -item[1],
                item[0].programme,
                item[0].student_id
            )
        )

        return [
            student
            for student, priority in students_with_priority
        ]

    def preprocess(
        self,
        exam: ExamSession,
        students
    ):
        """
        Stage 0:
        1. Validate exam.
        2. Find allowed rooms.
        3. Build available seat pool.
        4. Calculate deterministic student ordering.
        """

        self.validate_exam(exam)

        rooms = self.get_allowed_rooms(exam)

        available_seats = self.get_available_seats(rooms)

        ordered_students = self.get_ordered_students(students)

        if not available_seats:
            raise ValueError(
                "No available seats found in the allowed rooms."
            )

        if len(ordered_students) > len(available_seats):
            raise ValueError(
                "Not enough available seats for all students."
            )

        return {
            "exam": exam,
            "rooms": rooms,
            "available_seats": available_seats,
            "ordered_students": ordered_students
        }