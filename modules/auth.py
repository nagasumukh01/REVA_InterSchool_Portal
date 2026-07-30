"""
Authentication & authorization logic.

Two roles:
- admin        (Sports Director / Assistant Sports Directors)
- school_head  (School Sports Vertical Heads, logged in via college email or ID)

No Streamlit imports here on purpose — this is pure business logic that can
be lifted into a Flask auth endpoint later with minimal changes.
"""

import bcrypt

import config
from utils import storage, helpers


# --------------------------------------------------------------------------
# Bootstrap / seeding
# --------------------------------------------------------------------------
def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


def seed_defaults():
    """Create default admin + a few demo school-head accounts on first run."""
    admins = storage.read_table("admins")
    if not admins:
        for admin in config.DEFAULT_ADMINS:
            storage.append_row("admins", {
                "admin_id": admin["admin_id"],
                "name": admin["name"],
                "email": admin["email"],
                "password_hash": _hash_password(admin["password"]),
                "role": admin["role"],
                "created_at": helpers.now_iso(),
            })

    users = storage.read_table("users")
    if not users:
        demo_heads = [
            {
                "login_id": "sportshead.cse@reva.edu.in",
                "name": "Demo CSE Sports Head",
                "school": "School of Computer Science & Engineering",
                "password": "Demo@1234",
            },
            {
                "login_id": "sportshead.mech@reva.edu.in",
                "name": "Demo Mechanical Sports Head",
                "school": "School of Mechanical Engineering",
                "password": "Demo@1234",
            },
        ]
        for u in demo_heads:
            storage.append_row("users", {
                "login_id": u["login_id"],
                "name": u["name"],
                "school": u["school"],
                "password_hash": _hash_password(u["password"]),
                "role": "school_head",
                "created_at": helpers.now_iso(),
            })


# --------------------------------------------------------------------------
# Login
# --------------------------------------------------------------------------
def login_admin(email: str, password: str) -> dict | None:
    email = (email or "").strip().lower()
    for admin in storage.read_table("admins"):
        if admin.get("email", "").lower() == email and _check_password(password, admin.get("password_hash", "")):
            helpers.log_action(admin["admin_id"], "LOGIN", "Admin login")
            return {**admin, "role": "admin"}
    return None


def login_school_head(login_id: str, password: str) -> dict | None:
    login_id = (login_id or "").strip().lower()
    for user in storage.read_table("users"):
        if user.get("login_id", "").lower() == login_id and _check_password(password, user.get("password_hash", "")):
            helpers.log_action(user["login_id"], "LOGIN", "School head login")
            return user
    return None


def register_school_head(login_id: str, name: str, school: str, password: str) -> tuple[bool, str]:
    """Self-service account creation for a school sports vertical head (optional flow)."""
    login_id = (login_id or "").strip().lower()
    if not login_id or not name or not school or not password:
        return False, "All fields are required."
    if storage.find_rows("users", login_id=login_id):
        return False, "An account with this email/ID already exists."
    storage.append_row("users", {
        "login_id": login_id,
        "name": name,
        "school": school,
        "password_hash": _hash_password(password),
        "role": "school_head",
        "created_at": helpers.now_iso(),
    })
    return True, "Account created successfully. You can now log in."
