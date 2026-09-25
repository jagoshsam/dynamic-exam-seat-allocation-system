from sqlalchemy.orm import Session

from app.models.exam import ExamSession
from app.models.student import Student

from app.allocation.allocation_service import AllocationService


class AllocationPipeline:

    def __init__(self, db: Session):
        self.db = db
        self.service = AllocationService(db)

    def run(
        self,
        exam: ExamSession,
        students: list[Student],
        seed: int = 42,
        max_iterations: int = 100
    ):
        """
        Run the complete allocation pipeline.

        Stages:
        0. Preprocessing
        1. Constrained placement
        2. Seeded placement
        3. Local optimization

        Returns the final allocation and
        intermediate pipeline information.
        """

        # =====================================================
        # STAGE 0 - PREPROCESSING
        # =====================================================

        prepared = self.service.prepare_allocation(
            exam,
            students
        )

        ordered_students = prepared["ordered_students"]
        available_seats = prepared["available_seats"]

        # =====================================================
        # STAGE 1 - CONSTRAINED PLACEMENT
        # =====================================================

        constrained_allocation, remaining_seats = (
            self.service.constrained_placement(
                ordered_students,
                available_seats
            )
        )

        # =====================================================
        # STAGE 2 - SEEDED PLACEMENT
        # =====================================================

        seeded_allocation, remaining_seats = (
            self.service.seeded_placement(
                ordered_students,
                remaining_seats,
                seed
            )
        )

        # Combine Stage 1 and Stage 2 allocations.

        allocation = {}

        allocation.update(
            constrained_allocation
        )

        allocation.update(
            seeded_allocation
        )

        # =====================================================
        # STAGE 3 - LOCAL OPTIMIZATION
        # =====================================================

        optimized_allocation = self.service.optimize(
            allocation,
            ordered_students,
            max_iterations
        )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        return {
            "exam": exam,
            "allocation": optimized_allocation,
            "seed": seed,
            "students": ordered_students,
            "remaining_seats": remaining_seats
        }