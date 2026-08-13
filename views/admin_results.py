import streamlit as st

import config
from modules import events as events_mod
from utils import ui, helpers, leaderboard


def render():
    ui.section_title("Competition Leaderboard & Results")

    # Render Leaderboard Table using shared utility
    leaderboard.render_leaderboard_table(show_all_columns=True)

    st.write("")
    ui.section_title("Completed Events & Placements")

    # Filter completed events with results
    all_events = events_mod.list_events()
    completed_events = [e for e in all_events if e.get("registration_status") == "Closed" and e.get("results")]

    if not completed_events:
        ui.empty_state("No completed event results recorded yet.", icon="🏆")
    else:
        for e in completed_events:
            with st.container():
                res = e["results"]
                assoc_text = f" &nbsp;|&nbsp; 🤝 Associated: {e['associated_school']}" if e.get('associated_school') and e['associated_school'] != 'None' else ""
                
                st.markdown(
                    f"""
                    <div class="reva-card" style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding-bottom:8px; margin-bottom:8px;">
                            <strong style="font-size:17px; color:{config.COLORS['primary']};">🏆 {e.get('event_name','')}</strong>
                            <span style="font-size:12px; color:#6B7280;">⚽ {e.get('sport_category','')}</span>
                        </div>
                        <div style="font-size:13px; color:#6B7280; margin-bottom:10px;">
                            🏟️ Venue: {e.get('venue','')} &nbsp;|&nbsp; 🗓️ Event Date: {helpers.format_date(e.get('event_date'))}<br>
                            🏫 Organizer: {e.get('organizing_school','')}{assoc_text}
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; background:#f9f9f9; padding:10px; border-radius:8px;">
                            <div>
                                <span style="font-weight:700; color:#E0A800;">🥇 1st Place:</span> {res.get('pos1') or 'None'}<br>
                                <span style="font-weight:700; color:#8A8A8A;">🥈 2nd Place:</span> {res.get('pos2') or 'None'}
                            </div>
                            <div>
                                <span style="font-weight:700; color:#b07040;">🥉 3rd Place:</span> {res.get('pos3') or 'None'}<br>
                                <span style="font-weight:700; color:#5c7080;">🎖️ 4th Place:</span> {res.get('pos4') or 'None'}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
