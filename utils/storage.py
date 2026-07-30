"""
Storage abstraction layer.

WHY THIS FILE EXISTS
---------------------
Every other module (modules/auth.py, modules/events.py, modules/registrations.py,
modules/reports.py) talks to data ONLY through the functions in this file
(read_table / write_table / next_id / append_row / update_row / delete_row).
They never touch a JSON file, a SQL connection, or an HTTP client directly.

That means when you're ready to move to a real database:

  1. Stand up your Flask API with endpoints like
     GET/POST/PUT/DELETE /api/<table>  and  /api/<table>/<id>
  2. Set STORAGE_BACKEND = "flask" in config.py (or the env var)
  3. Fill in the `_flask_*` functions below to call `requests.get/post/...`
     against FLASK_API_BASE_URL instead of reading JSON files.
  4. Nothing in modules/ or the Streamlit pages needs to change.

CURRENT BACKEND ("json")
-------------------------
Each "table" is a single JSON file in /data, holding a list of dict "rows".
This is intentionally simple (no concurrent-write locking beyond a basic
file lock) - fine for a single-admin, low-concurrency portal during
development. Swap it out before you have real concurrent traffic.
"""

import json
import threading
import uuid
from pathlib import Path
from typing import Any

import config

_LOCK = threading.Lock()

TABLES = [
    "users", "schools", "branches", "events", "registrations",
    "captains", "vicecaptains", "documents", "admins",
    "announcements", "auditlogs",
]


# --------------------------------------------------------------------------
# JSON backend
# --------------------------------------------------------------------------
def _table_path(table: str) -> Path:
    return config.DATA_DIR / f"{table}.json"


def _json_read_table(table: str) -> list[dict[str, Any]]:
    path = _table_path(table)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _json_write_table(table: str, rows: list[dict[str, Any]]) -> None:
    path = _table_path(table)
    with _LOCK:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, default=str)


# --------------------------------------------------------------------------
# Flask backend (stub — implement when you migrate)
# --------------------------------------------------------------------------
def _flask_read_table(table: str) -> list[dict[str, Any]]:
    import requests
    resp = requests.get(f"{config.FLASK_API_BASE_URL}/{table}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def _flask_write_table(table: str, rows: list[dict[str, Any]]) -> None:
    raise NotImplementedError(
        "Bulk write isn't a good fit for a real API. Use append_row / "
        "update_row / delete_row instead once STORAGE_BACKEND='flask'."
    )


# --------------------------------------------------------------------------
# Public API used by everything else in the app
# --------------------------------------------------------------------------
def read_table(table: str) -> list[dict[str, Any]]:
    if config.STORAGE_BACKEND == "flask":
        return _flask_read_table(table)
    return _json_read_table(table)


def write_table(table: str, rows: list[dict[str, Any]]) -> None:
    if config.STORAGE_BACKEND == "flask":
        _flask_write_table(table, rows)
        return
    _json_write_table(table, rows)


def next_id() -> str:
    """Generate a short unique id (works fine as a swap-in for a DB PK)."""
    return uuid.uuid4().hex[:12]


def append_row(table: str, row: dict[str, Any]) -> dict[str, Any]:
    if "id" not in row:
        row["id"] = next_id()
    rows = read_table(table)
    rows.append(row)
    write_table(table, rows)
    return row


def update_row(table: str, row_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    rows = read_table(table)
    for row in rows:
        if row.get("id") == row_id:
            row.update(updates)
            write_table(table, rows)
            return row
    return None


def delete_row(table: str, row_id: str) -> bool:
    rows = read_table(table)
    new_rows = [r for r in rows if r.get("id") != row_id]
    if len(new_rows) == len(rows):
        return False
    write_table(table, new_rows)
    return True


def get_row(table: str, row_id: str) -> dict[str, Any] | None:
    for row in read_table(table):
        if row.get("id") == row_id:
            return row
    return None


def find_rows(table: str, **filters) -> list[dict[str, Any]]:
    rows = read_table(table)
    result = []
    for row in rows:
        if all(row.get(k) == v for k, v in filters.items()):
            result.append(row)
    return result
