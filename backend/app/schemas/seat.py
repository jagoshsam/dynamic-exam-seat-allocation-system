from pydantic import BaseModel, ConfigDict, Field


class SeatCreate(BaseModel):
    seat_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    x_coordinate: int
    y_coordinate: int
    accessibility_flag: bool = False
    occupied_flag: bool = False
    room_id: int


class SeatResponse(SeatCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SeatGenerationRequest(BaseModel):
    rows: int = Field(gt=0)
    columns: int = Field(gt=0)