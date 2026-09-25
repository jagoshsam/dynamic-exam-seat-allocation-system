import { apiRequest } from "./client"


// ============================================================
// GET ALL EXAMS
// ============================================================

export async function getExams() {
  return apiRequest("/exams/")
}


// ============================================================
// CREATE EXAM
// ============================================================

export async function createExam(exam) {
  return apiRequest("/exams/", {
    method: "POST",
    body: JSON.stringify(exam),
  })
}


// ============================================================
// EXPORT EXAMS TO CSV
// ============================================================

export async function exportExamsCsv() {
  const response = await fetch(
    "http://127.0.0.1:8000/exams/export-csv"
  )

  if (!response.ok) {
    throw new Error("Failed to export exams CSV")
  }

  const blob = await response.blob()

  const url = window.URL.createObjectURL(blob)

  const link = document.createElement("a")

  link.href = url
  link.download = "exams_export.csv"

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}