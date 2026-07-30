import base64
import streamlit as st
import config


def get_image_base64(path) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def inject_css():
    css_path = config.ASSETS_DIR / "css" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def header():
    reva_logo_path = config.ASSETS_DIR / "logos" / "reva_logo_horizontal.png"
    naac_logo_path = config.ASSETS_DIR / "logos" / "naac_logo_custom.png"
    
    reva_b64 = get_image_base64(reva_logo_path)
    naac_b64 = get_image_base64(naac_logo_path)
    
    if reva_b64:
        reva_logo_html = f"""
        <div style="display:flex; align-items:center; gap:12px;">
            <img src="data:image/png;base64,{reva_b64}" style="height:48px; object-fit:contain;" />
            <div style="border-left: 2px solid #ddd; padding-left: 12px; height: 32px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-weight:800;font-size:13px;color:#222;letter-spacing:0.5px;">SPORTS DEPARTMENT</div>
                <div style="font-size:10px;color:#6B7280;">Official Portal</div>
            </div>
        </div>
        """
    else:
        reva_logo_html = """
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:52px;height:52px;border-radius:12px;background:#F37021;
                        display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:800;font-size:20px;">R</div>
            <div>
                <div style="font-weight:800;font-size:14px;color:#222;">REVA UNIVERSITY</div>
                <div style="font-size:11px;color:#6B7280;">Sports Department</div>
            </div>
        </div>
        """
        
    if naac_b64:
        naac_logo_html = f"""
        <div style="display:flex; align-items:center; gap:12px;">
            <img src="data:image/png;base64,{naac_b64}" style="height:48px; object-fit:contain;" />
        </div>
        """
    else:
        naac_logo_html = """
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="text-align:right;">
                <div style="font-weight:800;font-size:14px;color:#222;">NAAC A+</div>
                <div style="font-size:11px;color:#6B7280;">Accredited Institution</div>
            </div>
            <div style="width:52px;height:52px;border-radius:12px;background:#1D9A5B;
                        display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:800;font-size:14px;">A+</div>
        </div>
        """

    html = f"""
    <div class="reva-header">
        <div class="logo-box">
            {reva_logo_html}
        </div>
        <div class="center-title">
            <h1>REVA InterSchool Competition Portal</h1>
            <p>Official Sports Event Registration System</p>
        </div>
        <div class="logo-box">
            {naac_logo_html}
        </div>
    </div>
    """
    st.markdown(html.replace("\n", ""), unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="reva-hero">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="reva-section-title">{text}</div>', unsafe_allow_html=True)


def metric_card(label: str, value, orange: bool = False):
    value_class = "reva-metric-value orange" if orange else "reva-metric-value"
    st.markdown(
        f"""
        <div class="reva-card">
            <div class="reva-metric-label">{label}</div>
            <div class="{value_class}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str) -> str:
    return f'<span class="reva-badge badge-{kind}">{text}</span>'


def status_badge_html(status: str) -> str:
    mapping = {
        "Open": "open", "Closed": "closed", "Draft": "draft", "Archived": "archived",
        "Pending": "pending", "Approved": "approved", "Rejected": "rejected",
    }
    return badge(status, mapping.get(status, "draft"))


def footer():
    st.markdown(
        """
        <div class="reva-footer">
            <strong>REVA University — Sports Department</strong><br>
            Kattigenahalli, Yelahanka, Bengaluru - 560064 &nbsp;|&nbsp;
            sports@reva.edu.in &nbsp;|&nbsp; +91-80-4696-6966<br>
            © 2026 REVA University. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(message: str, icon: str = "🏆"):
    st.markdown(
        f"""
        <div class="reva-card" style="text-align:center;padding:48px 20px;">
            <div style="font-size:44px;">{icon}</div>
            <div style="color:#6B7280;font-weight:600;margin-top:8px;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
