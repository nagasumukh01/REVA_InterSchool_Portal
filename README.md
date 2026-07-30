# REVA InterSchool Competition Portal

Official Streamlit portal for managing REVA InterSchool Competition registrations —
event management, role-based login, team registration workflow, admin analytics,
and Excel/CSV/PDF reporting.

## Current architecture (important)

- **Frontend/UI:** Streamlit (`app.py`, `views/`, `utils/ui.py`)
- **Business logic:** `modules/` — pure Python, **no Streamlit imports**. Auth,
  event rules, registration validation, and report generation all live here so
  they can be reused as-is inside a Flask service later.
- **Data storage:** `utils/storage.py` — currently flat **JSON files** under
  `/data` (one file per "table": `events.json`, `registrations.json`, etc).
  This is a deliberate placeholder until you pick a real database.

### Swapping in a real backend later

You told us the database is TBD and Flask will be the eventual backend. This
project is already structured for that hand-off:

1. Everything in `modules/` and `utils/validators.py` / `utils/helpers.py`
   is UI-agnostic — it can be lifted almost unchanged into Flask route
   handlers or service classes.
2. `utils/storage.py` is the **only** place that knows how data is persisted.
   Build your Flask API (`/api/events`, `/api/registrations`, etc.), then:
   - set `REVA_STORAGE_BACKEND=flask` and `REVA_API_BASE_URL=...` in `.env`
   - fill in the `_flask_read_table` / add `_flask_*` write functions in
     `utils/storage.py` to call `requests.get/post/put/delete`
   - nothing in `modules/` or `views/` needs to change.
3. When you land on a real database (PostgreSQL, MySQL, etc.), that change
   only touches the Flask side — this Streamlit app keeps talking to the API
   the same way.

Until then, everything just works out of the box with local JSON files —
no database setup required.

## Folder structure

```
REVA_InterSchool_Competition/
├── app.py                  # Streamlit entry point / router
├── config.py                # theme, schools, branches, sport list, constants
├── requirements.txt
├── .streamlit/config.toml   # Streamlit theme
├── .env.example              # copy to .env and edit
│
├── assets/
│   ├── logos/
│   ├── banners/
│   └── css/style.css
│
├── views/                   # Streamlit page renderers (UI layer only)
│   ├── home.py
│   ├── login.py
│   ├── user_dashboard.py
│   ├── event_details.py
│   ├── register_form.py
│   ├── admin_dashboard.py
│   ├── admin_events.py
│   ├── admin_registrations.py
│   └── admin_reports.py
│
├── modules/                  # Business logic — NO Streamlit imports
│   ├── auth.py
│   ├── events.py
│   ├── registrations.py
│   ├── reports.py
│   └── notifications.py
│
├── utils/
│   ├── storage.py            # data access layer (JSON now, swappable)
│   ├── validators.py
│   ├── helpers.py
│   └── ui.py                 # shared Streamlit UI components
│
├── data/                      # JSON "tables" (auto-created, gitignored)
└── uploads/                   # uploaded team lists / event images
```

> Note: page files live in `views/` rather than Streamlit's auto-discovered
> `pages/` folder. This was intentional — role-based routing (admin vs.
> school head) needs a controlled state machine, which Streamlit's automatic
> multi-page sidebar doesn't support well. `app.py` handles routing via
> `st.session_state.page`.

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (optional — sensible defaults exist)
cp .env.example .env
# edit .env to set your own bootstrap admin email/password

# 4. Run
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Default accounts (first run only)

These are created automatically the first time the app runs (stored hashed
in `data/admins.json` / `data/users.json`). Change them immediately in a
real deployment via `.env` before first run, or edit the login/password
afterwards through the admin panel.

| Role | Login | Password |
|---|---|---|
| Admin | `sportsdirector@reva.edu.in` (or your `.env` value) | `Admin@REVA2026` (or your `.env` value) |
| School Sports Head (demo) | `sportshead.cse@reva.edu.in` | `Demo@1234` |
| School Sports Head (demo) | `sportshead.mech@reva.edu.in` | `Demo@1234` |

New School Sports Vertical Heads can also self-register from the login page.

## Configuring schools, branches, and sports

Edit `config.py`:

- `SCHOOLS` — dict of school name → list of branches. Add/remove schools or
  branches here; the registration form and filters pick this up automatically.
- `SPORT_CATEGORIES` — list of sports offered.
- `COLORS` — theme colors (REVA Orange `#F37021` by default).
- `ALLOWED_UPLOAD_EXTENSIONS`, `MAX_UPLOAD_SIZE_MB` — file upload rules.

## Deployment

- Works out of the box on **Streamlit Community Cloud** or **Render** — just
  point at `app.py`, set the environment variables from `.env.example` in
  the platform's secrets/env settings, and deploy.
- No hardcoded paths or credentials — everything goes through `config.py`
  and environment variables.
- `data/` and `uploads/` are gitignored; make sure your deployment target
  has persistent storage if you need registrations to survive restarts
  (or migrate to the Flask + database backend described above, which is the
  recommended path for production use).

## Security notes

- Passwords are hashed with `bcrypt` — never stored in plaintext.
- File uploads are restricted by extension (`.pdf`, `.docx`, `.xlsx`) and
  size (10 MB default).
- All form inputs go through validators in `utils/validators.py`.
- Every create/update/delete/login action is written to `data/auditlogs.json`
  via `utils/helpers.log_action`.
- This JSON-file setup is meant for development/small-scale use. For
  production with real concurrent traffic, move to the Flask + database
  backend described above.
