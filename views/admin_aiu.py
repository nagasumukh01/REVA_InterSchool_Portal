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

    # Form to add record
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
        # Render details in a clean HTML rows-and-columns table
        table_rows = []
        for r in filtered_records:
            student_name = r.get("student_name", "")
            srn = r.get("srn", "")
            school_name = r.get("school_name", "")
            game = r.get("game", "")
            event = r.get("event", "")
            remarks = r.get("remarks", "")
            rec_date = helpers.format_date(r.get("date"))
            pts = r.get("points", 0)

            table_rows.append(f"""
            <tr style="border-bottom: 1px solid #E5E7EB;">
                <td style="padding: 12px 14px; font-weight: 600; color: #1F2937;">{student_name}</td>
                <td style="padding: 12px 14px; color: #4B5563;">{srn}</td>
                <td style="padding: 12px 14px; color: #4B5563;">{school_name}</td>
                <td style="padding: 12px 14px; color: #4B5563;">{game}</td>
                <td style="padding: 12px 14px; color: #4B5563;">{event}</td>
                <td style="padding: 12px 14px; color: #6B7280; font-size: 13px;">{remarks}</td>
                <td style="padding: 12px 14px; color: #4B5563;">{rec_date}</td>
                <td style="padding: 12px 14px; font-weight: 800; color: #F37021; text-align: center;">{pts}</td>
            </tr>
            """)

        table_body = "".join(table_rows)

        html_table = f"""
        <style>
            .aiu-table-container {{
                width: 100%;
                overflow-x: auto;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                margin-bottom: 25px;
                border: 1px solid #E5E7EB;
            }}
            .aiu-table {{
                width: 100%;
                border-collapse: collapse;
                background-color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
            }}
            .aiu-table th {{
                background: linear-gradient(135deg, #F37021, #FF8D48);
                color: white;
                font-weight: 700;
                padding: 14px;
                text-align: left;
                letter-spacing: 0.5px;
            }}
            .aiu-table tr:hover {{
                background-color: #F8FAFC !important;
            }}
        </style>
        <div class="aiu-table-container">
            <table class="aiu-table">
                <thead>
                    <tr>
                        <th>Student Name</th>
                        <th>SRN</th>
                        <th>School Name</th>
                        <th>Game</th>
                        <th>Event</th>
                        <th>Remarks</th>
                        <th>Date</th>
                        <th style="text-align: center; width: 100px;">Points</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
        """
        st.markdown(html_table.replace("\n", ""), unsafe_allow_html=True)

        st.write("")

        # Expander to edit/delete
        with st.expander("⚙ Edit / Delete Existing Records", expanded=False):
            record_options = {
                f"{r['student_name']} — {r['event']} ({r['points']} pts)": r
                for r in filtered_records
            }
            selected_record_label = st.selectbox("Select record to edit or delete", ["Select record..."] + list(record_options.keys()))
            
            if selected_record_label != "Select record...":
                r_to_edit = record_options[selected_record_label]
                
                with st.form(f"edit_aiu_form_{r_to_edit['id']}"):
                    estudent_name = st.text_input("Student Name*", value=r_to_edit.get("student_name"))
                    esrn = st.text_input("SRN*", value=r_to_edit.get("srn"))
                    eschool_name = st.selectbox(
                        "School Name*",
                        list(config.SCHOOLS.keys()),
                        index=list(config.SCHOOLS.keys()).index(r_to_edit.get("school_name")) if r_to_edit.get("school_name") in config.SCHOOLS else 0
                    )
                    egame = st.text_input("Game*", value=r_to_edit.get("game"))
                    eevent = st.text_input("Event*", value=r_to_edit.get("event"))
                    eremarks = st.text_area("Remarks", value=r_to_edit.get("remarks", ""))
                    edate = st.date_input("Date", value=helpers.parse_date(r_to_edit.get("date")) or date.today())
                    epoints = st.number_input("Points*", min_value=0, value=int(r_to_edit.get("points", 5)), step=1)
                    
                    c_save, c_del = st.columns([1, 4])
                    with c_save:
                        save = st.form_submit_button("Save Changes", type="primary")
                        if save:
                            if not estudent_name or not esrn or not egame or not eevent:
                                st.error("Starred fields are required.")
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
                                storage.update_row("aiu_records", r_to_edit["id"], updates)
                                st.toast("Record updated successfully!", icon="✅")
                                st.rerun()
                    with c_del:
                        delete = st.form_submit_button("Delete Record", type="secondary")
                        if delete:
                            storage.delete_row("aiu_records", r_to_edit["id"])
                            helpers.log_action(auth["admin_id"], "DELETE_AIU_RECORD", f"Deleted record {r_to_edit['id']}")
                            st.toast("Record deleted successfully.", icon="🗑️")
                            st.rerun()
