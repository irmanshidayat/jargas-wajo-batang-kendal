import { useState, useEffect, useRef } from 'react'
import type { Material } from '../services/inventoryService'

interface MaterialSelectorProps {
  value: string // kode_barang atau nama_barang yang ditampilkan
  materials: Material[]
  onSelect: (material: Material | null) => void
  onManualChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export default function MaterialSelector({
  value,
  materials,
  onSelect,
  onManualChange,
  placeholder = 'Ketik kode atau nama barang...',
  disabled = false,
}: MaterialSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredMaterials, setFilteredMaterials] = useState<Material[]>([])
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredMaterials(materials.filter(m => m.is_active === 1).slice(0, 50))
    } else {
      const term = searchTerm.toLowerCase()
      const filtered = materials
        .filter((material) => material.is_active === 1)
        .filter((material) => {
          const kodeBarang = (material.kode_barang || '').toLowerCase()
          const namaBarang = material.nama_barang.toLowerCase()
          return kodeBarang.includes(term) || namaBarang.includes(term)
        })
        .slice(0, 50) // Limit results untuk performa
      setFilteredMaterials(filtered)
    }
  }, [searchTerm, materials])

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

  const handleSelect = (material: Material) => {
    onSelect(material)
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

  const formatMaterialLabel = (material: Material): string => {
    if (material.kode_barang) {
      return `${material.kode_barang} - ${material.nama_barang}`
    }
    return material.nama_barang
  }

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
        className="w-full px-2 py-1 border-0 focus:outline-none focus:ring-1 focus:ring-indigo-500 rounded"
        disabled={disabled}
      />
      
      {isOpen && !disabled && (
        <div className="absolute z-[9999] w-full mt-1 bg-white border border-slate-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredMaterials.length > 0 ? (
            <ul className="py-1">
              {filteredMaterials.map((material) => (
                <li
                  key={material.id}
                  onClick={() => handleSelect(material)}
                  className="px-3 py-2 cursor-pointer hover:bg-indigo-50 transition-colors text-sm"
                >
                  <div className="font-medium">{formatMaterialLabel(material)}</div>
                  {material.satuan && (
                    <div className="text-xs text-slate-500">Satuan: {material.satuan}</div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 text-slate-500 text-sm">
              {searchTerm ? 'Tidak ada hasil' : 'Tidak ada data'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

