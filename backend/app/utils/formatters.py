from datetime import date, datetime
from typing import Optional


def format_currency(amount: float) -> str:
    """Format number ke currency Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")


def format_phone_number(phone: str) -> str:
    """Format phone number ke format Indonesia"""
    phone_clean = "".join(filter(str.isdigit, phone))
    if len(phone_clean) >= 10:
        return f"{phone_clean[:4]}-{phone_clean[4:8]}-{phone_clean[8:]}"
    return phone


def format_nik(nik: str) -> str:
    """Format NIK dengan separator"""
    if len(nik) == 16:
        return f"{nik[:4]}.{nik[4:8]}.{nik[8:12]}.{nik[12:]}"
    return nik


def format_date_indonesia(dt: Optional[date]) -> str:
    """Format date to DD/MM/YYYY format Indonesia"""
    if not dt:
        return ""
    return dt.strftime("%d/%m/%Y")


def format_datetime_indonesia(dt: datetime) -> str:
    """Format datetime ke string Indonesia (DD Month YYYY, HH:MM:SS)"""
    return dt.strftime("%d %B %Y, %H:%M:%S")
