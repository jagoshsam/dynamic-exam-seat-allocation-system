import { apiRequest } from "./client"


// =========================================================
// GET ALL SEATS
// =========================================================

export async function getSeats() {
  return apiRequest("/seats/")
}


// =========================================================
// CREATE SEAT
// =========================================================

export async function createSeat(seat) {
  return apiRequest("/seats/", {
    method: "POST",
    body: JSON.stringify(seat),
  })
}


// =========================================================
// GENERATE SEATS FOR A ROOM
// =========================================================

export async function generateSeats(roomId, data) {
  return apiRequest(
    `/seats/generate/${roomId}`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  )
}


// =========================================================
// GET SEATS OF A ROOM
// =========================================================

export async function getRoomSeats(roomId) {
  return apiRequest(
    `/seats/room/${roomId}`
  )
}


// =========================================================
// GET SINGLE SEAT
// =========================================================

export async function getSeat(seatId) {
  return apiRequest(
    `/seats/${seatId}`
  )
}


// =========================================================
// DELETE SEAT
// =========================================================

export async function deleteSeat(seatId) {
  return apiRequest(
    `/seats/${seatId}`,
    {
      method: "DELETE",
    }
  )
}


// =========================================================
// EXPORT SEATS TO CSV
// =========================================================

export async function exportSeatsCsv() {

  const response = await fetch(
    "http://127.0.0.1:8000/seats/export-csv"
  )

  if (!response.ok) {

    throw new Error(
      "Failed to export seats CSV"
    )

  }

  const blob = await response.blob()

  const url =
    window.URL.createObjectURL(blob)

  const link =
    document.createElement("a")

  link.href = url

  link.download =
    "seats_export.csv"

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}