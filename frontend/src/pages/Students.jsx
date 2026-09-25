import { useEffect, useState } from "react"

import {
  getStudents,
  previewStudentsCsv,
  importStudentsCsv,
  exportStudentsCsv,
} from "../api/students"

import StatCard from "../components/StatCard"

import { downloadCsvTemplate } from "../utils/csv"


function Students() {
  const [students, setStudents] = useState([])

  const [loading, setLoading] = useState(true)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)

  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)


  // =========================================================
  // Load Students
  // =========================================================

  async function loadStudents() {

    try {

      setLoading(true)
      setError("")

      const data = await getStudents()

      setStudents(data)

    } catch (err) {

      setError(err.message)

    } finally {

      setLoading(false)

    }

  }


  useEffect(() => {
    loadStudents()
  }, [])


  // =========================================================
  // File Selection
  // =========================================================

  function handleFileChange(event) {

    const file =
      event.target.files?.[0] || null

    setSelectedFile(file)

    setPreview(null)

    setError("")

    setSuccess("")

  }


  // =========================================================
  // Download CSV Template
  // =========================================================

  function handleDownloadTemplate() {

    downloadCsvTemplate(
      "students_template.csv",
      [
        "student_id",
        "name",
        "programme",
        "year",
        "special_needs",
        "conflict_exams",
        "priority_score",
      ]
    )

  }


  // =========================================================
  // Export Students CSV
  // =========================================================

  async function handleExportCsv() {

    try {

      setExportLoading(true)

      setError("")
      setSuccess("")

      await exportStudentsCsv()

      setSuccess(
        "Students exported successfully."
      )

    } catch (err) {

      setError(
        err.message ||
        "Failed to export students CSV."
      )

    } finally {

      setExportLoading(false)

    }

  }


  // =========================================================
  // Preview CSV
  // =========================================================

  async function handlePreview() {

    if (!selectedFile) {

      setError(
        "Please select a CSV file first."
      )

      return

    }

    setPreviewLoading(true)

    setError("")

    setSuccess("")

    setPreview(null)

    try {

      const result =
        await previewStudentsCsv(
          selectedFile
        )

      setPreview(result)

    } catch (err) {

      setError(err.message)

    } finally {

      setPreviewLoading(false)

    }

  }


  // =========================================================
  // Import CSV
  // =========================================================

  async function handleImport() {

    if (!selectedFile) {

      setError(
        "Please select a CSV file first."
      )

      return

    }

    if (!preview?.can_import) {

      setError(
        "The CSV must pass validation before it can be imported."
      )

      return

    }

    setImportLoading(true)

    setError("")

    setSuccess("")

    try {

      const result =
        await importStudentsCsv(
          selectedFile
        )

      setSuccess(
        result.message ||
        `${result.imported_count} students imported successfully.`
      )

      setSelectedFile(null)

      setPreview(null)

      const fileInput =
        document.getElementById(
          "student-csv"
        )

      if (fileInput) {

        fileInput.value = ""

      }

      await loadStudents()

    } catch (err) {

      setError(err.message)

    } finally {

      setImportLoading(false)

    }

  }


  // =========================================================
  // Statistics
  // =========================================================

  const specialNeedsCount =
    students.filter(
      (student) =>
        student.special_needs
    ).length


  return (
    <div>

      {/* =====================================================
          Heading
      ===================================================== */}

      <div>

        <p className="text-sm font-medium text-blue-600">
          Student Management
        </p>

        <h2 className="mt-1 text-3xl font-bold text-gray-900">
          Students
        </h2>

        <p className="mt-2 text-gray-500">
          Manage student records used for examination seat allocation.
        </p>

      </div>


      {/* =====================================================
          Messages
      ===================================================== */}

      {error && (

        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">

          <p className="font-semibold text-red-700">
            Error
          </p>

          <p className="mt-1 text-sm text-red-600">
            {error}
          </p>

        </div>

      )}


      {success && (

        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4">

          <p className="font-semibold text-green-700">
            Success
          </p>

          <p className="mt-1 text-sm text-green-600">
            {success}
          </p>

        </div>

      )}


      {/* =====================================================
          CSV Import
      ===================================================== */}

      <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

        <div>

          <h3 className="text-xl font-bold text-gray-900">
            Import Students from CSV
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Upload a CSV file containing student records.
          </p>

        </div>


        <div className="mt-6 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-8">

          <div className="text-center">

            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-white text-2xl shadow-sm">
              📄
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              Select a student CSV file
            </h4>

            <p className="mt-1 text-sm text-gray-500">
              The file will be validated before anything is imported.
            </p>


            <div className="mt-5">

              <input
                id="student-csv"
                type="file"
                accept=".csv,text/csv"
                onChange={handleFileChange}
                className="mx-auto block w-full max-w-md rounded-lg border border-gray-300 bg-white p-3 text-sm"
              />

            </div>


            {selectedFile && (

              <p className="mt-3 text-sm font-medium text-blue-600">
                Selected: {selectedFile.name}
              </p>

            )}


            <div className="mt-5 flex flex-wrap justify-center gap-3">

              {/* Preview */}

              <button
                type="button"
                onClick={handlePreview}
                disabled={
                  !selectedFile ||
                  previewLoading
                }
                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                {previewLoading
                  ? "Validating..."
                  : "Preview CSV"}
              </button>


              {/* Download Template */}

              <button
                type="button"
                onClick={
                  handleDownloadTemplate
                }
                className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50"
              >
                Download CSV Template
              </button>


              {/* Export Database */}

              <button
                type="button"
                onClick={handleExportCsv}
                disabled={exportLoading}
                className="rounded-lg bg-green-600 px-6 py-3 font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                {exportLoading
                  ? "Exporting..."
                  : "Export CSV"}
              </button>

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          Preview Results
      ===================================================== */}

      {preview && (

        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

            <div>

              <h3 className="text-xl font-bold text-gray-900">
                CSV Validation
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Review the validation result before importing.
              </p>

            </div>


            <div>

              {preview.can_import ? (

                <span className="rounded-full bg-green-100 px-4 py-2 text-sm font-semibold text-green-700">
                  Ready to Import
                </span>

              ) : (

                <span className="rounded-full bg-red-100 px-4 py-2 text-sm font-semibold text-red-700">
                  Validation Failed
                </span>

              )}

            </div>

          </div>


          {/* Preview Statistics */}

          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">

            <PreviewStat
              label="Total Rows"
              value={preview.total_rows}
            />

            <PreviewStat
              label="Valid Rows"
              value={preview.valid_count}
            />

            <PreviewStat
              label="Errors"
              value={preview.error_count}
            />

            <PreviewStat
              label="Duplicates"
              value={preview.duplicate_count}
            />

          </div>


          {/* Errors */}

          {preview.errors?.length > 0 && (

            <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">

              <h4 className="font-semibold text-red-700">
                Validation Errors
              </h4>

              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-red-600">

                {preview.errors.map(
                  (item, index) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </div>

          )}


          {/* Duplicates */}

          {preview.duplicates?.length > 0 && (

            <div className="mt-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4">

              <h4 className="font-semibold text-yellow-700">
                Duplicate Student IDs
              </h4>

              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-yellow-700">

                {preview.duplicates.map(
                  (item, index) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </div>

          )}


          {/* Valid Students Preview */}

          {preview.students?.length > 0 && (

            <div className="mt-6 overflow-hidden rounded-lg border border-gray-200">

              <div className="border-b border-gray-200 bg-gray-50 px-5 py-4">

                <h4 className="font-semibold text-gray-900">
                  Valid Student Records
                </h4>

              </div>


              <div className="max-h-80 overflow-auto">

                <table className="w-full text-left">

                  <thead className="sticky top-0 bg-white">

                    <tr className="border-b border-gray-200">

                      <TableHeader>
                        Student ID
                      </TableHeader>

                      <TableHeader>
                        Name
                      </TableHeader>

                      <TableHeader>
                        Programme
                      </TableHeader>

                      <TableHeader>
                        Year
                      </TableHeader>

                      <TableHeader>
                        Special Needs
                      </TableHeader>

                    </tr>

                  </thead>


                  <tbody>

                    {preview.students.map(
                      (student, index) => (

                        <tr
                          key={`${student.student_id}-${index}`}
                          className="border-b border-gray-100 last:border-0"
                        >

                          <td className="px-5 py-3 font-medium text-gray-900">
                            {student.student_id}
                          </td>

                          <td className="px-5 py-3 text-gray-700">
                            {student.name}
                          </td>

                          <td className="px-5 py-3 text-gray-700">
                            {student.programme}
                          </td>

                          <td className="px-5 py-3 text-gray-700">
                            {student.year}
                          </td>

                          <td className="px-5 py-3">

                            {student.special_needs ? (

                              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                                Yes
                              </span>

                            ) : (

                              <span className="text-gray-500">
                                No
                              </span>

                            )}

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            </div>

          )}


          {/* Import Button */}

          <div className="mt-6 flex flex-wrap gap-3">

            <button
              type="button"
              onClick={handleImport}
              disabled={
                !preview.can_import ||
                importLoading
              }
              className="rounded-lg bg-green-600 px-6 py-3 font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {importLoading
                ? "Importing..."
                : "Import Students"}
            </button>


            <button
              type="button"
              onClick={() => {

                setPreview(null)

                setSelectedFile(null)

                const fileInput =
                  document.getElementById(
                    "student-csv"
                  )

                if (fileInput) {

                  fileInput.value = ""

                }

              }}
              className="rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50"
            >
              Clear
            </button>

          </div>

        </div>

      )}


      {/* =====================================================
          Statistics
      ===================================================== */}

      <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">

        <StatCard
          label="Total Students"
          value={students.length}
        />

        <StatCard
          label="Special Needs"
          value={specialNeedsCount}
        />

        <StatCard
          label="API Status"
          value="Connected"
          green
        />

      </div>


      {/* =====================================================
          Student Records
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-5">

          <div>

            <h3 className="text-lg font-bold text-gray-900">
              Student Records
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Students currently stored in the database.
            </p>

          </div>


          <button
            onClick={loadStudents}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>

        </div>


        {loading ? (

          <div className="px-6 py-12 text-center text-gray-500">
            Loading students...
          </div>

        ) : students.length === 0 ? (

          <div className="px-6 py-16 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-2xl">
              👤
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              No students found
            </h4>

            <p className="mt-2 text-sm text-gray-500">
              Your database currently contains no student records.
            </p>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="bg-gray-50">

                <tr className="border-b border-gray-200">

                  <TableHeader>
                    Student ID
                  </TableHeader>

                  <TableHeader>
                    Name
                  </TableHeader>

                  <TableHeader>
                    Programme
                  </TableHeader>

                  <TableHeader>
                    Year
                  </TableHeader>

                  <TableHeader>
                    Special Needs
                  </TableHeader>

                  <TableHeader>
                    Priority
                  </TableHeader>

                </tr>

              </thead>


              <tbody>

                {students.map((student) => (

                  <tr
                    key={student.id}
                    className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                  >

                    <td className="px-6 py-4 font-medium text-gray-900">
                      {student.student_id}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {student.name}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {student.programme}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {student.year}
                    </td>

                    <td className="px-6 py-4">

                      {student.special_needs ? (

                        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                          Yes
                        </span>

                      ) : (

                        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
                          No
                        </span>

                      )}

                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {student.priority_score ?? 0}
                    </td>

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
   Preview Stat
========================================================= */

function PreviewStat({
  label,
  value,
}) {

  return (

    <div className="rounded-lg bg-gray-50 p-4">

      <p className="text-xs font-medium text-gray-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-bold text-gray-900">
        {value ?? 0}
      </p>

    </div>

  )
}


/* =========================================================
   Table Header
========================================================= */

function TableHeader({
  children,
}) {

  return (

    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
      {children}
    </th>

  )

}


export default Students