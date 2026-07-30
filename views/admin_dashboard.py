import streamlit as st
import plotly.express as px

import config
from modules import events as events_mod, reports, notifications
from utils import storage, ui, helpers


def render():
    auth = st.session_state.auth
    st.markdown(f"### 🛡️ Admin Dashboard")
    st.caption(f"Logged in as {auth['name']} ({auth.get('role','Sports Director')})")

    all_events = events_mod.list_events()
    all_regs = storage.read_table("registrations")
    open_events = [e for e in all_events if e.get("registration_status") == "Open"]
    closed_events = [e for e in all_events if e.get("registration_status") == "Closed"]
    schools_registered = {r.get("school") for r in all_regs}
    pending = [r for r in all_regs if r.get("status") == "Pending"]
    approved = [r for r in all_regs if r.get("status") == "Approved"]

    r1 = st.columns(4)
    with r1[0]:
        ui.metric_card("Total Events", len(all_events), orange=True)
    with r1[1]:
        ui.metric_card("Open Events", len(open_events))
    with r1[2]:
        ui.metric_card("Closed Events", len(closed_events))
    with r1[3]:
        ui.metric_card("Schools Registered", len(schools_registered))

    r2 = st.columns(4)
    with r2[0]:
        ui.metric_card("Total Registrations", len(all_regs), orange=True)
    with r2[1]:
        ui.metric_card("Pending Registrations", len(pending))
    with r2[2]:
        ui.metric_card("Approved Registrations", len(approved))
    with r2[3]:
        upcoming = [e for e in all_events if (helpers.days_until(e.get("event_date")) or -1) >= 0]
        ui.metric_card("Upcoming Events", len(upcoming))

    ui.section_title("Analytics")
    tab1, tab2 = st.tabs(["Registration Trend", "Distribution"])

    with tab1:
        df = reports.registration_trend()
        if df.empty:
            ui.empty_state("No registration data yet to chart.")
        else:
            fig = px.line(df, x="Date", y="Registrations", markers=True,
                           color_discrete_sequence=[config.COLORS["primary"]])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Event-wise Registrations**")
            df_e = reports.event_wise_counts()
            if df_e.empty:
                ui.empty_state("No events yet.")
            else:
                fig = px.bar(df_e, x="Event", y="Registrations", color_discrete_sequence=[config.COLORS["primary"]])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("**School-wise Participation**")
            df_s = reports.school_wise_counts()
            if df_s.empty:
                ui.empty_state("No registrations yet.")
            else:
                fig = px.pie(df_s, names="School", values="Registrations", hole=0.45,
                              color_discrete_sequence=px.colors.sequential.Oranges_r)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Branch-wise Participation**")
        df_b = reports.branch_wise_counts()
        if df_b.empty:
            ui.empty_state("No registrations yet.")
        else:
            fig = px.bar(df_b, x="Branch", y="Registrations", color_discrete_sequence=[config.COLORS["primary_dark"]])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

    ui.section_title("Recent Registrations")
    recent = sorted(all_regs, key=lambda r: r.get("registered_at", ""), reverse=True)[:5]
    if not recent:
        ui.empty_state("No registrations yet.")
    else:
        for r in recent:
            ev = events_mod.get_event(r["event_id"])
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:8px;padding:14px 18px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span><strong>{r.get('school','')}</strong> registered for
                        <strong>{ev.get('event_name','(deleted)') if ev else '(deleted)'}</strong></span>
                        {ui.status_badge_html(r.get('status','Pending'))}
                    </div>
                    <div style="color:#6B7280;font-size:12.5px;">{helpers.format_date(r.get('registered_at'))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    ui.section_title("Admin Announcements")
    col_post, col_manage = st.columns(2)
    
    with col_post:
        with st.expander("📢 Post New Announcement", expanded=False):
            title = st.text_input("Title", key="new_ann_title")
            message = st.text_area("Message", key="new_ann_message")
            if st.button("Publish Announcement", key="publish_ann_btn"):
                if title and message:
                    notifications.create_announcement(title, message, auth["admin_id"])
                    st.toast("Announcement published.", icon="📢")
                    st.rerun()
                else:
                    st.error("Title and message are required.")

    with col_manage:
        announcements = notifications.list_announcements(limit=20)
        with st.expander("✏️ Edit / Delete Announcement", expanded=False):
            if not announcements:
                st.info("No announcements to manage.")
            else:
                ann_options = {f"{a['title']} ({a.get('created_at', '')[:16].replace('T', ' ')})": a for a in announcements}
                selected_label = st.selectbox("Select announcement", ["-- Select --"] + list(ann_options.keys()), key="select_ann")
                
                if selected_label != "-- Select --":
                    selected_ann = ann_options[selected_label]
                    edit_title = st.text_input("Edit Title", value=selected_ann['title'], key="edit_title_input")
                    edit_message = st.text_area("Edit Message", value=selected_ann['message'], key="edit_msg_input")
                    
                    c_up, c_del = st.columns(2)
                    with c_up:
                        if st.button("Update Announcement", key="update_ann_action_btn", use_container_width=True):
                            if edit_title and edit_message:
                                notifications.update_announcement(selected_ann['id'], edit_title, edit_message)
                                st.toast("Announcement updated.", icon="✅")
                                st.rerun()
                            else:
                                st.error("Title and message are required.")
                    with c_del:
                        if st.button("Delete Announcement", key="delete_ann_action_btn", type="secondary", use_container_width=True):
                            notifications.delete_announcement(selected_ann['id'])
                            st.toast("Announcement deleted.", icon="🗑️")
                            st.rerun()

    st.markdown("**Currently Published Announcements**")
    announcements_list = notifications.list_announcements(limit=5)
    if not announcements_list:
        ui.empty_state("No announcements posted yet.", icon="📢")
    else:
        for a in announcements_list:
            st.markdown(
                f"""
                <div class="reva-card" style="margin-bottom:8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{a['title']}</strong>
                        <span style="font-size: 0.85em; color: gray;">{a.get('created_at', '')[:16].replace('T', ' ')}</span>
                    </div>
                    <div style="margin-top:6px;">{a['message']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    if st.button("Logout"):
        st.session_state.auth = None
        st.session_state.page = "home"
        st.rerun()
