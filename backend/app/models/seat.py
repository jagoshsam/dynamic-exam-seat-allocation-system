from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)

    seat_id = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)

    x_coordinate = Column(Integer, nullable=False)
    y_coordinate = Column(Integer, nullable=False)

    accessibility_flag = Column(Boolean, default=False)
    occupied_flag = Column(Boolean, default=False)

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    room = relationship(
        "Room",
        back_populates="seats"
    )