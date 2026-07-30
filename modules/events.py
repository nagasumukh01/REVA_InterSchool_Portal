"""Event management business logic. No Streamlit imports."""

from utils import storage, helpers


def list_events(status: str | None = None) -> list[dict]:
    events = storage.read_table("events")
    if status:
        events = [e for e in events if e.get("registration_status") == status]
    return sorted(events, key=lambda e: e.get("created_at", ""), reverse=True)


def get_event(event_id: str) -> dict | None:
    return storage.get_row("events", event_id)


def create_event(data: dict, created_by: str) -> dict:
    data["created_at"] = helpers.now_iso()
    data["created_by"] = created_by
    data.setdefault("registration_status", "Open")
    event = storage.append_row("events", data)
    helpers.log_action(created_by, "CREATE_EVENT", f"Created event '{data.get('event_name')}'")
    return event


def update_event(event_id: str, updates: dict, updated_by: str) -> dict | None:
    updates["updated_at"] = helpers.now_iso()
    event = storage.update_row("events", event_id, updates)
    if event:
        helpers.log_action(updated_by, "UPDATE_EVENT", f"Updated event '{event.get('event_name')}'")
    return event


def delete_event(event_id: str, deleted_by: str) -> bool:
    event = storage.get_row("events", event_id)
    ok = storage.delete_row("events", event_id)
    if ok and event:
        helpers.log_action(deleted_by, "DELETE_EVENT", f"Deleted event '{event.get('event_name')}'")
    return ok


def clone_event(event_id: str, cloned_by: str) -> dict | None:
    event = storage.get_row("events", event_id)
    if not event:
        return None
    new_event = {k: v for k, v in event.items() if k != "id"}
    new_event["event_name"] = f"{new_event.get('event_name', 'Event')} (Copy)"
    new_event["registration_status"] = "Draft"
    return create_event(new_event, cloned_by)


def set_status(event_id: str, status: str, actor: str) -> dict | None:
    return update_event(event_id, {"registration_status": status}, actor)


def registration_count(event_id: str) -> int:
    return len(storage.find_rows("registrations", event_id=event_id))
