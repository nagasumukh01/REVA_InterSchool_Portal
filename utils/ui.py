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
    dept_logo_path = config.ASSETS_DIR / "logos" / "sports_department_logo.jpg"
    
    reva_b64 = get_image_base64(reva_logo_path)
    naac_b64 = get_image_base64(naac_logo_path)
    dept_b64 = get_image_base64(dept_logo_path)
    
    # Left Side: Department Circular Logo (clips background with border-radius)
    if dept_b64:
        left_html = f'<img src="data:image/jpeg;base64,{dept_b64}" style="height:56px; width:56px; border-radius:50%; object-fit:cover;" />'
    else:
        left_html = """
        <div style="display:flex; flex-direction:column; justify-content:center;">
            <div style="font-weight:800;font-size:14px;color:#222;letter-spacing:0.5px;white-space:nowrap;">SPORTS DEPARTMENT</div>
            <div style="font-size:11px;color:#6B7280;font-weight:600;white-space:nowrap;">Official Portal</div>
        </div>
        """
    
    # Right Side: REVA logo and NAAC logo side-by-side, separated by a vertical line
    right_parts = []
    if reva_b64:
        right_parts.append(f'<img src="data:image/png;base64,{reva_b64}" style="height:44px; object-fit:contain;" />')
    else:
        right_parts.append('<div style="font-weight:800;font-size:12px;color:#F37021;">REVA</div>')
        
    if reva_b64 and naac_b64:
        right_parts.append('<div style="border-left: 2px solid #ddd; height: 32px; margin: 0 8px;"></div>')
        
    if naac_b64:
        right_parts.append(f'<img src="data:image/png;base64,{naac_b64}" style="height:44px; object-fit:contain;" />')
    else:
        right_parts.append('<div style="font-weight:800;font-size:12px;color:#1D9A5B;">NAAC A+</div>')
        
    right_html = f'<div style="display:flex; align-items:center; gap:12px;">{"".join(right_parts)}</div>'

    html = f"""
    <div class="reva-header">
        <div class="logo-box">
            {left_html}
        </div>
        <div class="center-title">
            <h1>DEPARTMENT OF PHYSICAL EDUCATION & SPORTS</h1>
            <p>Official Sports Event Registration System</p>
        </div>
        <div class="logo-box" style="justify-content: flex-end;">
            {right_html}
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
