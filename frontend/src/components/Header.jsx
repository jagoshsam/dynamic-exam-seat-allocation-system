function Header({ title }) {
  return (
    <header className="border-b border-gray-200 bg-white">

      <div className="flex items-center justify-between px-6 py-4 lg:px-8">

        {/* Page Information */}
        <div>

          <p className="text-sm text-gray-500">
            Examination Management
          </p>

          <h1 className="text-xl font-bold text-gray-900">
            {title}
          </h1>

        </div>


        {/* Backend Status */}
        <div className="flex items-center gap-2 rounded-full bg-green-50 px-4 py-2 text-sm text-green-700">

          <span className="h-2 w-2 rounded-full bg-green-500"></span>

          API Connected

        </div>

      </div>

    </header>
  )
}

export default Header