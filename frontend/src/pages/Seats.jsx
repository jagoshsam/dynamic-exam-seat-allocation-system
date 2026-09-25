import { useState } from "react"

import StatCard from "../components/StatCard"

import { downloadCsvTemplate } from "../utils/csv"

import {
  exportSeatsCsv,
  generateSeats,
} from "../api/seats"


function Seats({
  rooms,
  seats,
  loading,
  error,
  success,
  showForm,
  formData,
  setShowForm,
  handleChange,
  handleSubmit,
  loadSeats,
}) {

  const [exportLoading, setExportLoading] =
    useState(false)

  const [generateLoading, setGenerateLoading] =
    useState(false)

  const [selectedRoom, setSelectedRoom] =
    useState("")

  const [rows, setRows] =
    useState("")

  const [columns, setColumns] =
    useState("")

  const [generateError, setGenerateError] =
    useState("")

  const [generateSuccess, setGenerateSuccess] =
    useState("")


  // =========================================================
  // Download CSV Template
  // =========================================================

  function handleDownloadTemplate() {

    downloadCsvTemplate(
      "seats_template.csv",
      [
        "seat_id",
        "label",
        "x_coordinate",
        "y_coordinate",
        "accessibility_flag",
        "occupied_flag",
        "room_id",
      ]
    )

  }


  // =========================================================
  // Export Seats CSV
  // =========================================================

  async function handleExportCsv() {

    try {

      setExportLoading(true)

      await exportSeatsCsv()

    } catch (err) {

      console.error(
        "Seat CSV export failed:",
        err
      )

      alert(
        err.message ||
        "Failed to export seats CSV."
      )

    } finally {

      setExportLoading(false)

    }

  }


  // =========================================================
  // Generate Seats
  // =========================================================

  async function handleGenerateSeats(event) {

    event.preventDefault()

    setGenerateError("")
    setGenerateSuccess("")

    if (!selectedRoom) {

      setGenerateError(
        "Please select a room."
      )

      return

    }

    if (!rows || Number(rows) < 1) {

      setGenerateError(
        "Rows must be at least 1."
      )

      return

    }

    if (!columns || Number(columns) < 1) {

      setGenerateError(
        "Columns must be at least 1."
      )

      return

    }

    const room = rooms.find(
      (item) =>
        String(item.id) ===
        String(selectedRoom)
    )

    if (!room) {

      setGenerateError(
        "Selected room could not be found."
      )

      return

    }

    const totalSeats =
      Number(rows) *
      Number(columns)

    if (totalSeats > room.capacity) {

      setGenerateError(
        `Requested ${totalSeats} seats, but room capacity is ${room.capacity}.`
      )

      return

    }

    setGenerateLoading(true)

    try {

      const generatedSeats =
        await generateSeats(
          Number(selectedRoom),
          {
            rows: Number(rows),
            columns: Number(columns),
          }
        )

      setGenerateSuccess(
        `${generatedSeats.length} seats generated successfully for ${room.room_id}.`
      )

      setRows("")
      setColumns("")
      setSelectedRoom("")

      await loadSeats()

    } catch (err) {

      setGenerateError(
        err.message ||
        "Failed to generate seats."
      )

    } finally {

      setGenerateLoading(false)

    }

  }


  return (
    <div>

      {/* =====================================================
          Heading
      ===================================================== */}

      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

        <div>

          <p className="text-sm font-medium text-blue-600">
            Management
          </p>

          <h2 className="mt-1 text-3xl font-bold text-gray-900">
            Seats
          </h2>

          <p className="mt-2 text-gray-500">
            Manage individual examination seats.
          </p>

        </div>


        <div className="flex flex-wrap gap-3">

          {/* Export CSV */}

          <button
            type="button"
            onClick={handleExportCsv}
            disabled={exportLoading}
            className="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white shadow-sm hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {exportLoading
              ? "Exporting..."
              : "Export CSV"}
          </button>


          {/* Download CSV Template */}

          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="rounded-lg border border-gray-300 bg-white px-5 py-3 font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Download CSV Template
          </button>


          {/* Add Seat */}

          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white shadow-sm hover:bg-blue-700"
          >
            {showForm
              ? "Close Form"
              : "+ Add Seat"}
          </button>

        </div>

      </div>


      {/* =====================================================
          Error
      ===================================================== */}

      {error && (

        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">

          <p className="font-semibold">
            Error
          </p>

          <p className="mt-1 text-sm">
            {error}
          </p>

        </div>

      )}


      {/* =====================================================
          Success
      ===================================================== */}

      {success && (

        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-700">

          <p className="font-semibold">
            Success
          </p>

          <p className="mt-1 text-sm">
            {success}
          </p>

        </div>

      )}


      {/* =====================================================
          Generate Seats
      ===================================================== */}

      <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

        <div>

          <p className="text-sm font-medium text-blue-600">
            Automatic Seat Generation
          </p>

          <h3 className="mt-1 text-xl font-bold text-gray-900">
            Generate Seats for a Room
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Create a complete seat grid automatically using rows and columns.
          </p>

        </div>


        {generateError && (

          <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">

            <p className="font-semibold">
              Generation Error
            </p>

            <p className="mt-1 text-sm">
              {generateError}
            </p>

          </div>

        )}


        {generateSuccess && (

          <div className="mt-5 rounded-lg border border-green-200 bg-green-50 p-4 text-green-700">

            <p className="font-semibold">
              Generation Successful
            </p>

            <p className="mt-1 text-sm">
              {generateSuccess}
            </p>

          </div>

        )}


        <form
          onSubmit={handleGenerateSeats}
          className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-3"
        >

          {/* Room */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Room
            </label>

            <select
              value={selectedRoom}
              onChange={(event) => {
                setSelectedRoom(event.target.value)
                setGenerateError("")
                setGenerateSuccess("")
              }}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >

              <option value="">
                Select a room
              </option>

              {rooms.map((room) => (

                <option
                  key={room.id}
                  value={room.id}
                >
                  {room.room_id} — {room.building}
                </option>

              ))}

            </select>

            {rooms.length === 0 && (

              <p className="mt-2 text-xs text-red-500">
                No rooms are currently available.
              </p>

            )}

          </div>


          {/* Rows */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Rows
            </label>

            <input
              type="number"
              min="1"
              value={rows}
              onChange={(event) => {
                setRows(event.target.value)
                setGenerateError("")
              }}
              placeholder="Example: 5"
              required
              className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />

          </div>


          {/* Columns */}

          <div>

            <label className="mb-2 block text-sm font-medium text-gray-700">
              Columns
            </label>

            <input
              type="number"
              min="1"
              value={columns}
              onChange={(event) => {
                setColumns(event.target.value)
                setGenerateError("")
              }}
              placeholder="Example: 6"
              required
              className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />

          </div>


          {/* Capacity Information */}

          {selectedRoom && (

            <div className="md:col-span-3">

              {(() => {

                const room = rooms.find(
                  (item) =>
                    String(item.id) ===
                    String(selectedRoom)
                )

                if (!room) {
                  return null
                }

                const requestedSeats =
                  Number(rows || 0) *
                  Number(columns || 0)

                return (

                  <div className="rounded-lg bg-gray-50 p-4">

                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                      <div>

                        <p className="text-sm font-medium text-gray-700">
                          Room Capacity
                        </p>

                        <p className="text-2xl font-bold text-gray-900">
                          {room.capacity}
                        </p>

                      </div>


                      <div>

                        <p className="text-sm font-medium text-gray-700">
                          Seats to Generate
                        </p>

                        <p className="text-2xl font-bold text-blue-600">
                          {requestedSeats}
                        </p>

                      </div>

                    </div>

                    {requestedSeats > room.capacity && (

                      <p className="mt-3 text-sm font-medium text-red-600">
                        Requested seats exceed the room capacity.
                      </p>

                    )}

                  </div>

                )

              })()}

            </div>

          )}


          {/* Generate Button */}

          <div className="md:col-span-3">

            <button
              type="submit"
              disabled={
                generateLoading ||
                rooms.length === 0
              }
              className="rounded-lg bg-purple-600 px-6 py-3 font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {generateLoading
                ? "Generating Seats..."
                : "Generate Seats"}
            </button>

          </div>

        </form>

      </div>


      {/* =====================================================
          Add Seat Form
      ===================================================== */}

      {showForm && (

        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h3 className="text-xl font-bold text-gray-900">
            Add Examination Seat
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Define the seat and its physical position.
          </p>


          <form
            onSubmit={handleSubmit}
            className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2"
          >

            {/* Seat ID */}

            <Input
              label="Seat ID"
              name="seat_id"
              value={formData.seat_id}
              onChange={handleChange}
              placeholder="Example: ROOM101-S01"
            />


            {/* Label */}

            <Input
              label="Seat Label"
              name="label"
              value={formData.label}
              onChange={handleChange}
              placeholder="Example: A1"
            />


            {/* X */}

            <Input
              label="X Coordinate"
              name="x_coordinate"
              type="number"
              value={formData.x_coordinate}
              onChange={handleChange}
              placeholder="Example: 1"
            />


            {/* Y */}

            <Input
              label="Y Coordinate"
              name="y_coordinate"
              type="number"
              value={formData.y_coordinate}
              onChange={handleChange}
              placeholder="Example: 1"
            />


            {/* Room */}

            <div>

              <label className="mb-2 block text-sm font-medium text-gray-700">
                Room
              </label>

              <select
                name="room_id"
                value={formData.room_id}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >

                <option value="">
                  Select a room
                </option>

                {rooms.map((room) => (

                  <option
                    key={room.id}
                    value={room.id}
                  >
                    {room.room_id} — {room.building}
                  </option>

                ))}

              </select>

              {rooms.length === 0 && (

                <p className="mt-2 text-xs text-red-500">
                  No rooms are currently available.
                </p>

              )}

            </div>


            {/* Accessibility */}

            <div>

              <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-4">

                <input
                  type="checkbox"
                  name="accessibility_flag"
                  checked={
                    formData.accessibility_flag
                  }
                  onChange={handleChange}
                  className="h-4 w-4"
                />

                <div>

                  <p className="font-medium text-gray-800">
                    Accessibility Seat
                  </p>

                  <p className="text-xs text-gray-500">
                    Suitable for students with accessibility requirements.
                  </p>

                </div>

              </label>

            </div>


            {/* Occupied */}

            <div>

              <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-4">

                <input
                  type="checkbox"
                  name="occupied_flag"
                  checked={
                    formData.occupied_flag
                  }
                  onChange={handleChange}
                  className="h-4 w-4"
                />

                <div>

                  <p className="font-medium text-gray-800">
                    Occupied
                  </p>

                  <p className="text-xs text-gray-500">
                    Mark this seat as unavailable.
                  </p>

                </div>

              </label>

            </div>


            {/* Buttons */}

            <div className="flex gap-3 md:col-span-2">

              <button
                type="submit"
                disabled={rooms.length === 0}
                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                Save Seat
              </button>

              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>

            </div>

          </form>

        </div>

      )}


      {/* =====================================================
          Statistics
      ===================================================== */}

      <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">

        <StatCard
          label="Total Seats"
          value={seats.length}
        />

        <StatCard
          label="Accessibility Seats"
          value={
            seats.filter(
              (seat) =>
                seat.accessibility_flag
            ).length
          }
        />

        <StatCard
          label="Occupied Seats"
          value={
            seats.filter(
              (seat) =>
                seat.occupied_flag
            ).length
          }
        />

      </div>


      {/* =====================================================
          Seat Records
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-5">

          <div>

            <h3 className="text-lg font-bold text-gray-900">
              Seat Records
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Seats currently stored in the database.
            </p>

          </div>


          <button
            onClick={loadSeats}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>

        </div>


        {loading ? (

          <div className="px-6 py-12 text-center text-gray-500">
            Loading seats...
          </div>

        ) : seats.length === 0 ? (

          <div className="px-6 py-16 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-2xl">
              💺
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              No seats found
            </h4>

            <p className="mt-2 text-sm text-gray-500">
              Your database currently contains no seats.
            </p>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="bg-gray-50">

                <tr className="border-b border-gray-200">

                  <TH>
                    Seat ID
                  </TH>

                  <TH>
                    Label
                  </TH>

                  <TH>
                    Room
                  </TH>

                  <TH>
                    Position
                  </TH>

                  <TH>
                    Accessibility
                  </TH>

                  <TH>
                    Status
                  </TH>

                </tr>

              </thead>


              <tbody>

                {seats.map((seat) => {

                  const room = rooms.find(
                    (item) =>
                      item.id ===
                      seat.room_id
                  )


                  return (

                    <tr
                      key={seat.id}
                      className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                    >

                      <td className="px-6 py-4 font-medium text-gray-900">
                        {seat.seat_id}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {seat.label}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        {room?.room_id ||
                          seat.room_id}
                      </td>

                      <td className="px-6 py-4 text-gray-700">
                        (
                        {seat.x_coordinate},{" "}
                        {seat.y_coordinate}
                        )
                      </td>

                      <td className="px-6 py-4">

                        {seat.accessibility_flag ? (

                          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                            Accessible
                          </span>

                        ) : (

                          <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
                            Standard
                          </span>

                        )}

                      </td>

                      <td className="px-6 py-4">

                        {seat.occupied_flag ? (

                          <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700">
                            Occupied
                          </span>

                        ) : (

                          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                            Available
                          </span>

                        )}

                      </td>

                    </tr>

                  )

                })}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  )
}


/* =========================================================
   Input
========================================================= */

function Input({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder,
}) {

  return (

    <div>

      <label className="mb-2 block text-sm font-medium text-gray-700">
        {label}
      </label>

      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required
        min={
          type === "number"
            ? "0"
            : undefined
        }
        className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />

    </div>

  )
}


/* =========================================================
   Table Header
========================================================= */

function TH({
  children,
}) {

  return (

    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
      {children}
    </th>

  )

}


export default Seats