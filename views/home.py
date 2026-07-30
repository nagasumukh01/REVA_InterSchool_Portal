import streamlit as st

import config
from modules import events as events_mod, notifications
from utils import ui, helpers


def render():
    ui.hero(
        "Welcome to the REVA InterSchool Competition Portal",
        "The official platform for registering, managing, and tracking inter-school "
        "sporting events across REVA University. Built for Sports Vertical Heads and "
        "the Sports Department to run a fair, transparent, and efficient competition.",
    )

    all_events = events_mod.list_events()
    open_events = [e for e in all_events if e.get("registration_status") == "Open"]
    total_regs = len(_all_registrations())
    schools_count = len(config.SCHOOLS)

    ui.section_title("At a Glance")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card("Events Conducted", len(all_events), orange=True)
    with c2:
        ui.metric_card("Open for Registration", len(open_events))
    with c3:
        ui.metric_card("Schools Participating", schools_count)
    with c4:
        ui.metric_card("Players Registered", total_regs * 2)  # captain + vice-captain per team

    ui.section_title("Upcoming Events")
    if not open_events:
        ui.empty_state("No events are currently open for registration. Please check back soon.")
    else:
        cols = st.columns(3)
        for i, e in enumerate(open_events[:6]):
            with cols[i % 3]:
                _event_card(e)

    ui.section_title("Latest Announcements")
    ann = notifications.list_announcements(limit=3)
    if not ann:
        ui.empty_state("No announcements yet.", icon="📢")
    else:
        for a in ann:
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:10px;">
                    <strong>{a['title']}</strong>
                    <div style="color:#6B7280;font-size:13px;margin-top:4px;">{helpers.format_date(a['created_at'])}</div>
                    <div style="margin-top:8px;">{a['message']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    col_a, col_b, _ = st.columns([1, 1, 3])
    with col_a:
        if st.button("School Sports Head Login", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.login_role = "school_head"
            st.rerun()
    with col_b:
        if st.button("Admin Login", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.login_role = "admin"
            st.rerun()

    ui.footer()


def _event_card(e):
    reg_count = events_mod.registration_count(e["id"])
    days_left = helpers.days_until(e.get("registration_end_date"))
    deadline_text = f"{days_left} day(s) left" if days_left is not None and days_left >= 0 else "Deadline passed"
    st.markdown(
        f"""
        <div class="reva-card" style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:16px;">{e.get('event_name','')}</strong>
                {ui.status_badge_html(e.get('registration_status','Open'))}
            </div>
            <div style="color:#6B7280;font-size:13px;margin-top:6px;">🏟️ {e.get('venue','TBA')}</div>
            <div style="color:#6B7280;font-size:13px;">🗓️ Event: {helpers.format_date(e.get('event_date'))}</div>
            <div style="color:#F37021;font-weight:700;font-size:13px;margin-top:6px;">⏳ {deadline_text}</div>
            <div style="color:#6B7280;font-size:13px;margin-top:4px;">👥 {reg_count} Schools Registered</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View Details", key=f"home_view_{e['id']}", use_container_width=True):
        st.session_state.selected_event_id = e["id"]
        st.session_state.page = "event_details"
        st.rerun()


def _all_registrations():
    from utils import storage
    return storage.read_table("registrations")
