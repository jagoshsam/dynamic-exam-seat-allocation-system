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

from app.models.seat import Seat
from app.models.room import Room

from app.schemas.seat import (
    SeatCreate,
    SeatResponse,
    SeatGenerationRequest
)


router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)


# ============================================================
# CREATE SINGLE SEAT
# ============================================================

@router.post(
    "/",
    response_model=SeatResponse
)
def create_seat(
    seat: SeatCreate,
    db: Session = Depends(get_db)
):

    # Check whether the room exists

    room = db.query(Room).filter(
        Room.id == seat.room_id
    ).first()

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    # Check for duplicate seat ID

    existing = db.query(Seat).filter(
        Seat.seat_id == seat.seat_id
    ).first()

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Seat ID already exists"
        )

    new_seat = Seat(
        seat_id=seat.seat_id,
        label=seat.label,
        x_coordinate=seat.x_coordinate,
        y_coordinate=seat.y_coordinate,
        accessibility_flag=seat.accessibility_flag,
        occupied_flag=seat.occupied_flag,
        room_id=seat.room_id
    )

    db.add(new_seat)

    db.commit()

    db.refresh(new_seat)

    return new_seat


# ============================================================
# GET ALL SEATS
# ============================================================

@router.get(
    "/",
    response_model=list[SeatResponse]
)
def get_seats(
    db: Session = Depends(get_db)
):

    return (
        db.query(Seat)
        .order_by(Seat.seat_id)
        .all()
    )


# ============================================================
# EXPORT SEATS TO CSV
# ============================================================

@router.get(
    "/export-csv"
)
def export_seats_csv(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Get seats from database
    # --------------------------------------------------------

    seats = (
        db.query(Seat)
        .order_by(Seat.seat_id)
        .all()
    )

    # --------------------------------------------------------
    # Create CSV in memory
    # --------------------------------------------------------

    output = StringIO()

    writer = csv.writer(output)

    # --------------------------------------------------------
    # CSV HEADER
    # --------------------------------------------------------

    writer.writerow([
        "seat_id",
        "label",
        "x_coordinate",
        "y_coordinate",
        "accessibility_flag",
        "occupied_flag",
        "room_id"
    ])

    # --------------------------------------------------------
    # WRITE SEAT DATA
    # --------------------------------------------------------

    for seat in seats:

        writer.writerow([
            seat.seat_id,
            seat.label,
            seat.x_coordinate,
            seat.y_coordinate,
            seat.accessibility_flag,
            seat.occupied_flag,
            seat.room_id
        ])

    # --------------------------------------------------------
    # RETURN CSV FILE
    # --------------------------------------------------------

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="seats_export.csv"'
            )
        }
    )


# ============================================================
# GENERATE SEATS FOR A ROOM
# ============================================================

@router.post(
    "/generate/{room_id}",
    response_model=list[SeatResponse]
)
def generate_seats(
    room_id: int,
    request: SeatGenerationRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Check whether the room exists
    # --------------------------------------------------------

    room = db.query(Room).filter(
        Room.id == room_id
    ).first()

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    # --------------------------------------------------------
    # 2. Calculate requested number of seats
    # --------------------------------------------------------

    total_seats = (
        request.rows *
        request.columns
    )

    # --------------------------------------------------------
    # 3. Check room capacity
    # --------------------------------------------------------

    if total_seats > room.capacity:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Requested {total_seats} seats, "
                f"but room capacity is {room.capacity}"
            )
        )

    # --------------------------------------------------------
    # 4. Check whether the room already has seats
    # --------------------------------------------------------

    existing_seats = (
        db.query(Seat)
        .filter(
            Seat.room_id == room_id
        )
        .count()
    )

    if existing_seats > 0:

        raise HTTPException(
            status_code=409,
            detail="Seats already exist for this room"
        )

    # --------------------------------------------------------
    # 5. Generate seats
    # --------------------------------------------------------

    generated_seats = []

    for row in range(request.rows):

        # Convert row number to letter

        row_label = chr(65 + row)

        for column in range(
            request.columns
        ):

            column_number = column + 1

            seat_label = (
                f"{row_label}{column_number}"
            )

            seat_id = (
                f"{room.room_id}-{seat_label}"
            )

            new_seat = Seat(
                seat_id=seat_id,
                label=seat_label,
                x_coordinate=column_number,
                y_coordinate=row + 1,
                accessibility_flag=False,
                occupied_flag=False,
                room_id=room_id
            )

            db.add(new_seat)

            generated_seats.append(
                new_seat
            )

    # --------------------------------------------------------
    # 6. Save generated seats
    # --------------------------------------------------------

    db.commit()

    # Refresh generated objects

    for seat in generated_seats:

        db.refresh(seat)

    return generated_seats


# ============================================================
# GET ALL SEATS OF A ROOM
# ============================================================

@router.get(
    "/room/{room_id}",
    response_model=list[SeatResponse]
)
def get_room_seats(
    room_id: int,
    db: Session = Depends(get_db)
):

    # Check whether the room exists

    room = db.query(Room).filter(
        Room.id == room_id
    ).first()

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    return (
        db.query(Seat)
        .filter(
            Seat.room_id == room_id
        )
        .order_by(Seat.seat_id)
        .all()
    )


# ============================================================
# GET SINGLE SEAT
# ============================================================

@router.get(
    "/{seat_id}",
    response_model=SeatResponse
)
def get_seat(
    seat_id: str,
    db: Session = Depends(get_db)
):

    seat = db.query(Seat).filter(
        Seat.seat_id == seat_id
    ).first()

    if not seat:

        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    return seat


# ============================================================
# DELETE SEAT
# ============================================================

@router.delete(
    "/{seat_id}"
)
def delete_seat(
    seat_id: str,
    db: Session = Depends(get_db)
):

    seat = db.query(Seat).filter(
        Seat.seat_id == seat_id
    ).first()

    if not seat:

        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    db.delete(seat)

    db.commit()

    return {
        "message": f"Seat deleted: {seat_id}"
    }