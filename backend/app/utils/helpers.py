from typing import Any, Dict


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values dari dictionary
    Best practice: gunakan format_datetime_indonesia langsung dari formatters
    """
    return {k: v for k, v in data.items() if v is not None}
