"""Team registration workflow business logic. No Streamlit imports."""

from utils import storage, helpers, validators


def list_registrations(**filters) -> list[dict]:
    regs = storage.find_rows("registrations", **filters)
    return sorted(regs, key=lambda r: r.get("registered_at", ""), reverse=True)


def get_registration(reg_id: str) -> dict | None:
    return storage.get_row("registrations", reg_id)


def already_registered(event_id: str, school: str) -> bool:
    return bool(storage.find_rows("registrations", event_id=event_id, school=school))


def is_duplicate_srn(event_id: str, srn: str) -> bool:
    srn = srn.strip().upper()
    for reg in storage.find_rows("registrations", event_id=event_id):
        if reg.get("captain_srn", "").upper() == srn or reg.get("vice_captain_srn", "").upper() == srn:
            return True
    return False


def validate_registration(form: dict, event: dict, exclude_registration_id: str | None = None) -> list[str]:
    """Run all validations described in the spec. Returns a list of error messages.

    exclude_registration_id: when editing an existing registration, pass its id
    so duplicate checks don't flag the record against itself.
    """
    errors: list[str] = []

    if not helpers.is_registration_open(event):
        errors.append("Registration for this event is closed.")

    # Section 1 — Vertical Head
    for field in ("vh_name", "vh_college_id", "vh_school", "vh_department", "vh_contact", "vh_email", "vh_designation"):
        if not validators.required(form.get(field)):
            errors.append(f"'{field}' is required.")
    if form.get("vh_email") and not validators.is_valid_email(form["vh_email"]):
        errors.append("Vertical Head email is not a valid email address.")
    if form.get("vh_contact") and not validators.is_valid_phone(form["vh_contact"]):
        errors.append("Vertical Head contact number must be a valid 10-digit mobile number.")

    # Section 2 — Captain
    for field in ("captain_name", "captain_srn", "captain_semester", "captain_branch", "captain_phone", "captain_email", "captain_gender"):
        if not validators.required(form.get(field)):
            errors.append(f"Captain '{field}' is required.")
    if form.get("captain_email") and not validators.is_valid_email(form["captain_email"]):
        errors.append("Captain email is not valid.")
    if form.get("captain_phone") and not validators.is_valid_phone(form["captain_phone"]):
        errors.append("Captain phone number must be a valid 10-digit mobile number.")
    if form.get("captain_srn") and not validators.is_valid_srn(form["captain_srn"]):
        errors.append("Captain SRN format looks invalid.")

    # Section 3 — Vice Captain
    for field in ("vice_captain_name", "vice_captain_srn", "vice_captain_semester", "vice_captain_branch", "vice_captain_phone", "vice_captain_email", "vice_captain_gender"):
        if not validators.required(form.get(field)):
            errors.append(f"Vice-Captain '{field}' is required.")
    if form.get("vice_captain_email") and not validators.is_valid_email(form["vice_captain_email"]):
        errors.append("Vice-Captain email is not valid.")
    if form.get("vice_captain_phone") and not validators.is_valid_phone(form["vice_captain_phone"]):
        errors.append("Vice-Captain phone number must be a valid 10-digit mobile number.")
    if form.get("vice_captain_srn") and not validators.is_valid_srn(form["vice_captain_srn"]):
        errors.append("Vice-Captain SRN format looks invalid.")

    if form.get("captain_srn") and form.get("vice_captain_srn") and \
            form["captain_srn"].strip().upper() == form["vice_captain_srn"].strip().upper():
        errors.append("Captain and Vice-Captain cannot be the same person (same SRN).")

    # Section 5 — Declaration
    if not form.get("declaration_accepted"):
        errors.append("You must accept the declaration to submit.")
    if not validators.required(form.get("digital_signature")):
        errors.append("Digital signature (name) is required.")

    # Duplicate checks (an existing registration being edited is excluded from these)
    event_id = event.get("id")
    other_regs = [r for r in storage.find_rows("registrations", event_id=event_id)
                  if r.get("id") != exclude_registration_id]

    if any(r.get("school") == form.get("vh_school") for r in other_regs):
        errors.append("Your school has already registered a team for this event.")

    captain_srn = (form.get("captain_srn") or "").strip().upper()
    vice_srn = (form.get("vice_captain_srn") or "").strip().upper()
    for r in other_regs:
        if captain_srn and captain_srn in {r.get("captain_srn", "").upper(), r.get("vice_captain_srn", "").upper()}:
            errors.append("This Captain SRN is already registered for this event by another team.")
            break
    for r in other_regs:
        if vice_srn and vice_srn in {r.get("captain_srn", "").upper(), r.get("vice_captain_srn", "").upper()}:
            errors.append("This Vice-Captain SRN is already registered for this event by another team.")
            break

    # Max teams
    max_teams = event.get("max_teams")
    if max_teams and exclude_registration_id is None:
        try:
            if len(other_regs) >= int(max_teams):
                errors.append("This event has reached its maximum number of teams.")
        except (ValueError, TypeError):
            pass

    return errors


def create_registration(form: dict, event_id: str, file_path: str | None, submitted_by: str) -> dict:
    row = dict(form)
    row["event_id"] = event_id
    row["school"] = form.get("vh_school")
    row["branch"] = form.get("vh_department")
    row["file_path"] = file_path
    row["status"] = "Pending"
    row["registered_at"] = helpers.now_iso()
    row["submitted_by"] = submitted_by
    reg = storage.append_row("registrations", row)
    helpers.log_action(submitted_by, "SUBMIT_REGISTRATION", f"Registered for event {event_id}")
    return reg


def update_registration(reg_id: str, updates: dict, actor: str) -> dict | None:
    updates["updated_at"] = helpers.now_iso()
    reg = storage.update_row("registrations", reg_id, updates)
    if reg:
        helpers.log_action(actor, "UPDATE_REGISTRATION", f"Updated registration {reg_id}")
    return reg


def set_status(reg_id: str, status: str, actor: str) -> dict | None:
    return update_registration(reg_id, {"status": status}, actor)


def can_edit(reg: dict, event: dict) -> bool:
    return helpers.is_registration_open(event) and reg.get("status") == "Pending"
