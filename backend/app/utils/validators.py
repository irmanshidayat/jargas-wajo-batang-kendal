import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number (Indonesia format)"""
    # Remove non-digit characters
    phone_clean = re.sub(r'\D', '', phone)
    # Check if it's 10-13 digits
    return 10 <= len(phone_clean) <= 13 and phone_clean.isdigit()


def validate_nik(nik: str) -> bool:
    """Validate NIK format (16 digits)"""
    return len(nik) == 16 and nik.isdigit()
