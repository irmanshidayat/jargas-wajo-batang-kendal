// Date formatting
export const formatDate = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// Currency formatting
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
  }).format(amount)
}

// Phone number formatting
export const formatPhoneNumber = (phone: string): string => {
  return phone.replace(/(\d{4})(\d{4})(\d{4})/, '$1-$2-$3')
}

// NIK formatting
export const formatNIK = (nik: string): string => {
  return nik.replace(/(\d{4})(\d{4})(\d{4})(\d{4})/, '$1.$2.$3.$4')
}
