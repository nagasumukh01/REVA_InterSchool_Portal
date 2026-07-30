"""Pure validation helpers — no Streamlit, no storage. Safe to reuse in Flask later."""

import re
from pathlib import Path

import config

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")  # 10-digit Indian mobile
SRN_RE = re.compile(r"^[A-Za-z0-9]{6,15}$")


def is_valid_email(email: str, require_college_domain: bool = False) -> bool:
    if not email or not EMAIL_RE.match(email.strip()):
        return False
    if require_college_domain:
        return email.strip().lower().endswith("@reva.edu.in")
    return True


def is_valid_phone(phone: str) -> bool:
    return bool(phone and PHONE_RE.match(phone.strip()))


def is_valid_srn(srn: str) -> bool:
    return bool(srn and SRN_RE.match(srn.strip()))


def is_valid_file(filename: str, size_bytes: int) -> tuple[bool, str]:
    ext = Path(filename).suffix.lower()
    if ext not in config.ALLOWED_UPLOAD_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Allowed: {', '.join(config.ALLOWED_UPLOAD_EXTENSIONS)}"
    max_bytes = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File exceeds maximum size of {config.MAX_UPLOAD_SIZE_MB} MB."
    return True, ""


def required(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    return True


def sanitize_text(value: str) -> str:
    """Basic input sanitization for free-text fields."""
    if not value:
        return ""
    value = value.strip()
    # Strip characters commonly used in injection/script attempts.
    value = re.sub(r"[<>{};]", "", value)
    return value
