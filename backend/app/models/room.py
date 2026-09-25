from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(String, unique=True, nullable=False, index=True)
    building = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)

    seats = relationship(
        "Seat",
        back_populates="room",
        cascade="all, delete-orphan"
    )