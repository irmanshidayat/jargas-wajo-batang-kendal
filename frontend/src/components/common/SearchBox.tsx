import React from 'react'

interface SearchBoxProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

const SearchBox: React.FC<SearchBoxProps> = ({
  value,
  onChange,
  placeholder = 'Cari...',
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>
    </div>
  )
}

export default SearchBox

