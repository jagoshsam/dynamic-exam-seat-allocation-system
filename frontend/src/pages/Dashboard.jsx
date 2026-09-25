import { useEffect, useState } from "react"

import { getStudents } from "../api/students"
import { getRooms } from "../api/rooms"
import { getSeats } from "../api/seats"

import StatCard from "../components/StatCard"


function Dashboard() {
  const [students, setStudents] = useState([])
  const [rooms, setRooms] = useState([])
  const [seats, setSeats] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")


  async function loadDashboard() {
    try {
      setLoading(true)
      setError("")

      const [
        studentsData,
        roomsData,
        seatsData,
      ] = await Promise.all([
        getStudents(),
        getRooms(),
        getSeats(),
      ])

      setStudents(studentsData)
      setRooms(roomsData)
      setSeats(seatsData)

    } catch (err) {
      setError(err.message)

    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadDashboard()
  }, [])


  const accessibilitySeats =
    seats.filter(
      (seat) => seat.accessibility_flag
    ).length

  const occupiedSeats =
    seats.filter(
      (seat) => seat.occupied_flag
    ).length

  const totalCapacity =
    rooms.reduce(
      (total, room) =>
        total + Number(room.capacity || 0),
      0
    )


  return (
    <div>

      {/* Header */}

      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

        <div>

          <p className="text-sm font-medium text-blue-600">
            Overview
          </p>

          <h2 className="mt-1 text-3xl font-bold text-gray-900">
            Dashboard
          </h2>

          <p className="mt-2 text-gray-500">
            Overview of the examination seat allocation system.
          </p>

        </div>


        <button
          onClick={loadDashboard}
          className="rounded-lg border border-gray-300 bg-white px-5 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50"
        >
          Refresh Data
        </button>

      </div>


      {/* Error */}

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">

          <p className="font-semibold text-red-700">
            Unable to load dashboard
          </p>

          <p className="mt-1 text-sm text-red-600">
            {error}
          </p>

        </div>
      )}


      {/* Statistics */}

      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

        <StatCard
          label="Total Students"
          value={
            loading
              ? "..."
              : students.length
          }
        />

        <StatCard
          label="Total Rooms"
          value={
            loading
              ? "..."
              : rooms.length
          }
        />

        <StatCard
          label="Total Seats"
          value={
            loading
              ? "..."
              : seats.length
          }
        />

        <StatCard
          label="Occupied Seats"
          value={
            loading
              ? "..."
              : occupiedSeats
          }
        />

      </div>


      {/* Secondary Statistics */}

      <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-3">

        <StatCard
          label="Room Capacity"
          value={
            loading
              ? "..."
              : totalCapacity
          }
        />

        <StatCard
          label="Accessibility Seats"
          value={
            loading
              ? "..."
              : accessibilitySeats
          }
        />

        <StatCard
          label="API Status"
          value="Connected"
          green
        />

      </div>


      {/* System Overview */}

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">

        {/* Students */}

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm font-medium text-blue-600">
                Student Management
              </p>

              <h3 className="mt-1 text-xl font-bold text-gray-900">
                Students
              </h3>

            </div>

            <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
              {students.length}
            </span>

          </div>


          <p className="mt-4 text-sm leading-6 text-gray-500">
            Student records are stored in the examination database
            and can be imported using CSV files.
          </p>


          <div className="mt-5 rounded-lg bg-gray-50 p-4">

            <div className="flex justify-between text-sm">

              <span className="text-gray-500">
                Special needs
              </span>

              <span className="font-semibold text-gray-900">
                {
                  students.filter(
                    (student) =>
                      student.special_needs
                  ).length
                }
              </span>

            </div>

          </div>

        </div>


        {/* Rooms */}

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm font-medium text-blue-600">
                Infrastructure
              </p>

              <h3 className="mt-1 text-xl font-bold text-gray-900">
                Examination Rooms
              </h3>

            </div>

            <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
              {rooms.length}
            </span>

          </div>


          <p className="mt-4 text-sm leading-6 text-gray-500">
            Examination rooms define the available capacity for
            dynamic seat allocation.
          </p>


          <div className="mt-5 rounded-lg bg-gray-50 p-4">

            <div className="flex justify-between text-sm">

              <span className="text-gray-500">
                Total capacity
              </span>

              <span className="font-semibold text-gray-900">
                {totalCapacity}
              </span>

            </div>

          </div>

        </div>

      </div>


      {/* Seat Overview */}

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between">

          <div>

            <p className="text-sm font-medium text-blue-600">
              Seating Infrastructure
            </p>

            <h3 className="mt-1 text-xl font-bold text-gray-900">
              Seat Overview
            </h3>

          </div>

        </div>


        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">

          <OverviewItem
            label="Total Seats"
            value={seats.length}
          />

          <OverviewItem
            label="Accessibility Seats"
            value={accessibilitySeats}
          />

          <OverviewItem
            label="Occupied Seats"
            value={occupiedSeats}
          />

        </div>

      </div>


      {/* System Information */}

      <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-6">

        <h3 className="font-bold text-blue-900">
          Dynamic Examination Seat Allocation
        </h3>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-blue-800">
          The system manages students, examination rooms, seats,
          examinations and allocations through the backend API.
          The allocation engine will later use these records to
          generate deterministic, constraint-aware seating plans.
        </p>

      </div>

    </div>
  )
}


/* =========================================================
   Overview Item
========================================================= */

function OverviewItem({ label, value }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">

      <p className="text-sm text-gray-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-gray-900">
        {value}
      </p>

    </div>
  )
}


export default Dashboard