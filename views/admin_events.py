import streamlit as st
from datetime import date

import config
from modules import events as events_mod
from utils import ui, helpers


def render():
    ui.section_title("Event Management")
    auth = st.session_state.auth

    with st.expander("➕ Create New Event", expanded=False):
        _event_form(mode="create", actor=auth["admin_id"])

    st.write("")
    all_events = events_mod.list_events()
    if not all_events:
        ui.empty_state("No events created yet. Use the form above to add one.")
        return

    status_filter = st.selectbox("Filter by status", ["All"] + config.EVENT_STATUSES)
    events_to_show = all_events if status_filter == "All" else [e for e in all_events if e.get("registration_status") == status_filter]

    for e in events_to_show:
        with st.container():
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong style="font-size:16px;">{e.get('event_name','')}</strong>
                        {ui.status_badge_html(e.get('registration_status','Draft'))}
                    </div>
                    <div style="color:#6B7280;font-size:13px;margin-top:6px;">
                        🎽 {e.get('sport_category','')} &nbsp;|&nbsp; 🏟️ {e.get('venue','TBA')} &nbsp;|&nbsp;
                        🗓️ Event: {helpers.format_date(e.get('event_date'))} &nbsp;|&nbsp;
                        Deadline: {helpers.format_date(e.get('registration_end_date'))}
                    </div>
                    <div style="color:#6B7280;font-size:13px;">
                        👥 {events_mod.registration_count(e['id'])} registrations &nbsp;|&nbsp; Max teams: {e.get('max_teams','-')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cols = st.columns(6)
            with cols[0]:
                if st.button("Edit", key=f"edit_ev_{e['id']}", use_container_width=True):
                    st.session_state[f"editing_{e['id']}"] = True
            with cols[1]:
                if e.get("registration_status") != "Open":
                    if st.button("Publish/Open", key=f"open_ev_{e['id']}", use_container_width=True):
                        events_mod.set_status(e["id"], "Open", auth["admin_id"])
                        st.toast("Event opened for registration.", icon="✅")
                        st.rerun()
                else:
                    if st.button("Close", key=f"close_ev_{e['id']}", use_container_width=True):
                        events_mod.set_status(e["id"], "Closed", auth["admin_id"])
                        st.toast("Registration closed.", icon="🔒")
                        st.rerun()
            with cols[2]:
                if st.button("Archive", key=f"archive_ev_{e['id']}", use_container_width=True):
                    events_mod.set_status(e["id"], "Archived", auth["admin_id"])
                    st.toast("Event archived.", icon="🗄️")
                    st.rerun()
            with cols[3]:
                if st.button("Clone", key=f"clone_ev_{e['id']}", use_container_width=True):
                    events_mod.clone_event(e["id"], auth["admin_id"])
                    st.toast("Event cloned as Draft.", icon="📋")
                    st.rerun()
            with cols[4]:
                if st.button("View Registrations", key=f"viewregs_ev_{e['id']}", use_container_width=True):
                    st.session_state.admin_reg_event_filter = e["id"]
                    st.session_state.admin_nav = "Registrations"
                    st.rerun()
            with cols[5]:
                if st.button("Delete", key=f"delete_ev_{e['id']}", use_container_width=True):
                    events_mod.delete_event(e["id"], auth["admin_id"])
                    st.toast("Event deleted.", icon="🗑️")
                    st.rerun()

            if st.session_state.get(f"editing_{e['id']}"):
                with st.expander(f"Edit — {e.get('event_name')}", expanded=True):
                    _event_form(mode="edit", actor=auth["admin_id"], event=e)


def _event_form(mode: str, actor: str, event: dict | None = None):
    e = event or {}
    prefix = f"{mode}_{e.get('id','new')}"

    c1, c2 = st.columns(2)
    with c1:
        event_name = st.text_input("Event Name*", value=e.get("event_name", ""), key=f"{prefix}_name")
        sport_category = st.selectbox("Sport Category*", config.SPORT_CATEGORIES,
                                       index=config.SPORT_CATEGORIES.index(e["sport_category"]) if e.get("sport_category") in config.SPORT_CATEGORIES else 0,
                                       key=f"{prefix}_sport")
        venue = st.text_input("Venue*", value=e.get("venue", ""), key=f"{prefix}_venue")
        max_teams = st.number_input("Maximum Teams*", min_value=1, value=int(e.get("max_teams", 16)), key=f"{prefix}_maxteams")
        contact_person = st.text_input("Contact Person", value=e.get("contact_person", ""), key=f"{prefix}_contact_person")
        contact_number = st.text_input("Contact Number", value=e.get("contact_number", ""), key=f"{prefix}_contact_number")
    with c2:
        reg_start = st.date_input("Registration Start Date*", value=helpers.parse_date(e.get("registration_start_date")) or date.today(), key=f"{prefix}_regstart")
        reg_end = st.date_input("Registration End Date*", value=helpers.parse_date(e.get("registration_end_date")) or date.today(), key=f"{prefix}_regend")
        event_date = st.date_input("Event Date*", value=helpers.parse_date(e.get("event_date")) or date.today(), key=f"{prefix}_eventdate")
        reporting_time = st.text_input("Reporting Time", value=e.get("reporting_time", "8:00 AM"), key=f"{prefix}_reporttime")
        registration_status = st.selectbox("Registration Status", config.EVENT_STATUSES,
                                            index=config.EVENT_STATUSES.index(e.get("registration_status", "Draft")),
                                            key=f"{prefix}_status")

    description = st.text_area("Description", value=e.get("description", ""), key=f"{prefix}_desc")
    instructions = st.text_area("Instructions", value=e.get("instructions", ""), key=f"{prefix}_instr")
    rules = st.text_area("Rules", value=e.get("rules", ""), key=f"{prefix}_rules")
    required_documents = st.text_input("Required Documents", value=e.get("required_documents", "Department-authorized team list"), key=f"{prefix}_reqdocs")

    banner_image = st.file_uploader("Banner Image (optional)", type=["png", "jpg", "jpeg"], key=f"{prefix}_banner")
    event_image = st.file_uploader("Event Image (optional)", type=["png", "jpg", "jpeg"], key=f"{prefix}_image")

    label = "Save Changes" if mode == "edit" else "Create Event"
    if st.button(label, key=f"{prefix}_submit", type="primary"):
        if not event_name or not venue:
            st.error("Event Name and Venue are required.")
            return
        data = {
            "event_name": event_name, "sport_category": sport_category, "venue": venue,
            "max_teams": int(max_teams), "contact_person": contact_person, "contact_number": contact_number,
            "registration_start_date": str(reg_start), "registration_end_date": str(reg_end),
            "event_date": str(event_date), "reporting_time": reporting_time,
            "registration_status": registration_status, "description": description,
            "instructions": instructions, "rules": rules, "required_documents": required_documents,
        }
        if banner_image is not None:
            data["banner_image_path"] = helpers.save_uploaded_file(banner_image, subfolder="banners")
        if event_image is not None:
            data["event_image_path"] = helpers.save_uploaded_file(event_image, subfolder="events")

        if mode == "edit":
            events_mod.update_event(e["id"], data, actor)
            st.toast("Event updated.", icon="✅")
            st.session_state[f"editing_{e['id']}"] = False
        else:
            events_mod.create_event(data, actor)
            st.toast("Event created.", icon="✅")
        st.rerun()
