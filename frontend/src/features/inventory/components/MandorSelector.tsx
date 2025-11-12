import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Mandor } from '../services/inventoryService'

interface MandorSelectorProps {
  value: string // nama mandor yang ditampilkan
  mandors: Mandor[]
  onSelect: (mandor: Mandor | null) => void
  onManualChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export default function MandorSelector({
  value,
  mandors,
  onSelect,
  onManualChange,
  placeholder = 'Ketik nama mandor...',
  disabled = false,
}: MandorSelectorProps) {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredMandors, setFilteredMandors] = useState<Mandor[]>([])
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredMandors(mandors.filter(m => m.is_active === 1).slice(0, 50))
    } else {
      const term = searchTerm.toLowerCase()
      const filtered = mandors
        .filter((mandor) => mandor.is_active === 1)
        .filter((mandor) => {
          const namaMandor = mandor.nama.toLowerCase()
          return namaMandor.includes(term)
        })
        .slice(0, 50) // Limit results untuk performa
      setFilteredMandors(filtered)
    }
  }, [searchTerm, mandors])

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

  const handleSelect = (mandor: Mandor) => {
    onSelect(mandor)
    setIsOpen(false)
    setSearchTerm('')
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    onManualChange(inputValue)
    setSearchTerm(inputValue)
    if (!isOpen && inputValue) {
      setIsOpen(true)
    }
  }

  const handleFocus = () => {
    setIsOpen(true)
    if (!searchTerm && value) {
      setSearchTerm(value)
    }
  }

  const handleBlur = () => {
    setTimeout(() => {
      if (dropdownRef.current && !dropdownRef.current.contains(document.activeElement)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }, 200)
  }

  const handleAddNewMandor = () => {
    setIsOpen(false)
    setSearchTerm('')
    navigate('/inventory/mandors')
  }

  // Cek apakah search term tidak ada di filtered mandors
  const showAddButton = searchTerm.trim() && 
    !filteredMandors.some((mandor) => 
      mandor.nama.toLowerCase() === searchTerm.trim().toLowerCase()
    )

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-slate-700 transition-colors"
        disabled={disabled}
      />
      
      {isOpen && !disabled && (
        <div className="absolute z-[9999] w-full mt-1 bg-white border border-slate-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredMandors.length > 0 ? (
            <ul className="py-1">
              {filteredMandors.map((mandor) => (
                <li
                  key={mandor.id}
                  onClick={() => handleSelect(mandor)}
                  className="px-3 py-2 cursor-pointer hover:bg-indigo-50 transition-colors text-sm"
                >
                  <div className="font-medium text-slate-900">{mandor.nama}</div>
                  {mandor.nomor_kontak && (
                    <div className="text-xs text-slate-500">Kontak: {mandor.nomor_kontak}</div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 text-slate-500 text-sm">
              {searchTerm ? 'Tidak ada hasil' : 'Tidak ada data'}
            </div>
          )}

          {showAddButton && (
            <div className="border-t border-slate-200 p-2">
              <button
                type="button"
                onClick={handleAddNewMandor}
                className="w-full px-4 py-2 text-left text-indigo-600 hover:bg-indigo-50 rounded transition-colors flex items-center gap-2 text-sm font-medium"
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
                <span>Tambah Mandor "{searchTerm.trim()}"</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

