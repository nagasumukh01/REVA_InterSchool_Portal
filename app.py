"""
REVA InterSchool Competition Portal — Streamlit entry point.

This file only handles: page config, session bootstrap, and routing between
views/. All business logic lives in modules/ (no Streamlit imports there),
all data access goes through utils/storage.py (currently JSON files, see
that file's docstring for how to swap in a Flask backend later).
"""

import streamlit as st
from streamlit_option_menu import option_menu

import config
from modules import auth
from utils import ui
from views import (
    home, login, user_dashboard, event_details, register_form,
    admin_dashboard, admin_events, admin_registrations, admin_reports,
)

st.set_page_config(
    page_title="REVA InterSchool Competition Portal",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Bootstrap
# --------------------------------------------------------------------------
auth.seed_defaults()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "auth" not in st.session_state:
    st.session_state.auth = None
if "admin_nav" not in st.session_state:
    st.session_state.admin_nav = "Dashboard"

ui.inject_css()
ui.header()

current_auth = st.session_state.auth

# --------------------------------------------------------------------------
# Guard: keep users out of pages that don't match their role
# --------------------------------------------------------------------------
protected_school_pages = {"user_dashboard", "register_form"}
protected_admin_pages = {"admin_dashboard", "admin_manage"}

if st.session_state.page in protected_school_pages and (not current_auth or current_auth.get("role") != "school_head"):
    st.session_state.page = "login"
    st.session_state.login_role = "school_head"

if st.session_state.page in protected_admin_pages and (not current_auth or current_auth.get("role") != "admin"):
    st.session_state.page = "login"
    st.session_state.login_role = "admin"

# --------------------------------------------------------------------------
# Admin gets a persistent sidebar nav once logged in
# --------------------------------------------------------------------------
if current_auth and current_auth.get("role") == "admin" and st.session_state.page.startswith("admin"):
    with st.sidebar:
        st.markdown(f"**{current_auth['name']}**")
        st.caption(current_auth.get("role", "Admin"))
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Events", "Registrations", "Reports"],
            icons=["speedometer2", "calendar-event", "clipboard-check", "bar-chart"],
            default_index=["Dashboard", "Events", "Registrations", "Reports"].index(st.session_state.admin_nav),
        )
        st.session_state.admin_nav = selected

    if selected == "Dashboard":
        admin_dashboard.render()
    elif selected == "Events":
        admin_events.render()
    elif selected == "Registrations":
        admin_registrations.render()
    elif selected == "Reports":
        admin_reports.render()

else:
    # --------------------------------------------------------------------
    # Simple state-machine routing for everything else
    # --------------------------------------------------------------------
    page = st.session_state.page

    if page == "home":
        home.render()
    elif page == "login":
        login.render()
    elif page == "user_dashboard":
        user_dashboard.render()
    elif page == "event_details":
        event_details.render()
    elif page == "register_form":
        register_form.render()
    elif page == "admin_dashboard":
        st.session_state.admin_nav = "Dashboard"
        st.rerun()
    else:
        st.session_state.page = "home"
        st.rerun()
