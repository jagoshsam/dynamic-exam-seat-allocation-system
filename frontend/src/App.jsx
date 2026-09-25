import { useEffect, useState } from "react"

import Sidebar from "./components/Sidebar"
import Header from "./components/Header"

import Dashboard from "./pages/Dashboard"
import Students from "./pages/Students"
import Rooms from "./pages/Rooms"
import Seats from "./pages/Seats"
import Exams from "./pages/Exams"
import Allocations from "./pages/Allocations"
import AuditLogs from "./pages/AuditLogs"

import {
  getRooms,
  createRoom,
} from "./api/rooms"

import {
  getSeats,
  createSeat,
} from "./api/seats"


function App() {
  // =========================================================
  // Navigation
  // =========================================================

  const [activePage, setActivePage] =
    useState("dashboard")


  // =========================================================
  // Rooms
  // =========================================================

  const [rooms, setRooms] = useState([])
  const [roomsLoading, setRoomsLoading] =
    useState(true)

  const [roomsError, setRoomsError] =
    useState("")

  const [roomsSuccess, setRoomsSuccess] =
    useState("")

  const [showRoomForm, setShowRoomForm] =
    useState(false)

  const [roomFormData, setRoomFormData] =
    useState({
      room_id: "",
      building: "",
      floor: "",
      capacity: "",
    })


  // =========================================================
  // Seats
  // =========================================================

  const [seats, setSeats] = useState([])
  const [seatsLoading, setSeatsLoading] =
    useState(true)

  const [seatsError, setSeatsError] =
    useState("")

  const [seatsSuccess, setSeatsSuccess] =
    useState("")

  const [showSeatForm, setShowSeatForm] =
    useState(false)

  const [seatFormData, setSeatFormData] =
    useState({
      seat_id: "",
      label: "",
      x_coordinate: "",
      y_coordinate: "",
      room_id: "",
      accessibility_flag: false,
      occupied_flag: false,
    })


  // =========================================================
  // Load Rooms
  // =========================================================

  async function loadRooms() {
    try {
      setRoomsLoading(true)
      setRoomsError("")

      const data = await getRooms()

      setRooms(data)

    } catch (err) {
      setRoomsError(err.message)

    } finally {
      setRoomsLoading(false)
    }
  }


  // =========================================================
  // Load Seats
  // =========================================================

  async function loadSeats() {
    try {
      setSeatsLoading(true)
      setSeatsError("")

      const data = await getSeats()

      setSeats(data)

    } catch (err) {
      setSeatsError(err.message)

    } finally {
      setSeatsLoading(false)
    }
  }


  // =========================================================
  // Initial Load
  // =========================================================

  useEffect(() => {
    loadRooms()
    loadSeats()
  }, [])


  // =========================================================
  // Room Form Change
  // =========================================================

  function handleRoomChange(event) {
    const {
      name,
      value,
    } = event.target

    setRoomFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }


  // =========================================================
  // Create Room
  // =========================================================

  async function handleRoomSubmit(event) {
    event.preventDefault()

    setRoomsError("")
    setRoomsSuccess("")

    try {
      await createRoom({
        room_id:
          roomFormData.room_id,

        building:
          roomFormData.building,

        floor:
          Number(roomFormData.floor),

        capacity:
          Number(roomFormData.capacity),
      })

      setRoomsSuccess(
        "Room created successfully."
      )

      setRoomFormData({
        room_id: "",
        building: "",
        floor: "",
        capacity: "",
      })

      setShowRoomForm(false)

      await loadRooms()

    } catch (err) {
      setRoomsError(err.message)
    }
  }


  // =========================================================
  // Seat Form Change
  // =========================================================

  function handleSeatChange(event) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target

    setSeatFormData((previous) => ({
      ...previous,
      [name]:
        type === "checkbox"
          ? checked
          : value,
    }))
  }


  // =========================================================
  // Create Seat
  // =========================================================

  async function handleSeatSubmit(event) {
    event.preventDefault()

    setSeatsError("")
    setSeatsSuccess("")

    try {
      await createSeat({
        seat_id:
          seatFormData.seat_id,

        label:
          seatFormData.label,

        x_coordinate:
          Number(
            seatFormData.x_coordinate
          ),

        y_coordinate:
          Number(
            seatFormData.y_coordinate
          ),

        accessibility_flag:
          seatFormData.accessibility_flag,

        occupied_flag:
          seatFormData.occupied_flag,

        room_id:
          Number(
            seatFormData.room_id
          ),
      })

      setSeatsSuccess(
        "Seat created successfully."
      )

      setSeatFormData({
        seat_id: "",
        label: "",
        x_coordinate: "",
        y_coordinate: "",
        room_id: "",
        accessibility_flag: false,
        occupied_flag: false,
      })

      setShowSeatForm(false)

      await loadSeats()
      await loadRooms()

    } catch (err) {
      setSeatsError(err.message)
    }
  }


  // =========================================================
  // Page Titles
  // =========================================================

  const pageTitles = {
    dashboard: "Dashboard",
    students: "Students",
    rooms: "Rooms",
    seats: "Seats",
    exams: "Exams",
    allocations: "Allocations",
    audit: "Audit Logs",
  }


  // =========================================================
  // Render Page
  // =========================================================

  function renderPage() {
    switch (activePage) {

      case "students":
        return <Students />

      case "rooms":
        return (
          <Rooms
            rooms={rooms}
            loading={roomsLoading}
            error={roomsError}
            success={roomsSuccess}
            showForm={showRoomForm}
            formData={roomFormData}
            setShowForm={setShowRoomForm}
            handleChange={handleRoomChange}
            handleSubmit={handleRoomSubmit}
            loadRooms={loadRooms}
          />
        )

      case "seats":
        return (
          <Seats
            rooms={rooms}
            seats={seats}
            loading={seatsLoading}
            error={seatsError}
            success={seatsSuccess}
            showForm={showSeatForm}
            formData={seatFormData}
            setShowForm={setShowSeatForm}
            handleChange={handleSeatChange}
            handleSubmit={handleSeatSubmit}
            loadSeats={loadSeats}
          />
        )

      case "exams":
        return <Exams />

      case "allocations":
        return <Allocations />

      case "audit":
        return <AuditLogs />

      case "dashboard":
      default:
        return <Dashboard />
    }
  }


  return (
    <div className="min-h-screen bg-gray-50">

      {/* =====================================================
          Sidebar
      ===================================================== */}

      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
      />


      {/* =====================================================
          Main Area
      ===================================================== */}

      <div className="lg:pl-64">

        <Header
          title={
            pageTitles[activePage]
          }
        />


        <main className="px-6 py-8 lg:px-8">

          {renderPage()}

        </main>

      </div>

    </div>
  )
}


export default App