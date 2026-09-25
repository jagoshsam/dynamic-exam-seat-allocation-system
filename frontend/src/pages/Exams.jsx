import { useEffect, useState } from "react"

import {
  getExams,
  createExam,
  exportExamsCsv,
} from "../api/exams"

import { downloadCsvTemplate } from "../utils/csv"


function Exams() {
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [showForm, setShowForm] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)

  const [formData, setFormData] = useState({
    exam_id: "",
    course_code: "",
    exam_datetime: "",
    duration: "",
    allowed_rooms: "",
    proctoring_level: "",
  })


  // ============================================================
  // LOAD EXAMS
  // ============================================================

  async function loadExams() {
    try {
      setLoading(true)
      setError("")

      const data = await getExams()

      setExams(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadExams()
  }, [])


  // ============================================================
  // FORM CHANGE
  // ============================================================

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }


  // ============================================================
  // CREATE EXAM
  // ============================================================

  async function handleSubmit(event) {
    event.preventDefault()

    setError("")
    setSuccess("")

    try {
      await createExam({
        exam_id: formData.exam_id,
        course_code: formData.course_code,
        exam_datetime: formData.exam_datetime,
        duration: Number(formData.duration),
        allowed_rooms: formData.allowed_rooms,
        proctoring_level: formData.proctoring_level,
      })

      setSuccess("Exam created successfully.")

      setFormData({
        exam_id: "",
        course_code: "",
        exam_datetime: "",
        duration: "",
        allowed_rooms: "",
        proctoring_level: "",
      })

      setShowForm(false)

      await loadExams()
    } catch (err) {
      setError(err.message)
    }
  }


  // ============================================================
  // DOWNLOAD CSV TEMPLATE
  // ============================================================

  function handleDownloadTemplate() {
    downloadCsvTemplate(
      "exams_template.csv",
      [
        "exam_id",
        "course_code",
        "exam_datetime",
        "duration",
        "allowed_rooms",
        "proctoring_level",
      ]
    )
  }


  // ============================================================
  // EXPORT EXAMS CSV
  // ============================================================

  async function handleExportCsv() {
    try {
      setExportLoading(true)
      setError("")
      setSuccess("")

      await exportExamsCsv()

      setSuccess("Exams CSV exported successfully.")
    } catch (err) {
      setError(err.message)
    } finally {
      setExportLoading(false)
    }
  }


  return (
    <div className="space-y-6">

      {/* ========================================================
          PAGE HEADER
      ======================================================== */}

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Exam Sessions
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Manage examination sessions and schedules.
          </p>
        </div>


        <div className="flex flex-wrap gap-3">

          {/* CSV TEMPLATE */}

          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50"
          >
            Download CSV Template
          </button>


          {/* EXPORT CSV */}

          <button
            type="button"
            onClick={handleExportCsv}
            disabled={exportLoading}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {exportLoading ? "Exporting..." : "Export CSV"}
          </button>


          {/* ADD EXAM */}

          <button
            type="button"
            onClick={() => setShowForm((prev) => !prev)}
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-gray-800"
          >
            {showForm ? "Cancel" : "+ Add Exam"}
          </button>

        </div>
      </div>


      {/* ========================================================
          SUCCESS MESSAGE
      ======================================================== */}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {success}
        </div>
      )}


      {/* ========================================================
          ERROR MESSAGE
      ======================================================== */}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}


      {/* ========================================================
          ADD EXAM FORM
      ======================================================== */}

      {showForm && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h3 className="mb-5 text-lg font-semibold text-gray-900">
            Create Exam Session
          </h3>

          <form
            onSubmit={handleSubmit}
            className="grid grid-cols-1 gap-4 md:grid-cols-2"
          >

            {/* Exam ID */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Exam ID
              </label>

              <input
                type="text"
                name="exam_id"
                value={formData.exam_id}
                onChange={handleChange}
                required
                placeholder="EXAM001"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Course Code */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Course Code
              </label>

              <input
                type="text"
                name="course_code"
                value={formData.course_code}
                onChange={handleChange}
                required
                placeholder="CS101"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Exam Date & Time */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Exam Date & Time
              </label>

              <input
                type="datetime-local"
                name="exam_datetime"
                value={formData.exam_datetime}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Duration */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Duration (minutes)
              </label>

              <input
                type="number"
                name="duration"
                value={formData.duration}
                onChange={handleChange}
                min="1"
                required
                placeholder="180"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Allowed Rooms */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Allowed Rooms
              </label>

              <input
                type="text"
                name="allowed_rooms"
                value={formData.allowed_rooms}
                onChange={handleChange}
                required
                placeholder="R001,R002"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Proctoring Level */}

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Proctoring Level
              </label>

              <input
                type="text"
                name="proctoring_level"
                value={formData.proctoring_level}
                onChange={handleChange}
                required
                placeholder="standard"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
              />
            </div>


            {/* Submit */}

            <div className="md:col-span-2">

              <button
                type="submit"
                className="rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800"
              >
                Create Exam
              </button>

            </div>

          </form>
        </div>
      )}


      {/* ========================================================
          EXAMS TABLE
      ======================================================== */}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="border-b border-gray-200 px-6 py-4">

          <h3 className="text-lg font-semibold text-gray-900">
            Exam Sessions
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            {exams.length} exam session{exams.length !== 1 ? "s" : ""}
          </p>

        </div>


        {loading ? (

          <div className="px-6 py-12 text-center text-sm text-gray-500">
            Loading exams...
          </div>

        ) : exams.length === 0 ? (

          <div className="px-6 py-12 text-center">

            <p className="text-sm text-gray-500">
              No exam sessions found.
            </p>

            <p className="mt-1 text-xs text-gray-400">
              Create an exam session to see it here.
            </p>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="min-w-full divide-y divide-gray-200">

              <thead className="bg-gray-50">

                <tr>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Exam ID
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Course
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Date & Time
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Duration
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Allowed Rooms
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Proctoring
                  </th>

                </tr>

              </thead>


              <tbody className="divide-y divide-gray-200 bg-white">

                {exams.map((exam) => (

                  <tr
                    key={exam.id}
                    className="hover:bg-gray-50"
                  >

                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      {exam.exam_id}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700">
                      {exam.course_code}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700">
                      {exam.exam_datetime}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700">
                      {exam.duration} min
                    </td>

                    <td className="px-6 py-4 text-sm text-gray-700">
                      {exam.allowed_rooms}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700">
                      {exam.proctoring_level}
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


export default Exams