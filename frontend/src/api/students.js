import { apiRequest } from "./client"


// =========================================================
// GET ALL STUDENTS
// =========================================================

export async function getStudents() {
  return apiRequest("/students/")
}


// =========================================================
// CREATE SINGLE STUDENT
// =========================================================

export async function createStudent(student) {
  return apiRequest("/students/", {
    method: "POST",
    body: JSON.stringify(student),
  })
}


// =========================================================
// PREVIEW STUDENTS CSV
// =========================================================

export async function previewStudentsCsv(file) {
  const formData = new FormData()

  formData.append("file", file)

  return apiRequest("/students/preview-csv", {
    method: "POST",
    headers: {},
    body: formData,
  })
}


// =========================================================
// IMPORT STUDENTS CSV
// =========================================================

export async function importStudentsCsv(file) {
  const formData = new FormData()

  formData.append("file", file)

  return apiRequest("/students/import-csv", {
    method: "POST",
    headers: {},
    body: formData,
  })
}


// =========================================================
// EXPORT STUDENTS TO CSV
// =========================================================

export async function exportStudentsCsv() {

  const response = await fetch(
    "http://127.0.0.1:8000/students/export-csv"
  )

  if (!response.ok) {

    throw new Error(
      "Failed to export students CSV"
    )

  }

  const blob = await response.blob()

  const url = window.URL.createObjectURL(blob)

  const link = document.createElement("a")

  link.href = url

  link.download = "students_export.csv"

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}