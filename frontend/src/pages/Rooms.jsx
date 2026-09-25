import { useState } from "react"

import StatCard from "../components/StatCard"

import { downloadCsvTemplate } from "../utils/csv"

import { exportRoomsCsv } from "../api/rooms"


function Rooms({
  rooms,
  loading,
  error,
  success,
  showForm,
  formData,
  setShowForm,
  handleChange,
  handleSubmit,
  loadRooms,
}) {

  const [exportLoading, setExportLoading] =
    useState(false)


  // =========================================================
  // Download CSV Template
  // =========================================================

  function handleDownloadTemplate() {

    downloadCsvTemplate(
      "rooms_template.csv",
      [
        "room_id",
        "building",
        "floor",
        "capacity",
      ]
    )

  }


  // =========================================================
  // Export Rooms CSV
  // =========================================================

  async function handleExportCsv() {

    try {

      setExportLoading(true)

      await exportRoomsCsv()

    } catch (err) {

      console.error(
        "Room CSV export failed:",
        err
      )

      alert(
        err.message ||
        "Failed to export rooms CSV."
      )

    } finally {

      setExportLoading(false)

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
            Rooms
          </h2>

          <p className="mt-2 text-gray-500">
            Manage examination rooms used for seat allocation.
          </p>

        </div>


        <div className="flex flex-wrap gap-3">

          {/* Export CSV */}

          <button
            type="button"
            onClick={handleExportCsv}
            disabled={exportLoading}
            className="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {exportLoading
              ? "Exporting..."
              : "Export CSV"}
          </button>


          {/* Download Template */}

          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="rounded-lg border border-gray-300 bg-white px-5 py-3 font-semibold text-gray-700 hover:bg-gray-50"
          >
            Download CSV Template
          </button>


          {/* Add Room */}

          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            {showForm
              ? "Close Form"
              : "+ Add Room"}
          </button>

        </div>

      </div>


      {/* =====================================================
          Messages
      ===================================================== */}

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}


      {success && (
        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-700">
          {success}
        </div>
      )}


      {/* =====================================================
          Add Room Form
      ===================================================== */}

      {showForm && (

        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h3 className="text-xl font-bold text-gray-900">
            Add Room
          </h3>

          <form
            onSubmit={handleSubmit}
            className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2"
          >

            <Input
              label="Room ID"
              name="room_id"
              value={formData.room_id}
              onChange={handleChange}
            />

            <Input
              label="Building"
              name="building"
              value={formData.building}
              onChange={handleChange}
            />

            <Input
              label="Floor"
              name="floor"
              type="number"
              value={formData.floor}
              onChange={handleChange}
            />

            <Input
              label="Capacity"
              name="capacity"
              type="number"
              value={formData.capacity}
              onChange={handleChange}
            />


            <div className="md:col-span-2 flex gap-3">

              <button
                type="submit"
                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
              >
                Save Room
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
          label="Total Rooms"
          value={rooms.length}
        />

        <StatCard
          label="Total Capacity"
          value={
            rooms.reduce(
              (t, r) =>
                t + Number(r.capacity || 0),
              0
            )
          }
        />

        <StatCard
          label="API Status"
          value="Connected"
          green
        />

      </div>


      {/* =====================================================
          Rooms Table
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-5">

          <h3 className="text-lg font-bold">
            Rooms
          </h3>

          <button
            onClick={loadRooms}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>

        </div>


        {loading ? (

          <div className="p-10 text-center text-gray-500">
            Loading...
          </div>

        ) : rooms.length === 0 ? (

          <div className="p-10 text-center text-gray-500">
            No rooms found
          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full">

              <thead className="bg-gray-50">

                <tr>

                  <TH>
                    Room
                  </TH>

                  <TH>
                    Building
                  </TH>

                  <TH>
                    Floor
                  </TH>

                  <TH>
                    Capacity
                  </TH>

                  <TH>
                    Seats
                  </TH>

                </tr>

              </thead>


              <tbody>

                {rooms.map((room) => (

                  <tr
                    key={room.id}
                    className="border-t border-gray-100"
                  >

                    <TD>
                      {room.room_id}
                    </TD>

                    <TD>
                      {room.building}
                    </TD>

                    <TD>
                      {room.floor}
                    </TD>

                    <TD>
                      {room.capacity}
                    </TD>

                    <TD>
                      {room.seats?.length ?? 0}
                    </TD>

                  </tr>

                ))}

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
  ...props
}) {

  return (
    <div>

      <label className="mb-2 block text-sm font-medium text-gray-700">
        {label}
      </label>

      <input
        {...props}
        required
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
    <th className="px-6 py-3 text-left text-xs font-semibold uppercase text-gray-500">
      {children}
    </th>
  )
}


/* =========================================================
   Table Data
========================================================= */

function TD({
  children,
}) {

  return (
    <td className="px-6 py-4">
      {children}
    </td>
  )
}


export default Rooms