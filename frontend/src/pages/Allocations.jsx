import { useEffect, useState } from "react"

import { getExams } from "../api/exams"
import { getStudents } from "../api/students"

import {
  runAllocation,
  getAllocation,
  deltaReallocation,
} from "../api/allocations"

import { getSeats } from "../api/seats"
import { getRooms } from "../api/rooms"

import StatCard from "../components/StatCard"


function Allocations() {
  const [exams, setExams] = useState([])
  const [students, setStudents] = useState([])
  const [seats, setSeats] = useState([])
  const [rooms, setRooms] = useState([])

  const [selectedExam, setSelectedExam] = useState("")
  const [selectedStudents, setSelectedStudents] = useState([])

  const [seed, setSeed] = useState(42)
  const [maxIterations, setMaxIterations] = useState(100)

  const [allocations, setAllocations] = useState([])

  const [deltaStudentId, setDeltaStudentId] = useState("")
  const [deltaSeatId, setDeltaSeatId] = useState("")
  const [deltaRunning, setDeltaRunning] = useState(false)
  const [deltaError, setDeltaError] = useState("")
  const [deltaSuccess, setDeltaSuccess] = useState("")

  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")


  // =========================================================
  // LOAD DATA
  // =========================================================

  async function loadData() {
    try {
      setLoading(true)
      setError("")

      const [
        examsData,
        studentsData,
        seatsData,
        roomsData,
      ] = await Promise.all([
        getExams(),
        getStudents(),
        getSeats(),
        getRooms(),
      ])

      setExams(examsData)
      setStudents(studentsData)
      setSeats(seatsData)
      setRooms(roomsData)

    } catch (err) {
      setError(err.message)

    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadData()
  }, [])


  // =========================================================
  // STUDENT SELECTION
  // =========================================================

  function toggleStudent(studentId) {
    setSelectedStudents((previous) => {
      if (previous.includes(studentId)) {
        return previous.filter(
          (id) => id !== studentId
        )
      }

      return [
        ...previous,
        studentId,
      ]
    })
  }


  function selectAllStudents() {
    setSelectedStudents(
      students.map(
        (student) => student.student_id
      )
    )
  }


  function clearStudents() {
    setSelectedStudents([])
  }


  // =========================================================
  // RUN ALLOCATION
  // =========================================================

  async function handleRunAllocation() {
    setError("")
    setSuccess("")

    if (!selectedExam) {
      setError(
        "Please select an examination first."
      )
      return
    }

    if (selectedStudents.length === 0) {
      setError(
        "Please select at least one student."
      )
      return
    }

    setRunning(true)

    try {
      const result = await runAllocation(
        selectedExam,
        {
          student_ids: selectedStudents,
          seed: Number(seed),
          max_iterations: Number(maxIterations),
          assigned_by: "system",
        }
      )

      setAllocations(
        result.allocations || []
      )

      setDeltaStudentId("")
      setDeltaSeatId("")
      setDeltaError("")
      setDeltaSuccess("")

      setSuccess(
        `Allocation completed successfully. ${result.allocation_count} students assigned.`
      )

    } catch (err) {
      setError(err.message)

    } finally {
      setRunning(false)
    }
  }


  // =========================================================
  // LOAD SAVED ALLOCATION
  // =========================================================

  async function handleLoadAllocation() {
    setError("")
    setSuccess("")
    setDeltaError("")
    setDeltaSuccess("")

    if (!selectedExam) {
      setError(
        "Please select an examination first."
      )
      return
    }

    try {
      const result = await getAllocation(
        selectedExam
      )

      setAllocations(
        result.allocations || []
      )

      setDeltaStudentId("")
      setDeltaSeatId("")

      setSuccess(
        "Saved allocation loaded successfully."
      )

    } catch (err) {
      setError(err.message)
    }
  }


  // =========================================================
  // SELECTED EXAM
  // =========================================================

  const selectedExamData = exams.find(
    (exam) => exam.exam_id === selectedExam
  )


  // =========================================================
  // ALLOWED ROOMS
  // =========================================================

  const allowedRoomIds = selectedExamData
    ? selectedExamData.allowed_rooms
        .split(",")
        .map((roomId) => roomId.trim())
        .filter(Boolean)
    : []


  // =========================================================
  // ROOM LOOKUP
  // =========================================================

  const roomLookup = new Map(
    rooms.map((room) => [
      String(room.id),
      room.room_id,
    ])
  )


  // =========================================================
  // ALLOCATION SEAT LOOKUP
  // =========================================================

  const allocationBySeat = new Map(
    allocations.map(
      (allocation) => [
        allocation.seat_id,
        allocation,
      ]
    )
  )


  // =========================================================
  // GROUP SEATS BY ROOM
  // =========================================================

  const seatsByRoom = seats.reduce(
    (groups, seat) => {
      const roomId = seat.room_id

      if (!groups[roomId]) {
        groups[roomId] = []
      }

      groups[roomId].push(seat)

      return groups
    },
    {}
  )


  // =========================================================
  // FILTER ROOMS FOR SELECTED EXAM
  // =========================================================

  const roomGroups = Object.entries(
    seatsByRoom
  )
    .filter(([roomDatabaseId]) => {
      if (!selectedExamData) {
        return true
      }

      const publicRoomId =
        roomLookup.get(
          String(roomDatabaseId)
        )

      return allowedRoomIds.includes(
        publicRoomId
      )
    })
    .sort(([roomA], [roomB]) =>
      roomA.localeCompare(roomB)
    )


  // =========================================================
  // DELTA REALLOCATION DATA
  // =========================================================

  const allocatedStudents = allocations.map(
    (allocation) =>
      allocation.student_id
  )


  const selectedDeltaAllocation =
    allocations.find(
      (allocation) =>
        allocation.student_id ===
        deltaStudentId
    )


  const allocatedSeatIds = new Set(
    allocations.map(
      (allocation) =>
        allocation.seat_id
    )
  )


  const availableDeltaSeats =
    seats.filter((seat) => {
      const publicRoomId =
        roomLookup.get(
          String(seat.room_id)
        )

      const isAllowedRoom =
        selectedExamData
          ? allowedRoomIds.includes(
              publicRoomId
            )
          : true

      const isAllocated =
        allocatedSeatIds.has(
          seat.seat_id
        )

      return (
        isAllowedRoom &&
        !seat.occupied_flag &&
        !isAllocated
      )
    })


  // =========================================================
  // DELTA REALLOCATION
  // =========================================================

  async function handleDeltaReallocation() {
    setDeltaError("")
    setDeltaSuccess("")
    setError("")
    setSuccess("")

    if (!selectedExam) {
      setDeltaError(
        "Please select an examination first."
      )
      return
    }

    if (allocations.length === 0) {
      setDeltaError(
        "Load or create an allocation before reallocating a seat."
      )
      return
    }

    if (!deltaStudentId) {
      setDeltaError(
        "Please select a student."
      )
      return
    }

    if (!deltaSeatId) {
      setDeltaError(
        "Please select a replacement seat."
      )
      return
    }

    if (
      selectedDeltaAllocation?.seat_id ===
      deltaSeatId
    ) {
      setDeltaError(
        "The selected seat is already assigned to this student."
      )
      return
    }

    if (
      allocatedSeatIds.has(deltaSeatId)
    ) {
      setDeltaError(
        "The selected seat is already allocated to another student."
      )
      return
    }

    setDeltaRunning(true)

    try {
      const result =
        await deltaReallocation(
          selectedExam,
          {
            student_id:
              deltaStudentId,

            new_seat_id:
              deltaSeatId,

            seed: Number(seed),

            assigned_by:
              "system",
          }
        )


      // =====================================================
      // UPDATE LOCAL ALLOCATION STATE
      // =====================================================

      const updatedAllocation =
        allocations.map(
          (allocation) => {

            const change =
              (result.changes || []).find(
                (item) =>
                  item.student_id ===
                  allocation.student_id
              )

            if (!change) {
              return allocation
            }

            const newSeat =
              seats.find(
                (seat) =>
                  seat.seat_id ===
                  change.new_seat_id
              )

            if (!newSeat) {
              return allocation
            }

            return {
              ...allocation,

              seat_id:
                newSeat.seat_id,

              seat_label:
                newSeat.label,

              room_id:
                roomLookup.get(
                  String(
                    newSeat.room_id
                  )
                ) ||
                allocation.room_id,
            }
          }
        )


      setAllocations(
        updatedAllocation
      )


      const changedCount =
        result.changed_count || 0


      setDeltaSuccess(
        `Delta reallocation completed successfully. ${changedCount} student${changedCount === 1 ? "" : "s"} changed.`
      )


      setDeltaStudentId("")
      setDeltaSeatId("")

    } catch (err) {
      setDeltaError(
        err.message
      )

    } finally {
      setDeltaRunning(false)
    }
  }


  return (
    <div>

      {/* =====================================================
          HEADING
      ===================================================== */}

      <div>

        <p className="text-sm font-medium text-blue-600">
          Allocation Engine
        </p>

        <h2 className="mt-1 text-3xl font-bold text-gray-900">
          Allocations
        </h2>

        <p className="mt-2 text-gray-500">
          Generate deterministic, constraint-aware examination seating.
        </p>

      </div>


      {/* =====================================================
          GENERAL SUCCESS MESSAGE
      ===================================================== */}

      {success && (
        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4">

          <p className="font-medium text-green-700">
            {success}
          </p>

        </div>
      )}


      {/* =====================================================
          GENERAL ERROR MESSAGE
      ===================================================== */}

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">

          <p className="font-semibold text-red-700">
            Allocation Error
          </p>

          <p className="mt-1 text-sm text-red-600">
            {error}
          </p>

        </div>
      )}


      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-4">

        <StatCard
          label="Available Exams"
          value={exams.length}
        />

        <StatCard
          label="Available Students"
          value={students.length}
        />

        <StatCard
          label="Available Seats"
          value={seats.length}
        />

        <StatCard
          label="Allocated Students"
          value={allocations.length}
          green
        />

      </div>


      {/* =====================================================
          ALLOCATION CONFIGURATION
      ===================================================== */}

      <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

        <div>

          <h3 className="text-xl font-bold text-gray-900">
            Allocation Configuration
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Select an examination and students for the allocation run.
          </p>

        </div>


        <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">

          {/* EXAM */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Examination
            </label>

            <select
              value={selectedExam}
              onChange={(event) => {

                setSelectedExam(
                  event.target.value
                )

                setAllocations([])

                setSelectedStudents([])

                setDeltaStudentId("")

                setDeltaSeatId("")

                setDeltaError("")

                setDeltaSuccess("")

                setSuccess("")

                setError("")

              }}
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3"
            >

              <option value="">
                Select examination
              </option>

              {exams.map((exam) => (

                <option
                  key={exam.id}
                  value={exam.exam_id}
                >
                  {exam.exam_id} — {exam.course_code}
                </option>

              ))}

            </select>

          </div>


          {/* SEED */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Random Seed
            </label>

            <input
              type="number"
              value={seed}
              onChange={(event) =>
                setSeed(
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-gray-300 px-4 py-3"
            />

            <p className="mt-1 text-xs text-gray-500">
              Same seed + same input produces a reproducible allocation.
            </p>

          </div>


          {/* ITERATIONS */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Maximum Optimization Iterations
            </label>

            <input
              type="number"
              min="1"
              max="1000"
              value={maxIterations}
              onChange={(event) =>
                setMaxIterations(
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3"
            />

          </div>


          {/* SELECTED COUNT */}

          <div className="flex items-end">

            <div className="w-full rounded-lg bg-gray-50 p-4">

              <p className="text-sm text-gray-500">
                Selected Students
              </p>

              <p className="mt-1 text-2xl font-bold text-gray-900">
                {selectedStudents.length}
              </p>

            </div>

          </div>

        </div>


        {/* =================================================
            STUDENT SELECTION
        ================================================= */}

        <div className="mt-8">

          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">

            <div>

              <h4 className="font-semibold text-gray-900">
                Students
              </h4>

              <p className="text-sm text-gray-500">
                Choose students who should receive seats.
              </p>

            </div>


            <div className="flex gap-2">

              <button
                type="button"
                onClick={
                  selectAllStudents
                }
                disabled={
                  students.length === 0
                }
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Select All
              </button>


              <button
                type="button"
                onClick={
                  clearStudents
                }
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Clear
              </button>

            </div>

          </div>


          <div className="mt-4 max-h-72 overflow-y-auto rounded-lg border border-gray-200">

            {loading ? (

              <div className="p-8 text-center text-gray-500">
                Loading students...
              </div>

            ) : students.length === 0 ? (

              <div className="p-8 text-center text-gray-500">
                No students available.
              </div>

            ) : (

              <div>

                {students.map(
                  (student) => {

                    const selected =
                      selectedStudents.includes(
                        student.student_id
                      )

                    return (

                      <label
                        key={student.id}
                        className={`flex cursor-pointer items-center gap-4 border-b border-gray-100 px-5 py-4 last:border-0 ${
                          selected
                            ? "bg-blue-50"
                            : "hover:bg-gray-50"
                        }`}
                      >

                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() =>
                            toggleStudent(
                              student.student_id
                            )
                          }
                          className="h-4 w-4"
                        />


                        <div className="min-w-0 flex-1">

                          <p className="font-medium text-gray-900">
                            {student.name}
                          </p>

                          <p className="text-sm text-gray-500">
                            {student.student_id}
                            {" • "}
                            {student.programme}
                            {" • "}
                            Year {student.year}
                          </p>

                        </div>


                        {student.special_needs && (
                          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                            Accessibility
                          </span>
                        )}

                      </label>

                    )
                  }
                )}

              </div>

            )}

          </div>

        </div>


        {/* =================================================
            ACTION BUTTONS
        ================================================= */}

        <div className="mt-6 flex flex-wrap gap-3">

          <button
            onClick={
              handleRunAllocation
            }
            disabled={
              running ||
              loading ||
              !selectedExam ||
              selectedStudents.length === 0
            }
            className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {running
              ? "Running Allocation..."
              : "Run Allocation"}
          </button>


          <button
            onClick={
              handleLoadAllocation
            }
            disabled={
              loading ||
              !selectedExam
            }
            className="rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Load Saved Allocation
          </button>

        </div>

      </div>


      {/* =====================================================
          DELTA REALLOCATION
      ===================================================== */}

      <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

        <div>

          <p className="text-sm font-medium text-purple-600">
            Minimal-Churn Reallocation
          </p>

          <h3 className="mt-1 text-xl font-bold text-gray-900">
            Delta Reallocation
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Change a student's seat without regenerating the complete examination allocation.
          </p>

        </div>


        {/* DELTA SUCCESS */}

        {deltaSuccess && (
          <div className="mt-5 rounded-lg border border-green-200 bg-green-50 p-4">

            <p className="font-medium text-green-700">
              {deltaSuccess}
            </p>

          </div>
        )}


        {/* DELTA ERROR */}

        {deltaError && (
          <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4">

            <p className="font-semibold text-red-700">
              Delta Reallocation Error
            </p>

            <p className="mt-1 text-sm text-red-600">
              {deltaError}
            </p>

          </div>
        )}


        {/* NO ALLOCATION */}

        {allocations.length === 0 ? (

          <div className="mt-6 rounded-lg bg-gray-50 p-5 text-center">

            <p className="font-medium text-gray-700">
              No saved allocation available
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Run an allocation or load a saved allocation before using delta reallocation.
            </p>

          </div>

        ) : (

          <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-3">

            {/* STUDENT */}

            <div>

              <label className="mb-2 block text-sm font-medium text-gray-700">
                Student
              </label>

              <select
                value={deltaStudentId}
                onChange={(event) => {

                  setDeltaStudentId(
                    event.target.value
                  )

                  setDeltaSeatId("")

                  setDeltaError("")

                  setDeltaSuccess("")

                }}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3"
              >

                <option value="">
                  Select allocated student
                </option>

                {allocatedStudents.map(
                  (studentId) => {

                    const allocation =
                      allocations.find(
                        (item) =>
                          item.student_id ===
                          studentId
                      )

                    return (

                      <option
                        key={studentId}
                        value={studentId}
                      >
                        {studentId} —{" "}
                        {allocation?.student_name ||
                          "Student"}
                      </option>

                    )
                  }
                )}

              </select>

            </div>


            {/* CURRENT SEAT */}

            <div>

              <label className="mb-2 block text-sm font-medium text-gray-700">
                Current Seat
              </label>

              <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">

                {selectedDeltaAllocation ? (

                  <>

                    <p className="font-semibold text-gray-900">
                      {selectedDeltaAllocation.seat_id}
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      {selectedDeltaAllocation.room_id}
                      {" • "}
                      {selectedDeltaAllocation.seat_label}
                    </p>

                  </>

                ) : (

                  <p className="text-sm text-gray-500">
                    Select a student
                  </p>

                )}

              </div>

            </div>


            {/* REPLACEMENT SEAT */}

            <div>

              <label className="mb-2 block text-sm font-medium text-gray-700">
                Replacement Seat
              </label>

              <select
                value={deltaSeatId}
                onChange={(event) => {

                  setDeltaSeatId(
                    event.target.value
                  )

                  setDeltaError("")

                  setDeltaSuccess("")

                }}
                disabled={
                  !deltaStudentId ||
                  availableDeltaSeats.length === 0
                }
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 disabled:cursor-not-allowed disabled:bg-gray-100"
              >

                <option value="">
                  Select replacement seat
                </option>

                {availableDeltaSeats.map(
                  (seat) => (

                    <option
                      key={seat.seat_id}
                      value={seat.seat_id}
                    >
                      {seat.seat_id}
                      {" — "}
                      {seat.label}
                      {" — "}
                      {roomLookup.get(
                        String(
                          seat.room_id
                        )
                      ) || seat.room_id}
                    </option>

                  )
                )}

              </select>

            </div>

          </div>
        )}


        {/* DELTA ACTION */}

        {allocations.length > 0 && (

          <div className="mt-5 flex flex-col gap-3 rounded-lg bg-purple-50 p-4 md:flex-row md:items-center md:justify-between">

            <div>

              <p className="text-sm font-semibold text-purple-900">
                Minimal-churn change
              </p>

              <p className="mt-1 text-xs text-purple-700">
                Only the affected allocation changes are submitted to the delta engine.
              </p>

            </div>


            <button
              type="button"
              onClick={
                handleDeltaReallocation
              }
              disabled={
                deltaRunning ||
                !selectedExam ||
                !deltaStudentId ||
                !deltaSeatId
              }
              className="rounded-lg bg-purple-600 px-6 py-3 font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {deltaRunning
                ? "Reallocating..."
                : "Reallocate Student"}
            </button>

          </div>

        )}


        {/* NO FREE SEATS */}

        {selectedExamData &&
          allocations.length > 0 &&
          availableDeltaSeats.length === 0 && (

            <p className="mt-4 text-sm text-yellow-700">
              No free replacement seats are currently available in the selected examination's allowed rooms.
            </p>

          )}

      </div>


      {/* =====================================================
          VISUAL SEAT MAP
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="border-b border-gray-200 px-6 py-5">

          <h3 className="text-lg font-bold text-gray-900">
            Visual Seat Map
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Seat positions and allocation status based on stored seat coordinates.
          </p>

        </div>


        {seats.length === 0 ? (

          <div className="px-6 py-16 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-2xl">
              💺
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              No seats available
            </h4>

            <p className="mt-2 text-sm text-gray-500">
              Add rooms and generate seats before viewing the seat map.
            </p>

          </div>

        ) : (

          <div className="p-6">

            {selectedExamData &&
              roomGroups.length === 0 && (

                <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-5">

                  <p className="font-semibold text-yellow-800">
                    No allowed rooms available
                  </p>

                  <p className="mt-1 text-sm text-yellow-700">
                    The selected examination allows:
                    {" "}
                    {allowedRoomIds.join(", ")}
                    {" "}
                    but no matching seats were found.
                  </p>

                </div>

              )}


            {/* LEGEND */}

            <div className="mb-6 flex flex-wrap gap-4">

              <Legend
                label="Available"
                className="bg-green-100 border-green-200"
              />

              <Legend
                label="Allocated"
                className="bg-blue-100 border-blue-200"
              />

              <Legend
                label="Occupied"
                className="bg-red-100 border-red-200"
              />

              <Legend
                label="Accessibility"
                className="bg-purple-100 border-purple-200"
              />

            </div>


            {/* ROOMS */}

            <div className="space-y-8">

              {roomGroups.map(
                ([roomId, roomSeats]) => {

                  const sortedSeats =
                    [...roomSeats].sort(
                      (a, b) => {

                        if (
                          a.y_coordinate !==
                          b.y_coordinate
                        ) {
                          return (
                            a.y_coordinate -
                            b.y_coordinate
                          )
                        }

                        return (
                          a.x_coordinate -
                          b.x_coordinate
                        )

                      }
                    )


                  const maxX =
                    Math.max(
                      ...sortedSeats.map(
                        (seat) =>
                          seat.x_coordinate
                      ),
                      1
                    )


                  return (

                    <div
                      key={roomId}
                      className="rounded-xl border border-gray-200 bg-gray-50 p-5"
                    >

                      <div className="mb-5 flex items-center justify-between">

                        <div>

                          <h4 className="text-lg font-bold text-gray-900">
                            Room{" "}
                            {roomLookup.get(
                              String(roomId)
                            ) || roomId}
                          </h4>

                          <p className="text-sm text-gray-500">
                            {sortedSeats.length} seats
                          </p>

                        </div>

                      </div>


                      <div
                        className="grid gap-3 overflow-x-auto"
                        style={{
                          gridTemplateColumns:
                            `repeat(${maxX}, minmax(90px, 1fr))`,
                        }}
                      >

                        {sortedSeats.map(
                          (seat) => {

                            const allocation =
                              allocationBySeat.get(
                                seat.seat_id
                              )


                            let seatClass =
                              "border-gray-200 bg-green-50 text-green-700"


                            if (
                              seat.occupied_flag
                            ) {

                              seatClass =
                                "border-red-200 bg-red-50 text-red-700"

                            } else if (
                              allocation
                            ) {

                              seatClass =
                                "border-blue-200 bg-blue-50 text-blue-700"

                            } else if (
                              seat.accessibility_flag
                            ) {

                              seatClass =
                                "border-purple-200 bg-purple-50 text-purple-700"

                            }


                            return (

                              <div
                                key={seat.seat_id}
                                className={`min-h-[95px] rounded-xl border-2 p-3 ${seatClass}`}
                              >

                                <div className="flex items-center justify-between">

                                  <span className="text-xs font-semibold">
                                    {seat.label}
                                  </span>

                                  <span className="text-xs">
                                    (
                                    {seat.x_coordinate}
                                    ,{" "}
                                    {seat.y_coordinate}
                                    )
                                  </span>

                                </div>


                                <p className="mt-3 text-sm font-bold">

                                  {allocation
                                    ? allocation.student_id
                                    : seat.occupied_flag
                                      ? "Occupied"
                                      : "Available"}

                                </p>


                                {allocation && (

                                  <p className="mt-1 truncate text-xs">
                                    {allocation.student_name}
                                  </p>

                                )}

                              </div>

                            )

                          }
                        )}

                      </div>

                    </div>

                  )

                }
              )}

            </div>

          </div>

        )}

      </div>


      {/* =====================================================
          ALLOCATION RESULTS
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="border-b border-gray-200 px-6 py-5">

          <h3 className="text-lg font-bold text-gray-900">
            Allocation Results
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Seat assignments generated by the allocation engine.
          </p>

        </div>


        {allocations.length === 0 ? (

          <div className="px-6 py-16 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-2xl">
              🎯
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              No allocation results
            </h4>

            <p className="mt-2 text-sm text-gray-500">
              Select an examination and students, then run the allocation.
            </p>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="bg-gray-50">

                <tr className="border-b border-gray-200">

                  <TH>Student ID</TH>
                  <TH>Student Name</TH>
                  <TH>Seat ID</TH>
                  <TH>Seat Label</TH>
                  <TH>Room</TH>

                </tr>

              </thead>


              <tbody>

                {allocations.map(
                  (allocation, index) => (

                    <tr
                      key={`${allocation.student_id}-${index}`}
                      className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                    >

                      <td className="px-6 py-4 font-medium text-gray-900">
                        {allocation.student_id}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {allocation.student_name}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {allocation.seat_id}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {allocation.seat_label}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {allocation.room_id}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  )
}


/* =========================================================
   LEGEND
========================================================= */

function Legend({
  label,
  className,
}) {

  return (

    <div className="flex items-center gap-2">

      <span
        className={`h-4 w-4 rounded border ${className}`}
      />

      <span className="text-sm text-gray-600">
        {label}
      </span>

    </div>

  )
}


/* =========================================================
   TABLE HEADER
========================================================= */

function TH({ children }) {

  return (

    <th className="px-6 py-3 text-left text-xs font-semibold uppercase text-gray-500">
      {children}
    </th>

  )
}


export default Allocations