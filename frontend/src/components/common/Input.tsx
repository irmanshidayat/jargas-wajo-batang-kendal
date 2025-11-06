import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-1">
          {label}
        </label>
      )}
      <input
        className={`w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-slate-700 transition-colors ${
          error ? 'border-red-400 focus:ring-red-400 focus:border-red-400' : ''
        } ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 font-medium">{error}</p>
      )}
    </div>
  )
}

export default Input
