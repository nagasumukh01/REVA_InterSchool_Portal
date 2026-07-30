import streamlit as st

from modules import events as events_mod, registrations as reg_mod
from utils import ui, helpers


def render():
    event = events_mod.get_event(st.session_state.get("selected_event_id"))
    if not event:
        st.error("Event not found.")
        if st.button("← Back"):
            st.session_state.page = "home"
            st.rerun()
        return

    reg_count = events_mod.registration_count(event["id"])
    is_open = helpers.is_registration_open(event)

    st.markdown(
        f"""
        <div class="reva-hero" style="padding:34px 30px;">
            <h2>{event.get('event_name','')}</h2>
            <p>{event.get('sport_category','')} &nbsp;•&nbsp; Venue: {event.get('venue','TBA')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card("Event Date", helpers.format_date(event.get("event_date")))
    with c2:
        ui.metric_card("Registration Deadline", helpers.format_date(event.get("registration_end_date")))
    with c3:
        ui.metric_card("Schools Registered", reg_count, orange=True)
    with c4:
        ui.metric_card("Max Teams", event.get("max_teams", "—"))

    col_main, col_side = st.columns([2, 1])
    with col_main:
        ui.section_title("Description")
        st.write(event.get("description", "No description provided."))

        ui.section_title("Rules")
        st.write(event.get("rules", "—"))

        ui.section_title("Instructions")
        st.write(event.get("instructions", "—"))

        ui.section_title("Required Documents")
        st.write(event.get("required_documents", "Department-authorized team list (PDF/DOCX/XLSX)"))

    with col_side:
        ui.section_title("Contact")
        st.markdown(
            f"""
            <div class="reva-card">
                <div><strong>{event.get('contact_person','Sports Office')}</strong></div>
                <div style="color:#6B7280;font-size:13px;">📞 {event.get('contact_number','-')}</div>
                <div style="margin-top:10px;">{ui.status_badge_html(event.get('registration_status','Open'))}</div>
                <div style="color:#6B7280;font-size:13px;margin-top:6px;">
                    Reporting Time: {event.get('reporting_time','TBA')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

        auth = st.session_state.get("auth")
        if auth and auth.get("role") == "school_head":
            already = reg_mod.already_registered(event["id"], auth.get("school"))
            if already:
                st.button("Already Registered", disabled=True, use_container_width=True)
            elif not is_open:
                st.button("Registration Closed", disabled=True, use_container_width=True)
            else:
                if st.button("Register Now", use_container_width=True, type="primary"):
                    st.session_state.edit_registration_id = None
                    st.session_state.page = "register_form"
                    st.rerun()
        elif not auth:
            st.info("Log in as a School Sports Vertical Head to register.")
            if st.button("Login", use_container_width=True):
                st.session_state.page = "login"
                st.session_state.login_role = "school_head"
                st.rerun()

    st.write("")
    back_target = "user_dashboard" if st.session_state.get("auth") else "home"
    if st.button("← Back"):
        st.session_state.page = back_target
        st.rerun()

    ui.footer()
