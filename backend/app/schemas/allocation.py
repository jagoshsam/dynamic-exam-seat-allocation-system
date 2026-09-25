from pydantic import BaseModel, Field


# =========================================================
# RUN ALLOCATION REQUEST
# =========================================================

class AllocationRunRequest(BaseModel):
    """
    Request body for running an examination
    seat allocation.
    """

    student_ids: list[str] = Field(
        min_length=1,
        description="Student IDs to include in the allocation"
    )

    seed: int = Field(
        default=42,
        description="Deterministic allocation seed"
    )

    max_iterations: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum local optimization iterations"
    )

    assigned_by: str = Field(
        default="system",
        min_length=1,
        description="User or system performing the allocation"
    )


# =========================================================
# SINGLE ALLOCATION RESPONSE
# =========================================================

class AllocationItemResponse(BaseModel):
    """
    Single student seat assignment.
    """

    student_id: str
    student_name: str
    seat_id: str
    seat_label: str
    room_id: str


# =========================================================
# RUN ALLOCATION RESPONSE
# =========================================================

class AllocationRunResponse(BaseModel):
    """
    Response returned after running allocation.
    """

    exam_id: str
    seed: int
    allocation_count: int
    allocations: list[AllocationItemResponse]


# =========================================================
# SAVED ALLOCATION RESPONSE
# =========================================================

class SavedAllocationResponse(BaseModel):
    """
    Response returned when retrieving an
    already saved allocation.
    """

    exam_id: str
    allocation_count: int
    allocations: list[AllocationItemResponse]