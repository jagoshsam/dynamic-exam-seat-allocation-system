# Dynamic Examination Seat Allocation System

A web-based examination seat allocation system designed around deterministic, constraint-aware, and auditable examination seating. The project supports student, room, seat, and examination management; deterministic allocation; visual seat-map review; minimal-delta reallocation; and audit logging.

The project specification describes a broader rule-driven scheduling platform with hard and soft constraints, reproducible allocation runs, visual seat tools, dynamic reallocation, auditability, integrations, notifications, and institutional outputs. The current implementation covers the implemented development scope documented below; features from the specification that are not yet implemented are explicitly listed as future work.

## 1. Project Overview

The system assigns students to seats across examination rooms for an examination session. The allocation design prioritizes hard constraints before soft optimization and uses deterministic tie-breaking with a stored seed for reproducibility.

The project logic defines the following major allocation stages:

1. Preprocess and validate inputs.
2. Place constrained students first.
3. Perform seeded initial placement.
4. Apply bounded local optimization.
5. Persist allocation information and run metadata where supported.
6. Support minimal-delta changes for live allocation updates.

The specification also defines hard constraints such as one student per seat, seat capacity/availability, accessibility requirements, and avoiding overlapping examination sessions. Soft objectives include programme dispersion, reduced same-programme adjacency, room-utilization balance, and minimizing student movement between published runs.

## 2. Implemented Features

### Student Management

- Create individual students
- View students
- Validate student CSV files before import
- Preview student CSV imports without inserting records
- Import validated student CSV data
- Export student data to CSV
- Duplicate student detection
- Validation of required fields and numeric values

### Room Management

- Create rooms
- View rooms
- Store building, floor, capacity, and room ID
- Export rooms to CSV

### Seat Management

- Create individual seats
- View seats
- Generate a rectangular seat layout from rows and columns
- Associate seats with rooms
- Store seat coordinates
- Store accessibility and occupied flags
- Export seats to CSV

### Examination Management

- Create examination sessions
- View examination sessions
- Store exam ID, course code, date/time, duration, allowed rooms, and proctoring level
- Export examinations to CSV
- Delete examinations

### Allocation

- Deterministic allocation using a configurable seed
- Constraint-aware allocation pipeline
- Constrained-student placement
- Seeded initial placement
- Bounded local optimization
- Saved allocation retrieval
- Examination-specific allowed-room filtering
- Visual seat-map representation

### Delta Reallocation

- Select an existing allocated student
- View the student's current seat
- Select a free replacement seat
- Prevent selection of an already allocated or occupied replacement seat in the frontend
- Restrict replacement seats to rooms allowed for the selected examination
- Submit a delta reallocation request
- Persist allocation changes
- Record delta changes in the audit log

### Auditability

- Audit log API
- Allocation creation records
- Delta reallocation records
- Timestamp and user information
- Human-readable delta change display in the frontend
- Action filtering in the Audit Logs page

### Developer / API Features

- FastAPI REST API
- Swagger/OpenAPI documentation
- Automated backend tests
- React/Vite frontend
- CSV import/export utilities

## 3. Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- JavaScript

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Uvicorn

### Testing

- Pytest
- FastAPI TestClient / HTTPX

## 4. Project Structure

```text
dynamic-exam-seat/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── allocation/
│   │   ├── database/
│   │   └── main.py
│   ├── tests/
│   ├── pytest.ini
│   ├── exam_seat.db
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 5. Backend Setup

Open PowerShell in the project directory:

```powershell
cd backend
```

Create the virtual environment if it does not already exist:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart httpx pytest
```

## 6. Run the Backend

From the `backend` directory with the virtual environment activated:

```powershell
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## 7. API Documentation

FastAPI provides Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

Main API groups:

- Students
- Rooms
- Seats
- Exams
- Allocations
- Audit Logs

Important allocation endpoints:

```text
POST /allocations/run/{exam_id}
GET  /allocations/{exam_id}
POST /allocations/delta/{exam_id}
```

Audit endpoint:

```text
GET /audit-logs/
```

## 8. Frontend Setup

Open a second PowerShell terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the development server:

```powershell
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

The frontend communicates with the backend at:

```text
http://127.0.0.1:8000
```

## 9. Production Build Verification

To create the frontend production build:

```powershell
npm run build
```

The current project has been verified with a successful Vite production build.

## 10. Database

The current development database is SQLite:

```text
backend/exam_seat.db
```

The application creates the required tables when the FastAPI application starts.

The project database is intentionally kept free of fabricated institutional records. The person receiving the project should provide the actual student, room, seat, and examination data.

For future production deployment, the database can be migrated to PostgreSQL.

## 11. Student CSV Import

Students can be created individually or imported through CSV.

The import process supports validation and preview before insertion.

Required columns:

```text
student_id,name,programme,year
```

Optional supported columns:

```text
special_needs,conflict_exams,priority_score
```

Template structure:

```csv
student_id,name,programme,year,special_needs,conflict_exams,priority_score
```

The import validates required fields, numeric values, boolean values, duplicate IDs, and existing database IDs.

Do not insert fabricated institutional data simply for demonstration.

## 12. Room Management

Rooms contain:

- Room ID
- Building
- Floor
- Capacity

Rooms can be created through the frontend and exported to CSV.

## 13. Seat Management

Seats contain:

- Seat ID
- Seat label
- X coordinate
- Y coordinate
- Accessibility flag
- Occupied flag
- Room association

Seats can be created individually or generated automatically for a room.

The seat generator accepts rows and columns and rejects a requested layout when the number of generated seats exceeds the room capacity.

## 14. Examination Management

An examination session contains:

- Exam ID
- Course code
- Examination date/time
- Duration
- Allowed rooms
- Proctoring level

The current application stores `allowed_rooms` as a comma-separated room ID string.

Example:

```text
R001,R002,R003
```

The allocation page uses this configuration to restrict the displayed examination seat map and available replacement seats to permitted rooms.

## 15. Allocation Workflow

The implemented workflow is:

```text
Students
   ↓
Rooms
   ↓
Seats
   ↓
Exam Session
   ↓
Select Students
   ↓
Run Allocation
   ↓
Constraint-Aware Allocation
   ↓
Local Optimization
   ↓
Save Allocation
   ↓
Visual Seat Map
```

The allocation request includes selected student IDs, a deterministic seed, maximum local-optimization iterations, and the user/system performing the operation.

## 16. Allocation Logic

The project logic defines a deterministic constraint-aware pipeline:

### Stage 0 — Preprocessing

Validate inputs, identify unavailable seats, and compute relevant student priority information.

### Stage 1 — Constrained Placement

Students with strict requirements, such as accessibility or conflict-related constraints, are placed first.

### Stage 2 — Seeded Initial Placement

Students are ordered deterministically and seats are filled using a seeded placement strategy with round-robin room distribution intended to improve programme dispersion.

### Stage 3 — Local Optimization

Bounded local search evaluates possible swaps to improve soft objectives without breaking hard constraints.

### Stage 4 — Delta Reallocation

For live changes, the project logic calls for minimal-diff reallocation that reduces total churn and can support manual override locks.

The current implementation exposes a delta reallocation endpoint and frontend workflow for changing an allocated student's seat while preserving the rest of the saved allocation where possible.

## 17. Constraints and Objectives

The project logic identifies these hard constraints:

- One student per seat per timeslot
- Seat capacity and room availability
- Accessibility seats for students with special needs
- No student assigned to overlapping examination sessions

The documented soft objectives include:

- Programme dispersion across rooms
- Minimizing adjacency of students from the same programme
- Balancing room utilization
- Minimizing student movement between published runs

Hard constraints are intended to be satisfied before soft optimization.

## 18. Visual Seat Map

The Allocations page provides a visual representation based on stored seat coordinates.

Seat states include:

- Available
- Allocated
- Occupied
- Accessibility

When an examination is selected, the map filters rooms using the examination's `allowed_rooms` configuration.

The current implementation provides visual seat-map review. The broader specification describes a full visual seat-map editor with drag/drop adjustments; that editing capability is not part of the current implemented scope.

## 19. Saved Allocations

Existing allocations can be loaded with:

```text
GET /allocations/{exam_id}
```

The application displays the student, seat, seat label, and room for each saved allocation.

## 20. Delta Reallocation

Delta reallocation is used when an existing examination allocation needs to change without rerunning the complete initial allocation workflow.

Frontend workflow:

```text
Saved Allocation
      ↓
Select Allocated Student
      ↓
View Current Seat
      ↓
Select Free Replacement Seat
      ↓
Submit Delta Reallocation
      ↓
Apply Delta Changes
      ↓
Update Allocation Records
      ↓
Create Audit Records
```

API endpoint:

```text
POST /allocations/delta/{exam_id}
```

Request structure:

```json
{
  "student_id": "STUDENT_ID",
  "new_seat_id": "SEAT_ID",
  "seed": 42,
  "assigned_by": "system"
}
```

The frontend filters replacement seats to allowed rooms and excludes seats already allocated or marked occupied.

The project logic additionally describes graph-matching/minimal-churn strategies, constrained swaps, and manual override locks for a more advanced live-reallocation implementation. These advanced capabilities should be treated as future extensions unless implemented separately.

## 21. Audit Logs

Audit records are available through:

```text
GET /audit-logs/
```

The current implementation records allocation-related actions including:

```text
CREATE_ALLOCATION
DELTA_REALLOCATION
```

Delta records contain information such as:

```text
student=...
old_seat=...
new_seat=...
reason=...
```

The frontend provides:

- Total log count
- System-action count
- Allocation count
- Delta-change count
- Action filtering
- Human-readable delta change display
- Timestamp formatting

The project specification calls for an append-only audit store and reproducibility information such as seeds, traces, and allocation snapshots. The current implementation provides the audit-record foundation; broader forensic trace/snapshot infrastructure remains a future enhancement.

## 22. Testing

Run the backend test suite from the `backend` directory:

```powershell
pytest
```

Current verification:

```text
98 passed
2 warnings
```

The warnings did not cause test failures.

The frontend production build has also been verified successfully with:

```powershell
npm run build
```

## 23. Complete Implemented Workflow

```text
1. Start Backend
       ↓
2. Start Frontend
       ↓
3. Add / Import Students
       ↓
4. Create Rooms
       ↓
5. Generate Seats
       ↓
6. Create Examination
       ↓
7. Select Examination
       ↓
8. Select Students
       ↓
9. Run Allocation
       ↓
10. Review Visual Seat Map
       ↓
11. Load Saved Allocation When Required
       ↓
12. Perform Delta Reallocation When Required
       ↓
13. Review Audit Logs
```

## 24. Handover Notes

- The current SQLite database is intentionally free of fabricated institutional data.
- Use actual student, room, seat, and examination information for institutional use.
- Keep the backend virtual environment active when running backend commands.
- Start the backend before using the frontend.
- The current application uses SQLite for development.
- PostgreSQL can be introduced later for production deployment.
- Review environment configuration before deploying outside local development.
- Do not commit secrets, passwords, API keys, or private institutional data to Git.

## 25. Useful Commands

### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Backend tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

### Frontend development

```powershell
cd frontend
npm install
npm run dev
```

### Frontend production build

```powershell
cd frontend
npm run build
```

## 26. Specification Scope and Future Work

The SRS describes a broader institutional system. The following items are specified in the project documents but are not currently represented as completed frontend/backend features in this implementation:

- Role-based access for Admin, Scheduler, Invigilator, Student, and Auditor
- Full visual seat-map editing with drag/drop adjustments
- Configurable constraint weights through a UI
- Waitlist handling
- Manual override locks stored as exceptions
- Email/SMS/push notification pipeline
- PDF/PNG exports and iCal feeds
- Student admit cards with QR codes
- Invigilator rosters
- Utilization and conflict reporting dashboards
- SIS REST integration beyond the current CSV workflow
- Calendar integration
- Printing-kiosk integration
- Production-scale load testing
- Full decision traces, input checksums, and allocation snapshots
- Advanced graph-matching delta optimization and large-cohort partitioning/parallelization

These items are retained as future work rather than being described as already implemented.

## 27. Acceptance and Verification Notes

The project documents define acceptance goals including zero hard-constraint violations in pilot allocations, reproducible runs using a recorded seed, tracked manual edits, correct admit cards/rosters, and acceptable allocation performance at institutional scale.

The current development verification establishes:

- Backend automated test suite: **98 passed, 2 warnings**
- Frontend Vite production build: **successful**
- FastAPI Swagger/OpenAPI documentation: **available**
- Allocation API: **available**
- Delta Reallocation API: **available**
- Audit Logs API: **available**
- Visual Seat Map: **implemented**
- CSV student import/preview/export: **implemented**
- CSV room/seat/exam export: **implemented**

A full institutional pilot, representative-data validation, large-scale load test, and verification of all SRS acceptance items require the representative dataset and pilot process described in the project brief.

## Project Status

**Core development implementation complete for the current handover scope.**

The project is ready for final institutional data integration, deployment-specific configuration, and future implementation of the remaining specification-level features listed above.
