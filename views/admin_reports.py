import streamlit as st

from modules import events as events_mod, reports, notifications
from utils import ui


def render():
    auth = st.session_state.auth
    ui.section_title("Reports")

    all_events = events_mod.list_events()
    event_options = {"All Events": None}
    event_options.update({e["event_name"]: e["id"] for e in all_events})
    event_label = st.selectbox("Select scope", list(event_options.keys()))
    event_id = event_options[event_label]

    df = reports.registrations_dataframe(event_id=event_id)
    st.dataframe(df, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ Excel", reports.to_excel_bytes(df), file_name=f"report_{event_label}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)
    with c2:
        st.download_button("⬇️ CSV", reports.to_csv_bytes(df), file_name=f"report_{event_label}.csv",
                            mime="text/csv", use_container_width=True)
    with c3:
        st.download_button("⬇️ PDF", reports.to_pdf_bytes(df, title=f"Report — {event_label}"),
                            file_name=f"report_{event_label}.pdf", mime="application/pdf", use_container_width=True)

    ui.section_title("Registration Summary")
    st.markdown("**Event-wise**")
    st.dataframe(reports.event_wise_counts(), use_container_width=True, hide_index=True)
    st.markdown("**School-wise**")
    st.dataframe(reports.school_wise_counts(), use_container_width=True, hide_index=True)
    st.markdown("**Branch-wise**")
    st.dataframe(reports.branch_wise_counts(), use_container_width=True, hide_index=True)


