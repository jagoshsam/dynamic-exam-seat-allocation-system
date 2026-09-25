function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-gray-200 bg-white lg:block">

      <div className="flex h-full flex-col">

        {/* Logo */}
        <div className="border-b border-gray-200 px-6 py-6">

          <h1 className="text-lg font-bold text-gray-900">
            ExamSeat
          </h1>

          <p className="mt-1 text-xs text-gray-500">
            Dynamic Seat Allocation
          </p>

        </div>


        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-4 py-5">

          <NavItem
            icon="📊"
            label="Dashboard"
            active={activePage === "dashboard"}
            onClick={() => setActivePage("dashboard")}
          />

          <NavItem
            icon="👨‍🎓"
            label="Students"
            active={activePage === "students"}
            onClick={() => setActivePage("students")}
          />

          <NavItem
            icon="🏫"
            label="Rooms"
            active={activePage === "rooms"}
            onClick={() => setActivePage("rooms")}
          />

          <NavItem
            icon="💺"
            label="Seats"
            active={activePage === "seats"}
            onClick={() => setActivePage("seats")}
          />

          <NavItem
            icon="📝"
            label="Exams"
            active={activePage === "exams"}
            onClick={() => setActivePage("exams")}
          />

          <NavItem
            icon="🎯"
            label="Allocations"
            active={activePage === "allocations"}
            onClick={() => setActivePage("allocations")}
          />

          <NavItem
            icon="📋"
            label="Audit Logs"
            active={activePage === "audit"}
            onClick={() => setActivePage("audit")}
          />

        </nav>


        {/* Backend Status */}
        <div className="border-t border-gray-200 p-4">

          <div className="rounded-lg bg-green-50 p-3">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-full bg-green-500"></span>

              <span className="text-xs font-medium text-green-700">
                Backend Connected
              </span>

            </div>

          </div>

        </div>

      </div>

    </aside>
  )
}


/* =========================================================
   Navigation Item
========================================================= */

function NavItem({
  icon,
  label,
  active,
  onClick,
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition ${
        active
          ? "bg-blue-50 text-blue-700"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
      }`}
    >

      <span className="text-lg">
        {icon}
      </span>

      <span>
        {label}
      </span>

    </button>
  )
}


export default Sidebar