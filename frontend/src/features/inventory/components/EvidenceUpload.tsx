import { useState } from 'react'

interface EvidenceUploadProps {
  files: File[]
  onChange: (files: File[]) => void
  maxFiles?: number
  maxSize?: number // in MB
  label?: string
  inputId?: string
}

export default function EvidenceUpload({
  files,
  onChange,
  maxFiles = 5,
  maxSize = 5,
  label,
  inputId = 'evidence-upload',
}: EvidenceUploadProps) {
  const [error, setError] = useState<string>('')

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    setError('')

    // Validate file count
    if (files.length + selectedFiles.length > maxFiles) {
      setError(`Maksimal ${maxFiles} file`)
      return
    }

    // Validate file size and type
    const validFiles: File[] = []
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

    selectedFiles.forEach((file) => {
      // Check file type
      if (!allowedTypes.includes(file.type)) {
        setError(`${file.name}: Format file tidak didukung (hanya JPG, PNG, PDF)`)
        return
      }

      // Check file size (MB to bytes)
      if (file.size > maxSize * 1024 * 1024) {
        setError(`${file.name}: Ukuran file maksimal ${maxSize}MB`)
        return
      }

      validFiles.push(file)
    })

    onChange([...files, ...validFiles])
    event.target.value = '' // Reset input
  }

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    onChange(newFiles)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label || `Upload Evidence (Maksimal ${maxFiles} file, ${maxSize}MB per file)`}
      </label>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
        <input
          type="file"
          multiple
          accept="image/jpeg,image/jpg,image/png,application/pdf"
          onChange={handleFileSelect}
          className="hidden"
          id={inputId}
          disabled={files.length >= maxFiles}
        />
        <label
          htmlFor={inputId}
          className={`cursor-pointer ${files.length >= maxFiles ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="text-sm text-gray-600">
              Klik untuk upload atau drag & drop
            </p>
            <p className="text-xs text-gray-500">
              PNG, JPG, PDF hingga {maxSize}MB
            </p>
          </div>
        </label>
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600">{error}</div>
      )}

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                <span className="text-sm text-gray-700 truncate">{file.name}</span>
                <span className="text-xs text-gray-500">
                  ({formatFileSize(file.size)})
                </span>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="ml-2 text-red-600 hover:text-red-800"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

