import streamlit as st

import config
from modules import events as events_mod, registrations as reg_mod
from utils import ui, helpers


def render():
    auth = st.session_state.get("auth")
    if not auth or auth.get("role") != "school_head":
        st.warning("Please log in as a School Sports Vertical Head to register a team.")
        st.session_state.page = "login"
        st.session_state.login_role = "school_head"
        st.rerun()
        return

    event = events_mod.get_event(st.session_state.get("selected_event_id"))
    if not event:
        st.error("Event not found.")
        return

    edit_id = st.session_state.get("edit_registration_id")
    existing = reg_mod.get_registration(edit_id) if edit_id else None

    ui.section_title(f"Register Your Team — {event.get('event_name','')}")
    if not helpers.is_registration_open(event):
        st.error("Registration for this event is closed.")
        if st.button("← Back to Event"):
            st.session_state.page = "event_details"
            st.rerun()
        return

    def val(field, default=""):
        return existing.get(field, default) if existing else default

    with st.form("registration_form", clear_on_submit=False):
        st.markdown("#### Section 1 — Sports Vertical Head")
        c1, c2 = st.columns(2)
        with c1:
            vh_name = st.text_input("Vertical Head Name*", value=val("vh_name", auth.get("name", "")))
            vh_college_id = st.text_input("College ID*", value=val("vh_college_id", auth.get("login_id", "")))
            vh_school = st.selectbox("School*", list(config.SCHOOLS.keys()),
                                      index=list(config.SCHOOLS.keys()).index(val("vh_school", auth.get("school")))
                                      if val("vh_school", auth.get("school")) in config.SCHOOLS else 0)
            vh_designation = st.text_input("Designation*", value=val("vh_designation", ""),
                                            placeholder="e.g. Assistant Sports Vertical Head")
        with c2:
            branches = config.SCHOOLS.get(vh_school, [])
            vh_department = st.selectbox("Department / Branch*", branches) if branches else st.text_input("Department*", value=val("vh_department", ""))
            vh_contact = st.text_input("Contact Number*", value=val("vh_contact", ""), max_chars=10)
            vh_email = st.text_input("Official Email*", value=val("vh_email", auth.get("login_id", "")))

        st.markdown("#### Section 2 — Captain Details")
        c3, c4 = st.columns(2)
        with c3:
            captain_name = st.text_input("Captain Name*", value=val("captain_name", ""))
            captain_srn = st.text_input("Captain SRN*", value=val("captain_srn", ""))
            captain_semester = st.selectbox("Captain Semester*", [str(i) for i in range(1, 9)],
                                             index=int(val("captain_semester", "1")) - 1 if str(val("captain_semester", "1")).isdigit() else 0)
            captain_branch = st.text_input("Captain Branch*", value=val("captain_branch", ""))
        with c4:
            captain_phone = st.text_input("Captain Phone*", value=val("captain_phone", ""), max_chars=10)
            captain_email = st.text_input("Captain Email*", value=val("captain_email", ""))
            captain_gender = st.selectbox("Captain Gender*", ["Male", "Female", "Other"],
                                           index=["Male", "Female", "Other"].index(val("captain_gender", "Male")))

        st.markdown("#### Section 3 — Vice-Captain Details")
        c5, c6 = st.columns(2)
        with c5:
            vice_captain_name = st.text_input("Vice-Captain Name*", value=val("vice_captain_name", ""))
            vice_captain_srn = st.text_input("Vice-Captain SRN*", value=val("vice_captain_srn", ""))
            vice_captain_semester = st.selectbox("Vice-Captain Semester*", [str(i) for i in range(1, 9)],
                                                  index=int(val("vice_captain_semester", "1")) - 1 if str(val("vice_captain_semester", "1")).isdigit() else 0)
            vice_captain_branch = st.text_input("Vice-Captain Branch*", value=val("vice_captain_branch", ""))
        with c6:
            vice_captain_phone = st.text_input("Vice-Captain Phone*", value=val("vice_captain_phone", ""), max_chars=10)
            vice_captain_email = st.text_input("Vice-Captain Email*", value=val("vice_captain_email", ""))
            vice_captain_gender = st.selectbox("Vice-Captain Gender*", ["Male", "Female", "Other"],
                                                index=["Male", "Female", "Other"].index(val("vice_captain_gender", "Male")))

        st.markdown("#### Section 4 — Team List Upload")
        uploaded_file = st.file_uploader(
            "Upload department-authorized team list (PDF, DOCX, or XLSX, max "
            f"{config.MAX_UPLOAD_SIZE_MB} MB)*",
            type=["pdf", "docx", "xlsx"],
        )
        if existing and existing.get("file_path") and not uploaded_file:
            st.caption(f"Current file on record: {existing['file_path']}")

        st.markdown("#### Section 5 — Declaration")
        declaration_accepted = st.checkbox(
            "I certify that the above information is true and has been approved by my department.*",
            value=bool(val("declaration_accepted", False)),
        )
        digital_signature = st.text_input("Digital Signature (Type your full name)*", value=val("digital_signature", ""))

        submitted = st.form_submit_button("Submit Registration", use_container_width=True, type="primary")

    if submitted:
        form = {
            "vh_name": vh_name, "vh_college_id": vh_college_id, "vh_school": vh_school,
            "vh_department": vh_department, "vh_contact": vh_contact, "vh_email": vh_email,
            "vh_designation": vh_designation,
            "captain_name": captain_name, "captain_srn": captain_srn, "captain_semester": captain_semester,
            "captain_branch": captain_branch, "captain_phone": captain_phone, "captain_email": captain_email,
            "captain_gender": captain_gender,
            "vice_captain_name": vice_captain_name, "vice_captain_srn": vice_captain_srn,
            "vice_captain_semester": vice_captain_semester, "vice_captain_branch": vice_captain_branch,
            "vice_captain_phone": vice_captain_phone, "vice_captain_email": vice_captain_email,
            "vice_captain_gender": vice_captain_gender,
            "declaration_accepted": declaration_accepted, "digital_signature": digital_signature,
        }

        errors = reg_mod.validate_registration(
            form, event, exclude_registration_id=existing["id"] if existing else None
        )

        file_path = existing.get("file_path") if existing else None
        if uploaded_file is not None:
            from utils import validators
            ok, msg = validators.is_valid_file(uploaded_file.name, uploaded_file.size)
            if not ok:
                errors.append(msg)
            else:
                file_path = helpers.save_uploaded_file(uploaded_file, subfolder=event["id"])
        elif not file_path:
            errors.append("Please upload the department-authorized team list.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            if existing:
                reg_mod.update_registration(existing["id"], {**form, "file_path": file_path}, auth["login_id"])
                st.toast("Registration updated successfully!", icon="✅")
            else:
                reg_mod.create_registration(form, event["id"], file_path, auth["login_id"])
                st.toast("Registration submitted successfully!", icon="✅")
            st.session_state.page = "user_dashboard"
            st.session_state.edit_registration_id = None
            st.rerun()

    if st.button("← Cancel"):
        st.session_state.page = "event_details"
        st.rerun()
