import StatCard from "../components/StatCard"

function Dashboard() {
  return (
    <div className="space-y-6">

      <div>
        <h2 className="text-2xl font-bold text-gray-900">
          Dashboard
        </h2>

        <p className="mt-1 text-gray-500">
          Examination Seat Allocation Overview
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

        <StatCard
          label="Total Students"
          value="0"
        />

        <StatCard
          label="Total Rooms"
          value="0"
        />

        <StatCard
          label="Total Seats"
          value="0"
        />

        <StatCard
          label="Backend Status"
          value="Online"
          green
        />

      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">

        <h3 className="text-lg font-semibold">
          Project Status
        </h3>

        <div className="mt-4 space-y-2 text-sm">

          <p>✅ FastAPI Backend</p>
          <p>✅ Database Connected</p>
          <p>✅ Student API</p>
          <p>✅ Room API</p>
          <p>✅ Seat API</p>
          <p>✅ Allocation Engine</p>
          <p>⏳ Exam Management UI</p>
          <p>⏳ Allocation Dashboard</p>

        </div>

      </div>

    </div>
  )
}

export default Dashboard