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
            cols = st.columns(7)
            with cols[0]:
                if st.button("Edit", key=f"edit_ev_{e['id']}", use_container_width=True):
                    st.session_state[f"editing_{e['id']}"] = True
            with cols[1]:
                if st.button("Results", key=f"res_ev_{e['id']}", use_container_width=True):
                    st.session_state[f"editing_results_{e['id']}"] = True
            with cols[2]:
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
            with cols[3]:
                if st.button("Archive", key=f"archive_ev_{e['id']}", use_container_width=True):
                    events_mod.set_status(e["id"], "Archived", auth["admin_id"])
                    st.toast("Event archived.", icon="🗄️")
                    st.rerun()
            with cols[4]:
                if st.button("Clone", key=f"clone_ev_{e['id']}", use_container_width=True):
                    events_mod.clone_event(e["id"], auth["admin_id"])
                    st.toast("Event cloned as Draft.", icon="📋")
                    st.rerun()
            with cols[5]:
                if st.button("View Registrations", key=f"viewregs_ev_{e['id']}", use_container_width=True):
                    st.session_state.admin_reg_event_filter = e["id"]
                    st.session_state.admin_nav = "Registrations"
                    st.rerun()
            with cols[6]:
                if st.button("Delete", key=f"delete_ev_{e['id']}", use_container_width=True):
                    events_mod.delete_event(e["id"], auth["admin_id"])
                    st.toast("Event deleted.", icon="🗑️")
                    st.rerun()

            if st.session_state.get(f"editing_{e['id']}"):
                with st.expander(f"Edit — {e.get('event_name')}", expanded=True):
                    _event_form(mode="edit", actor=auth["admin_id"], event=e)

            if st.session_state.get(f"editing_results_{e['id']}"):
                with st.expander(f"🏆 Update Results — {e.get('event_name')}", expanded=True):
                    _results_form(e, auth["admin_id"])


def _event_form(mode: str, actor: str, event: dict | None = None):
    e = event or {}
    prefix = f"{mode}_{e.get('id','new')}"
    schools_list = list(config.SCHOOLS.keys())
    assoc_schools_list = ["None"] + schools_list

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
        organizing_school = st.selectbox("Organizing School*", schools_list,
                                         index=schools_list.index(e.get("organizing_school")) if e.get("organizing_school") in schools_list else 0,
                                         key=f"{prefix}_org_school")
    with c2:
        reg_start = st.date_input("Registration Start Date*", value=helpers.parse_date(e.get("registration_start_date")) or date.today(), key=f"{prefix}_regstart")
        reg_end = st.date_input("Registration End Date*", value=helpers.parse_date(e.get("registration_end_date")) or date.today(), key=f"{prefix}_regend")
        event_date = st.date_input("Event Date*", value=helpers.parse_date(e.get("event_date")) or date.today(), key=f"{prefix}_eventdate")
        reporting_time = st.text_input("Reporting Time", value=e.get("reporting_time", "8:00 AM"), key=f"{prefix}_reporttime")
        registration_status = st.selectbox("Registration Status", config.EVENT_STATUSES,
                                            index=config.EVENT_STATUSES.index(e.get("registration_status", "Draft")),
                                            key=f"{prefix}_status")
        associated_school = st.selectbox("Associated School (Co-organizer)", assoc_schools_list,
                                         index=assoc_schools_list.index(e.get("associated_school")) if e.get("associated_school") in assoc_schools_list else 0,
                                         key=f"{prefix}_assoc_school")

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
            "organizing_school": organizing_school,
            "associated_school": associated_school if associated_school != "None" else "None"
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


def _results_form(e: dict, actor: str):
    schools_list = ["None"] + list(config.SCHOOLS.keys())
    res = e.get("results") or {}
    
    pos1_val = res.get("pos1") or "None"
    pos2_val = res.get("pos2") or "None"
    pos3_val = res.get("pos3") or "None"
    pos4_val = res.get("pos4") or "None"
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        pos1 = st.selectbox("1st Place (Winner - 20 pts)*", schools_list,
                            index=schools_list.index(pos1_val) if pos1_val in schools_list else 0,
                            key=f"res_{e['id']}_pos1")
    with c2:
        pos2 = st.selectbox("2nd Place (Runner - 14 pts)", schools_list,
                            index=schools_list.index(pos2_val) if pos2_val in schools_list else 0,
                            key=f"res_{e['id']}_pos2")
    with c3:
        pos3 = st.selectbox("3rd Place (10 pts)", schools_list,
                            index=schools_list.index(pos3_val) if pos3_val in schools_list else 0,
                            key=f"res_{e['id']}_pos3")
    with c4:
        pos4 = st.selectbox("4th Place (6 pts)", schools_list,
                            index=schools_list.index(pos4_val) if pos4_val in schools_list else 0,
                            key=f"res_{e['id']}_pos4")
        
    col_s, col_c = st.columns([1, 4])
    with col_s:
        if st.button("Save Results", key=f"res_submit_{e['id']}", type="primary", use_container_width=True):
            updated_results = {
                "pos1": pos1 if pos1 != "None" else None,
                "pos2": pos2 if pos2 != "None" else None,
                "pos3": pos3 if pos3 != "None" else None,
                "pos4": pos4 if pos4 != "None" else None,
            }
            events_mod.update_event(e["id"], {"results": updated_results}, actor)
            st.toast("Event results updated successfully!", icon="🏆")
            st.session_state[f"editing_results_{e['id']}"] = False
            st.rerun()
    with col_c:
        if st.button("Cancel", key=f"res_cancel_{e['id']}", use_container_width=True):
            st.session_state[f"editing_results_{e['id']}"] = False
            st.rerun()
