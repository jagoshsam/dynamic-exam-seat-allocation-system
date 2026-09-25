from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response
)

import csv
from io import StringIO

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.room import Room

from app.schemas.room import (
    RoomCreate,
    RoomResponse
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


# =========================================================
# CREATE ROOM
# =========================================================

@router.post(
    "/",
    response_model=RoomResponse
)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Check whether room already exists
    # -----------------------------------------------------

    existing_room = (
        db.query(Room)
        .filter(
            Room.room_id == room.room_id
        )
        .first()
    )

    if existing_room is not None:

        raise HTTPException(
            status_code=409,
            detail=(
                f"Room already exists: "
                f"{room.room_id}"
            )
        )

    # -----------------------------------------------------
    # Create new room
    # -----------------------------------------------------

    new_room = Room(
        room_id=room.room_id,
        building=room.building,
        floor=room.floor,
        capacity=room.capacity
    )

    db.add(new_room)

    db.commit()

    db.refresh(new_room)

    return new_room


# =========================================================
# GET ALL ROOMS
# =========================================================

@router.get(
    "/",
    response_model=list[RoomResponse]
)
def get_rooms(
    db: Session = Depends(get_db)
):

    return (
        db.query(Room)
        .order_by(Room.room_id)
        .all()
    )


# =========================================================
# EXPORT ROOMS TO CSV
# =========================================================

@router.get(
    "/export-csv"
)
def export_rooms_csv(
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Get rooms from database
    # -----------------------------------------------------

    rooms = (
        db.query(Room)
        .order_by(Room.room_id)
        .all()
    )

    # -----------------------------------------------------
    # Create CSV in memory
    # -----------------------------------------------------

    output = StringIO()

    writer = csv.writer(output)

    # -----------------------------------------------------
    # CSV HEADER
    # -----------------------------------------------------

    writer.writerow([
        "room_id",
        "building",
        "floor",
        "capacity"
    ])

    # -----------------------------------------------------
    # WRITE ROOM DATA
    # -----------------------------------------------------

    for room in rooms:

        writer.writerow([
            room.room_id,
            room.building,
            room.floor,
            room.capacity
        ])

    # -----------------------------------------------------
    # RETURN CSV FILE
    # -----------------------------------------------------

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="rooms_export.csv"'
            )
        }
    )