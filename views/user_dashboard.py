import streamlit as st

from modules import events as events_mod, registrations as reg_mod, notifications
from utils import ui, helpers


def render():
    auth = st.session_state.auth
    st.markdown(f"### 👋 Welcome, {auth['name']}")
    st.caption(f"{auth.get('school','')}")

    all_events = events_mod.list_events()
    my_regs = reg_mod.list_registrations(school=auth.get("school"))
    my_event_ids = {r["event_id"] for r in my_regs}

    warnings = notifications.deadline_warnings(all_events)
    for w in warnings:
        st.warning(f"⏳ Registration for **{w['event_name']}** closes in {w['days_left']} day(s).")

    c1, c2, c3 = st.columns(3)
    with c1:
        ui.metric_card("Open Events", len([e for e in all_events if e.get("registration_status") == "Open"]), orange=True)
    with c2:
        ui.metric_card("My Registrations", len(my_regs))
    with c3:
        ui.metric_card("Approved", len([r for r in my_regs if r.get("status") == "Approved"]))

    ui.section_title("Available Events")
    open_events = [e for e in all_events if e.get("registration_status") in ("Open", "Closed")]
    if not open_events:
        ui.empty_state("No events published yet.")
    else:
        cols = st.columns(2)
        for i, e in enumerate(open_events):
            with cols[i % 2]:
                _event_row(e, my_event_ids)

    ui.section_title("My School's Registrations")
    if not my_regs:
        ui.empty_state("You haven't registered for any events yet.", icon="📝")
    else:
        for r in my_regs:
            event = events_mod.get_event(r["event_id"])
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;">
                        <strong>{event.get('event_name','(deleted event)') if event else '(deleted event)'}</strong>
                        {ui.status_badge_html(r.get('status','Pending'))}
                    </div>
                    <div style="color:#6B7280;font-size:13px;margin-top:4px;">
                        Captain: {r.get('captain_name','')} &nbsp;|&nbsp; Vice-Captain: {r.get('vice_captain_name','')}
                    </div>
                    <div style="color:#6B7280;font-size:13px;">Submitted on {helpers.format_date(r.get('registered_at'))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if event and reg_mod.can_edit(r, event):
                if st.button("Edit Registration", key=f"edit_{r['id']}"):
                    st.session_state.edit_registration_id = r["id"]
                    st.session_state.selected_event_id = event["id"]
                    st.session_state.page = "register_form"
                    st.rerun()

    st.write("")
    if st.button("Logout"):
        st.session_state.auth = None
        st.session_state.page = "home"
        st.rerun()

    ui.footer()


def _event_row(e, my_event_ids):
    reg_count = events_mod.registration_count(e["id"])
    already = e["id"] in my_event_ids
    st.markdown(
        f"""
        <div class="reva-card" style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:16px;">{e.get('event_name','')}</strong>
                {ui.status_badge_html(e.get('registration_status','Open'))}
            </div>
            <div style="color:#6B7280;font-size:13px;margin-top:6px;">🏟️ {e.get('venue','TBA')} &nbsp;|&nbsp; 🎽 {e.get('sport_category','')}</div>
            <div style="color:#6B7280;font-size:13px;">🗓️ Deadline: {helpers.format_date(e.get('registration_end_date'))}</div>
            <div style="color:#6B7280;font-size:13px;margin-top:4px;">👥 {reg_count} Schools Registered</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Details", key=f"ud_view_{e['id']}", use_container_width=True):
            st.session_state.selected_event_id = e["id"]
            st.session_state.page = "event_details"
            st.rerun()
    with col2:
        if already:
            st.button("Already Registered", key=f"ud_reg_{e['id']}", disabled=True, use_container_width=True)
        elif not helpers.is_registration_open(e):
            st.button("Registration Closed", key=f"ud_closed_{e['id']}", disabled=True, use_container_width=True)
        else:
            if st.button("Register Now", key=f"ud_reg_open_{e['id']}", use_container_width=True):
                st.session_state.selected_event_id = e["id"]
                st.session_state.edit_registration_id = None
                st.session_state.page = "register_form"
                st.rerun()
