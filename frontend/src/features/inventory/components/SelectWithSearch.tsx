import { useState, useEffect, useRef } from 'react'
import Swal from 'sweetalert2'

interface SelectWithSearchProps {
  value: string
  onChange: (value: string) => void
  options: string[]
  placeholder?: string
  label: string
  required?: boolean
  onAddNew?: (newValue: string) => Promise<void>
  disabled?: boolean
}

export default function SelectWithSearch({
  value,
  onChange,
  options,
  placeholder = 'Cari atau pilih...',
  label,
  required = false,
  onAddNew,
  disabled = false,
}: SelectWithSearchProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredOptions, setFilteredOptions] = useState<string[]>([])
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredOptions(options)
    } else {
      const filtered = options.filter((option) =>
        option.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredOptions(filtered)
    }
  }, [searchTerm, options])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleSelect = (selectedValue: string) => {
    onChange(selectedValue)
    setIsOpen(false)
    setSearchTerm('')
  }

  useEffect(() => {
    // Reset searchTerm saat value berubah dari luar (misal dari form reset)
    if (!isOpen) {
      setSearchTerm('')
    }
  }, [value, isOpen])

  const handleAddNew = async () => {
    if (!searchTerm.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Perhatian',
        text: 'Silakan masukkan nilai terlebih dahulu',
      })
      return
    }

    // Cek apakah sudah ada di options
    if (options.some((opt) => opt.toLowerCase() === searchTerm.trim().toLowerCase())) {
      Swal.fire({
        icon: 'info',
        title: 'Sudah Ada',
        text: `"${searchTerm.trim()}" sudah ada dalam daftar`,
      })
      return
    }

    try {
      if (onAddNew) {
        await onAddNew(searchTerm.trim())
      }
      onChange(searchTerm.trim())
      setIsOpen(false)
      setSearchTerm('')
      Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: `"${searchTerm.trim()}" berhasil ditambahkan`,
        timer: 1500,
      })
    } catch (error: any) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.detail || error.message || 'Gagal menambahkan nilai baru',
      })
    }
  }

  const showAddButton = searchTerm.trim() && !filteredOptions.some(
    (opt) => opt.toLowerCase() === searchTerm.trim().toLowerCase()
  )

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={isOpen ? searchTerm : (value || '')}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            if (!isOpen) setIsOpen(true)
          }}
          onFocus={() => {
            setIsOpen(true)
            // Kosongkan searchTerm saat dropdown dibuka untuk memudahkan pencarian
            if (!searchTerm) {
              setSearchTerm('')
            }
          }}
          onBlur={() => {
            // Delay untuk memungkinkan click pada dropdown
            setTimeout(() => {
              if (dropdownRef.current && !dropdownRef.current.contains(document.activeElement)) {
                setIsOpen(false)
                setSearchTerm('')
              }
            }, 200)
          }}
          placeholder={placeholder}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
          required={required}
          disabled={disabled}
        />
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <svg
            className={`h-5 w-5 text-gray-400 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredOptions.length > 0 ? (
            <ul className="py-1">
              {filteredOptions.map((option, index) => (
                <li
                  key={index}
                  onClick={() => handleSelect(option)}
                  className={`px-4 py-2 cursor-pointer hover:bg-blue-50 transition-colors ${
                    value === option ? 'bg-blue-100 font-semibold' : ''
                  }`}
                >
                  {option}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 text-gray-500 text-sm">
              {searchTerm ? 'Tidak ada hasil' : 'Tidak ada data'}
            </div>
          )}

          {showAddButton && onAddNew && (
            <div className="border-t border-gray-200 p-2">
              <button
                type="button"
                onClick={handleAddNew}
                className="w-full px-4 py-2 text-left text-blue-600 hover:bg-blue-50 rounded transition-colors flex items-center gap-2"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M12 4v16m8-8H4" />
                </svg>
                <span>Tambah "{searchTerm.trim()}"</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

