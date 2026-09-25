import { useEffect, useMemo, useState } from "react"

import { getAuditLogs } from "../api/audit"

import StatCard from "../components/StatCard"


function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [actionFilter, setActionFilter] = useState("ALL")


  // =========================================================
  // LOAD AUDIT LOGS
  // =========================================================

  async function loadLogs() {
    try {
      setLoading(true)
      setError("")

      const data = await getAuditLogs()

      setLogs(data)

    } catch (err) {
      setError(err.message)

    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadLogs()
  }, [])


  // =========================================================
  // FILTERED LOGS
  // =========================================================

  const filteredLogs = useMemo(() => {
    if (actionFilter === "ALL") {
      return logs
    }

    return logs.filter(
      (log) => log.action === actionFilter
    )
  }, [logs, actionFilter])


  // =========================================================
  // LOG STATISTICS
  // =========================================================

  const deltaCount = logs.filter(
    (log) =>
      log.action === "DELTA_REALLOCATION"
  ).length


  const allocationCount = logs.filter(
    (log) =>
      log.action === "CREATE_ALLOCATION"
  ).length


  return (
    <div>

      {/* =====================================================
          HEADING
      ===================================================== */}

      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

        <div>

          <p className="text-sm font-medium text-blue-600">
            System History
          </p>

          <h2 className="mt-1 text-3xl font-bold text-gray-900">
            Audit Logs
          </h2>

          <p className="mt-2 text-gray-500">
            Track actions and changes made within the examination system.
          </p>

        </div>


        <button
          onClick={loadLogs}
          disabled={loading}
          className="rounded-lg border border-gray-300 bg-white px-5 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Refreshing..."
            : "Refresh Logs"}
        </button>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">

          <p className="font-semibold text-red-700">
            Unable to load audit logs
          </p>

          <p className="mt-1 text-sm text-red-600">
            {error}
          </p>

        </div>
      )}


      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-4">

        <StatCard
          label="Total Log Entries"
          value={
            loading
              ? "..."
              : logs.length
          }
        />

        <StatCard
          label="System Actions"
          value={
            loading
              ? "..."
              : logs.filter(
                  (log) =>
                    log.user === "system"
                ).length
          }
        />

        <StatCard
          label="Allocations"
          value={
            loading
              ? "..."
              : allocationCount
          }
        />

        <StatCard
          label="Delta Changes"
          value={
            loading
              ? "..."
              : deltaCount
          }
          green
        />

      </div>


      {/* =====================================================
          FILTERS
      ===================================================== */}

      <div className="mt-8 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>

            <h3 className="font-semibold text-gray-900">
              Filter Activity
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Filter the audit history by action type.
            </p>

          </div>


          <select
            value={actionFilter}
            onChange={(event) =>
              setActionFilter(
                event.target.value
              )
            }
            className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-700"
          >

            <option value="ALL">
              All Actions
            </option>

            <option value="CREATE_ALLOCATION">
              Create Allocation
            </option>

            <option value="DELTA_REALLOCATION">
              Delta Reallocation
            </option>

          </select>

        </div>

      </div>


      {/* =====================================================
          AUDIT TABLE
      ===================================================== */}

      <div className="mt-8 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="border-b border-gray-200 px-6 py-5">

          <h3 className="text-lg font-bold text-gray-900">
            Activity History
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Recorded actions from the system and authorized users.
          </p>

        </div>


        {loading ? (

          <div className="px-6 py-12 text-center text-gray-500">
            Loading audit logs...
          </div>

        ) : filteredLogs.length === 0 ? (

          <div className="px-6 py-16 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-2xl">
              📋
            </div>

            <h4 className="mt-4 font-semibold text-gray-900">
              No audit logs found
            </h4>

            <p className="mt-2 text-sm text-gray-500">
              {logs.length === 0
                ? "System actions will appear here once activity is recorded."
                : "No logs match the selected action filter."}
            </p>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="bg-gray-50">

                <tr className="border-b border-gray-200">

                  <TH>Action</TH>
                  <TH>Entity</TH>
                  <TH>User</TH>
                  <TH>Timestamp</TH>
                  <TH>Changes</TH>

                </tr>

              </thead>


              <tbody>

                {filteredLogs.map((log) => (

                  <tr
                    key={log.id}
                    className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                  >

                    {/* ACTION */}

                    <td className="px-6 py-4">

                      <ActionBadge
                        action={log.action}
                      />

                    </td>


                    {/* ENTITY */}

                    <td className="px-6 py-4">

                      <span className="rounded-md bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                        {log.entity}
                      </span>

                    </td>


                    {/* USER */}

                    <td className="px-6 py-4 text-gray-700">
                      {log.user}
                    </td>


                    {/* TIMESTAMP */}

                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                      {formatDate(log.timestamp)}
                    </td>


                    {/* CHANGES */}

                    <td className="max-w-xl px-6 py-4">

                      {log.action ===
                      "DELTA_REALLOCATION" ? (

                        <DeltaChange
                          diff={log.diff}
                        />

                      ) : (

                        <pre className="max-h-24 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-gray-50 p-3 text-xs text-gray-600">
                          {formatDiff(log.diff)}
                        </pre>

                      )}

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
   ACTION BADGE
========================================================= */

function ActionBadge({
  action,
}) {

  let className =
    "bg-gray-100 text-gray-700"

  if (
    action ===
    "CREATE_ALLOCATION"
  ) {
    className =
      "bg-blue-50 text-blue-700"
  }

  if (
    action ===
    "DELTA_REALLOCATION"
  ) {
    className =
      "bg-purple-50 text-purple-700"
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${className}`}
    >
      {formatActionName(action)}
    </span>
  )
}


/* =========================================================
   DELTA CHANGE DISPLAY
========================================================= */

function DeltaChange({
  diff,
}) {

  const change =
    parseDeltaDiff(diff)

  if (!change) {

    return (
      <pre className="max-h-24 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-gray-50 p-3 text-xs text-gray-600">
        {formatDiff(diff)}
      </pre>
    )

  }


  return (

    <div className="rounded-lg border border-purple-100 bg-purple-50 p-3">

      <div className="flex flex-wrap items-center gap-2 text-sm">

        <span className="font-semibold text-gray-900">
          {change.student}
        </span>

        <span className="text-gray-500">
          moved
        </span>

        <span className="rounded-md bg-white px-2 py-1 font-semibold text-gray-700">
          {change.oldSeat}
        </span>

        <span className="font-bold text-purple-600">
          →
        </span>

        <span className="rounded-md bg-white px-2 py-1 font-semibold text-purple-700">
          {change.newSeat}
        </span>

      </div>


      {change.reason && (

        <p className="mt-2 text-xs text-purple-700">
          Reason: {change.reason}
        </p>

      )}

    </div>

  )
}


/* =========================================================
   PARSE DELTA DIFF
========================================================= */

function parseDeltaDiff(value) {

  if (!value) {
    return null
  }

  const text =
    String(value)


  const studentMatch =
    text.match(
      /student=([^;]+)/
    )


  const oldSeatMatch =
    text.match(
      /old_seat=([^;]+)/
    )


  const newSeatMatch =
    text.match(
      /new_seat=([^;]+)/
    )


  const reasonMatch =
    text.match(
      /reason=([^;]+)/
    )


  if (
    !studentMatch &&
    !oldSeatMatch &&
    !newSeatMatch
  ) {
    return null
  }


  return {
    student:
      studentMatch
        ? studentMatch[1].trim()
        : "-",

    oldSeat:
      oldSeatMatch
        ? oldSeatMatch[1].trim()
        : "-",

    newSeat:
      newSeatMatch
        ? newSeatMatch[1].trim()
        : "-",

    reason:
      reasonMatch
        ? reasonMatch[1].trim()
        : "",
  }
}


/* =========================================================
   TABLE HEADER
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
   DATE FORMATTER
========================================================= */

function formatDate(value) {

  if (!value) {
    return "-"
  }


  const date =
    new Date(value)


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }


  return date.toLocaleString()
}


/* =========================================================
   DIFF FORMATTER
========================================================= */

function formatDiff(value) {

  if (!value) {
    return "No changes recorded"
  }


  try {

    return JSON.stringify(
      JSON.parse(value),
      null,
      2
    )

  } catch {

    return value

  }
}


/* =========================================================
   ACTION NAME FORMATTER
========================================================= */

function formatActionName(
  action
) {

  if (!action) {
    return "-"
  }


  return action
    .replaceAll(
      "_",
      " "
    )
    .toLowerCase()
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    )
}


export default AuditLogs