from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    room_id: str = Field(min_length=1)
    building: str = Field(min_length=1)
    floor: int
    capacity: int = Field(gt=0)


class RoomResponse(RoomCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )