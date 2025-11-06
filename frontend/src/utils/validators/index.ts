export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^[0-9]{10,13}$/
  return phoneRegex.test(phone.replace(/\D/g, ''))
}

export const validateNIK = (nik: string): boolean => {
  return /^[0-9]{16}$/.test(nik)
}
