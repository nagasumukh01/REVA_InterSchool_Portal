"""Small shared utilities: dates, formatting, file saving."""

from datetime import datetime, date
from pathlib import Path

import config


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def parse_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def is_registration_open(event: dict) -> bool:
    if event.get("registration_status") != "Open":
        return False
    end = parse_date(event.get("registration_end_date"))
    if end is None:
        return True
    return date.today() <= end


def days_until(target) -> int | None:
    d = parse_date(target)
    if d is None:
        return None
    return (d - date.today()).days


def format_date(value) -> str:
    d = parse_date(value)
    return d.strftime("%d %b %Y") if d else "-"


def save_uploaded_file(uploaded_file, subfolder: str) -> str:
    """Save a Streamlit UploadedFile to disk, return the relative path."""
    folder = config.UPLOAD_DIR / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
    dest = folder / safe_name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest.relative_to(config.BASE_DIR))


def log_action(actor: str, action: str, details: str = ""):
    from utils import storage
    storage.append_row("auditlogs", {
        "actor": actor,
        "action": action,
        "details": details,
        "timestamp": now_iso(),
    })
