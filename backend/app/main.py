from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

from app.models.student import Student
from app.models.room import Room
from app.models.seat import Seat
from app.models.exam import ExamSession
from app.models.allocation import AllocationRecord
from app.models.audit import AuditLog

from app.routes.students import router as student_router
from app.routes.rooms import router as room_router
from app.routes.seats import router as seat_router
from app.routes.exams import router as exam_router
from app.routes.allocations import router as allocation_router
from app.routes.audit import router as audit_router



# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# CREATE FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Dynamic Examination Seat Allocation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REGISTER API ROUTES
# =========================================================

app.include_router(student_router)
app.include_router(room_router)
app.include_router(seat_router)
app.include_router(exam_router)
app.include_router(allocation_router)
app.include_router(audit_router)



# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Dynamic Examination Seat Allocation System API",
        "status": "running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
