import streamlit as st

from modules import auth
from utils import ui


def render():
    role = st.session_state.get("login_role", "school_head")

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="reva-card">', unsafe_allow_html=True)
        tabs = st.tabs(["🏫 School Sports Head", "🛡️ Admin"])

        with tabs[0]:
            st.markdown("##### Login with your College Email or College ID")
            login_id = st.text_input("College Email / College ID", key="sh_login_id",
                                      placeholder="sportshead.soe@reva.edu.in")
            password = st.text_input("Password", type="password", key="sh_password")
            if st.button("Login", key="sh_login_btn", use_container_width=True):
                user = auth.login_school_head(login_id, password)
                if user:
                    st.session_state.auth = {"role": "school_head", **user}
                    st.session_state.page = "user_dashboard"
                    st.toast(f"Welcome back, {user['name']}!", icon="✅")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please check your College Email/ID and password.")
            st.caption("Demo account: sportshead.cse@reva.edu.in / Demo@1234")

            with st.expander("New Sports Vertical Head? Create an account"):
                import config
                new_id = st.text_input("College Email / College ID", key="new_login_id")
                new_name = st.text_input("Full Name", key="new_name")
                new_school = st.selectbox("School", list(config.SCHOOLS.keys()), key="new_school")
                new_password = st.text_input("Set Password", type="password", key="new_password")
                if st.button("Create Account", key="create_account_btn"):
                    ok, msg = auth.register_school_head(new_id, new_name, new_school, new_password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        with tabs[1]:
            st.markdown("##### Admin / Sports Director Login")
            admin_email = st.text_input("Admin Email", key="admin_email")
            admin_password = st.text_input("Password", type="password", key="admin_password")
            if st.button("Login as Admin", key="admin_login_btn", use_container_width=True):
                admin = auth.login_admin(admin_email, admin_password)
                if admin:
                    st.session_state.auth = {"role": "admin", **admin}
                    st.session_state.page = "admin_dashboard"
                    st.toast(f"Welcome, {admin['name']}!", icon="✅")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials.")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
