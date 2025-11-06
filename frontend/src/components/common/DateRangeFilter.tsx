interface DateRangeFilterProps {
  startDate: string
  endDate: string
  onDateChange: (startDate: string, endDate: string) => void
  label?: string
}

export default function DateRangeFilter({
  startDate,
  endDate,
  onDateChange,
  label = 'Filter Tanggal',
}: DateRangeFilterProps) {
  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onDateChange(e.target.value, endDate)
  }

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onDateChange(startDate, e.target.value)
  }

  const handleClear = () => {
    onDateChange('', '')
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <label className="text-sm font-medium text-gray-700 whitespace-nowrap">{label}</label>
        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          <div className="flex flex-col">
            <label className="text-xs text-gray-600 mb-1">Dari Tanggal</label>
            <input
              type="date"
              value={startDate}
              onChange={handleStartDateChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xs text-gray-600 mb-1">Sampai Tanggal</label>
            <div className="flex gap-2">
              <input
                type="date"
                value={endDate}
                onChange={handleEndDateChange}
                min={startDate || undefined}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
              {(startDate || endDate) && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg border border-gray-300 transition-colors"
                  title="Hapus filter"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

