import streamlit as st
from datetime import date

import config
from utils import storage, ui, helpers


def render():
    ui.section_title("AIU & Other Tournaments Management")
    auth = st.session_state.auth

    if "aiu_selected_option" not in st.session_state:
        st.session_state.aiu_selected_option = "AIU Achievements"

    # Option buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏆 AIU Achievements", type="primary" if st.session_state.aiu_selected_option == "AIU Achievements" else "secondary", use_container_width=True):
            st.session_state.aiu_selected_option = "AIU Achievements"
            st.rerun()
    with c2:
        if st.button("🏃 AIU Participation", type="primary" if st.session_state.aiu_selected_option == "AIU Participation" else "secondary", use_container_width=True):
            st.session_state.aiu_selected_option = "AIU Participation"
            st.rerun()
    with c3:
        if st.button("🏅 Inter College Achievements", type="primary" if st.session_state.aiu_selected_option == "Inter College Achievements" else "secondary", use_container_width=True):
            st.session_state.aiu_selected_option = "Inter College Achievements"
            st.rerun()

    st.write("")
    st.markdown(f"### 📋 Manage: **{st.session_state.aiu_selected_option}**")

    # Expander to add record
    with st.expander("➕ Add New Record", expanded=False):
        with st.form("add_aiu_record_form", clear_on_submit=True):
            student_name = st.text_input("Student Name*")
            srn = st.text_input("SRN*")
            school_name = st.selectbox("School Name*", list(config.SCHOOLS.keys()))
            game = st.text_input("Game*")
            event = st.text_input("Event*")
            remarks = st.text_area("Remarks")
            record_date = st.date_input("Date", value=date.today())
            points = st.number_input("Points*", min_value=0, value=5, step=1)
            
            submit = st.form_submit_button("Add Record", type="primary")
            if submit:
                if not student_name or not srn or not game or not event:
                    st.error("Student Name, SRN, Game, and Event are required.")
                else:
                    new_record = {
                        "type": st.session_state.aiu_selected_option,
                        "student_name": student_name,
                        "srn": srn,
                        "school_name": school_name,
                        "game": game,
                        "event": event,
                        "remarks": remarks,
                        "date": str(record_date),
                        "points": int(points),
                        "created_at": helpers.now_iso(),
                        "created_by": auth["admin_id"]
                    }
                    storage.append_row("aiu_records", new_record)
                    helpers.log_action(auth["admin_id"], "ADD_AIU_RECORD", f"Added {st.session_state.aiu_selected_option} record for {student_name}")
                    st.toast("Record added successfully!", icon="✅")
                    st.rerun()

    st.write("")

    # Read and filter records
    try:
        all_records = storage.read_table("aiu_records")
    except Exception:
        all_records = []

    filtered_records = [r for r in all_records if r.get("type") == st.session_state.aiu_selected_option]

    if not filtered_records:
        ui.empty_state("No records added yet for this section.", icon="📋")
    else:
        for r in filtered_records:
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding-bottom:8px; margin-bottom:8px;">
                        <strong style="font-size:16px; color:{config.COLORS['primary']};">{r.get('student_name','')} ({r.get('srn','')})</strong>
                        <span style="font-weight:800; font-size:14px; background:#FFEAD2; color:#B35400; padding:2px 8px; border-radius:12px;">★ {r.get('points',0)} pts</span>
                    </div>
                    <div style="font-size:13px; color:#6B7280;">
                        🏫 <strong>School:</strong> {r.get('school_name','')} &nbsp;|&nbsp; ⚽ <strong>Game:</strong> {r.get('game','')} &nbsp;|&nbsp; 🏆 <strong>Event:</strong> {r.get('event','')}<br>
                        🗓️ <strong>Date:</strong> {helpers.format_date(r.get('date'))}
                    </div>
                    {f'<div style="font-size:13px; color:#4B5563; margin-top:6px; background:#f9f9f9; padding:6px; border-radius:6px;"><strong>Remarks:</strong> {r["remarks"]}</div>' if r.get('remarks') else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Edit and Delete buttons
            cols = st.columns(6)
            with cols[0]:
                if st.button("Edit", key=f"edit_aiu_btn_{r['id']}", use_container_width=True):
                    st.session_state[f"editing_aiu_{r['id']}"] = True
            with cols[1]:
                if st.button("Delete", key=f"del_aiu_btn_{r['id']}", use_container_width=True):
                    storage.delete_row("aiu_records", r["id"])
                    helpers.log_action(auth["admin_id"], "DELETE_AIU_RECORD", f"Deleted AIU record {r['id']}")
                    st.toast("Record deleted successfully.", icon="🗑️")
                    st.rerun()

            # Editing form
            if st.session_state.get(f"editing_aiu_{r['id']}"):
                with st.expander(f"Edit Record — {r.get('student_name')}", expanded=True):
                    with st.form(f"edit_aiu_form_{r['id']}"):
                        estudent_name = st.text_input("Student Name*", value=r.get("student_name"))
                        esrn = st.text_input("SRN*", value=r.get("srn"))
                        eschool_name = st.selectbox(
                            "School Name*",
                            list(config.SCHOOLS.keys()),
                            index=list(config.SCHOOLS.keys()).index(r.get("school_name")) if r.get("school_name") in config.SCHOOLS else 0
                        )
                        egame = st.text_input("Game*", value=r.get("game"))
                        eevent = st.text_input("Event*", value=r.get("event"))
                        eremarks = st.text_area("Remarks", value=r.get("remarks", ""))
                        edate = st.date_input("Date", value=helpers.parse_date(r.get("date")) or date.today())
                        epoints = st.number_input("Points*", min_value=0, value=int(r.get("points", 5)), step=1)
                        
                        col_save, col_cancel = st.columns([1, 4])
                        with col_save:
                            save = st.form_submit_button("Save", type="primary")
                            if save:
                                if not estudent_name or not esrn or not egame or not eevent:
                                    st.error("All starred fields are required.")
                                else:
                                    updates = {
                                        "student_name": estudent_name,
                                        "srn": esrn,
                                        "school_name": eschool_name,
                                        "game": egame,
                                        "event": eevent,
                                        "remarks": eremarks,
                                        "date": str(edate),
                                        "points": int(epoints),
                                        "updated_at": helpers.now_iso()
                                    }
                                    storage.update_row("aiu_records", r["id"], updates)
                                    st.toast("Record updated successfully!", icon="✅")
                                    st.session_state[f"editing_aiu_{r['id']}"] = False
                                    st.rerun()
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_aiu_{r['id']}"] = False
                                st.rerun()
