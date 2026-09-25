function StatCard({
  label,
  value,
  green = false,
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

      <p className="text-sm font-medium text-gray-500">
        {label}
      </p>

      <p
        className={`mt-2 text-3xl font-bold ${
          green
            ? "text-green-600"
            : "text-gray-900"
        }`}
      >
        {value}
      </p>

    </div>
  )
}

export default StatCard