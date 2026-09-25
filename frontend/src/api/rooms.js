import { apiRequest } from "./client"


// =========================================================
// GET ALL ROOMS
// =========================================================

export async function getRooms() {
  return apiRequest("/rooms/")
}


// =========================================================
// CREATE ROOM
// =========================================================

export async function createRoom(room) {
  return apiRequest("/rooms/", {
    method: "POST",
    body: JSON.stringify(room),
  })
}


// =========================================================
// EXPORT ROOMS TO CSV
// =========================================================

export async function exportRoomsCsv() {

  const response = await fetch(
    "http://127.0.0.1:8000/rooms/export-csv"
  )

  if (!response.ok) {

    throw new Error(
      "Failed to export rooms CSV"
    )

  }

  const blob = await response.blob()

  const url = window.URL.createObjectURL(blob)

  const link = document.createElement("a")

  link.href = url

  link.download = "rooms_export.csv"

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}