"""
Central configuration for the REVA InterSchool Competition Portal.

IMPORTANT (read this before wiring up a real backend):
This file, plus everything under utils/ and modules/, contains ZERO Streamlit
imports. That is intentional. When you're ready to move to Flask + a real
database, these modules become your Flask service layer almost unchanged —
only utils/storage.py needs to be swapped for real DB calls (see the note
at the top of that file).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# Storage backend switch
# --------------------------------------------------------------------------
# "json"  -> flat JSON files under /data  (current, zero-setup default)
# "flask" -> talk to a Flask API instead (fill in FLASK_API_BASE_URL below
#            and implement the matching functions in utils/storage.py when
#            you're ready to migrate)
STORAGE_BACKEND = os.getenv("REVA_STORAGE_BACKEND", "json")
FLASK_API_BASE_URL = os.getenv("REVA_API_BASE_URL", "http://localhost:5000/api")

# --------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------
COLORS = {
    "primary": "#F37021",       # REVA Orange
    "primary_dark": "#D45A0F",  # Hover
    "secondary": "#FFFFFF",
    "background": "#F7F7F7",
    "card": "#FFFFFF",
    "text": "#222222",
    "muted": "#6B7280",
    "success": "#1D9A5B",
    "warning": "#E0A800",
    "danger": "#D9534F",
    "info": "#2C7BE5",
}

FONT_FAMILY = "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"

# --------------------------------------------------------------------------
# Admin credentials (INITIAL / bootstrap only)
# --------------------------------------------------------------------------
# Stored hashed at first run inside data/admins.json. Change these via env
# vars before first run in a real deployment, or edit data/admins.json
# afterwards. Never commit real credentials.
DEFAULT_ADMINS = [
    {
        "admin_id": "director01",
        "name": "Sports Director",
        "email": os.getenv("REVA_ADMIN_EMAIL", "sportsdirector@reva.edu.in"),
        "password": os.getenv("REVA_ADMIN_PASSWORD", "Admin@REVA2026"),
        "role": "Sports Director",
    },
]

# --------------------------------------------------------------------------
# Schools & Branches (configurable)
# --------------------------------------------------------------------------
SCHOOLS = {
    "School of Computer Science & Engineering": [
        "AI", "AIML", "CSE", "Cyber Security", "Data Science", "IoT",
    ],
    "School of Mechanical Engineering": [
        "Mechanical", "Robotics", "Automobile",
    ],
    "School of Civil Engineering": [
        "Civil", "Construction Technology",
    ],
    "School of Electronics & Communication": [
        "ECE", "VLSI", "Embedded Systems",
    ],
    "School of Management Studies": [
        "BBA", "MBA", "International Business",
    ],
    "School of Commerce": [
        "B.Com General", "B.Com Honours", "B.Com CA",
    ],
    "School of Architecture": [
        "Architecture", "Interior Design",
    ],
    "School of Law": [
        "BA LLB", "BBA LLB",
    ],
    "School of Applied Sciences": [
        "Biotechnology", "Chemistry", "Physics", "Mathematics",
    ],
}

# --------------------------------------------------------------------------
# Sports categories
# --------------------------------------------------------------------------
SPORT_CATEGORIES = [
    "Football", "Basketball", "Volleyball", "Cricket", "Athletics",
    "Badminton", "Table Tennis", "Kabaddi", "Throwball", "Chess",
    "Kho-Kho", "Tennis", "Swimming",
]

# --------------------------------------------------------------------------
# Registration / upload rules
# --------------------------------------------------------------------------
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
MAX_UPLOAD_SIZE_MB = 10

REGISTRATION_STATUSES = ["Pending", "Approved", "Rejected"]
EVENT_STATUSES = ["Draft", "Open", "Closed", "Archived"]

SESSION_TIMEOUT_MINUTES = 60
