"""Announcement storage + notification message builders. No Streamlit imports.
(Actual toast display happens in the UI layer via st.toast, which just calls
functions from here to decide *what* to show.)"""

from utils import storage, helpers


def list_announcements(limit: int = 10) -> list[dict]:
    items = storage.read_table("announcements")
    return sorted(items, key=lambda a: a.get("created_at", ""), reverse=True)[:limit]


def create_announcement(title: str, message: str, created_by: str) -> dict:
    return storage.append_row("announcements", {
        "title": title,
        "message": message,
        "created_by": created_by,
        "created_at": helpers.now_iso(),
    })


def update_announcement(ann_id: str, title: str, message: str) -> dict | None:
    return storage.update_row("announcements", ann_id, {
        "title": title,
        "message": message,
        "updated_at": helpers.now_iso(),
    })


def delete_announcement(ann_id: str) -> bool:
    return storage.delete_row("announcements", ann_id)


def deadline_warnings(events: list[dict], within_days: int = 3) -> list[dict]:
    """Return events whose registration deadline is within `within_days` days."""
    warnings = []
    for e in events:
        days = helpers.days_until(e.get("registration_end_date"))
        if days is not None and 0 <= days <= within_days and e.get("registration_status") == "Open":
            warnings.append({**e, "days_left": days})
    return warnings
