import streamlit as st

import config
from modules import events as events_mod, registrations as reg_mod, reports
from utils import ui, helpers


def render():
    ui.section_title("Registrations")
    auth = st.session_state.auth

    all_events = events_mod.list_events()
    event_options = {"All Events": None}
    event_options.update({e["event_name"]: e["id"] for e in all_events})

    default_event_id = st.session_state.pop("admin_reg_event_filter", None)
    default_label = next((k for k, v in event_options.items() if v == default_event_id), "All Events")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        event_label = st.selectbox("Event", list(event_options.keys()), index=list(event_options.keys()).index(default_label))
    with c2:
        school_filter = st.selectbox("School", ["All"] + list(config.SCHOOLS.keys()))
    with c3:
        status_filter = st.selectbox("Status", ["All"] + config.REGISTRATION_STATUSES)
    with c4:
        search_text = st.text_input("Search (captain, vice-captain, vertical head)")

    filters = {}
    event_id = event_options[event_label]
    if event_id:
        filters["event_id"] = event_id
    if school_filter != "All":
        filters["school"] = school_filter
    if status_filter != "All":
        filters["status"] = status_filter

    regs = reg_mod.list_registrations(**filters)
    if search_text:
        s = search_text.lower()
        regs = [r for r in regs if s in r.get("captain_name", "").lower()
                or s in r.get("vice_captain_name", "").lower()
                or s in r.get("vh_name", "").lower()]

    st.caption(f"{len(regs)} registration(s) found")

    if not regs:
        ui.empty_state("No registrations match these filters.")
    else:
        for r in regs:
            ev = events_mod.get_event(r["event_id"])
            with st.container():
                st.markdown(
                    f"""
                    <div class="reva-card" style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;">
                            <strong>{ev.get('event_name','(deleted)') if ev else '(deleted)'}</strong>
                            {ui.status_badge_html(r.get('status','Pending'))}
                        </div>
                        <div style="color:#6B7280;font-size:13px;margin-top:6px;">
                            🏫 {r.get('school','')} &nbsp;|&nbsp; {r.get('branch','')}
                        </div>
                        <div style="color:#6B7280;font-size:13px;">
                            Vertical Head: {r.get('vh_name','')} ({r.get('vh_email','')})
                        </div>
                        <div style="color:#6B7280;font-size:13px;">
                            Captain: {r.get('captain_name','')} ({r.get('captain_srn','')}) &nbsp;|&nbsp;
                            Vice-Captain: {r.get('vice_captain_name','')} ({r.get('vice_captain_srn','')})
                        </div>
                        <div style="color:#6B7280;font-size:12.5px;margin-top:4px;">
                            Registered on {helpers.format_date(r.get('registered_at'))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                cols = st.columns(4)
                with cols[0]:
                    if r.get("status") != "Approved":
                        if st.button("Approve", key=f"appr_{r['id']}", use_container_width=True):
                            reg_mod.set_status(r["id"], "Approved", auth["admin_id"])
                            st.toast("Registration approved.", icon="✅")
                            st.rerun()
                with cols[1]:
                    if r.get("status") != "Rejected":
                        if st.button("Reject", key=f"rej_{r['id']}", use_container_width=True):
                            reg_mod.set_status(r["id"], "Rejected", auth["admin_id"])
                            st.toast("Registration rejected.", icon="🚫")
                            st.rerun()
                with cols[2]:
                    file_path = r.get("file_path")
                    if file_path:
                        full_path = config.BASE_DIR / file_path
                        if full_path.exists():
                            with open(full_path, "rb") as f:
                                st.download_button("Download File", f.read(), file_name=full_path.name,
                                                    key=f"dl_{r['id']}", use_container_width=True)
                with cols[3]:
                    with st.popover("View Full Details"):
                        st.json(r)

    ui.section_title("Export")
    df = reports.registrations_dataframe(event_id=event_id)
    ce1, ce2, ce3 = st.columns(3)
    with ce1:
        st.download_button("⬇️ Export Excel", reports.to_excel_bytes(df), file_name="registrations.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)
    with ce2:
        st.download_button("⬇️ Export CSV", reports.to_csv_bytes(df), file_name="registrations.csv",
                            mime="text/csv", use_container_width=True)
    with ce3:
        st.download_button("⬇️ Export PDF", reports.to_pdf_bytes(df, title=event_label), file_name="registrations.pdf",
                            mime="application/pdf", use_container_width=True)
