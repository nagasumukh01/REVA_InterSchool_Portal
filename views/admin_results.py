import streamlit as st
import pandas as pd

import config
from modules import events as events_mod
from utils import ui, helpers


def render():
    ui.section_title("Competition Leaderboard & Results")

    all_events = events_mod.list_events()

    # Initialize points mapping for all schools
    schools_list = list(config.SCHOOLS.keys())
    points_map = {
        school: {"Organizing Points": 0, "Placement Points": 0, "Total Points": 0}
        for school in schools_list
    }

    # Calculate points from each event
    for e in all_events:
        org = e.get("organizing_school")
        assoc = e.get("associated_school")

        # 5 points for organizing
        if org and org in points_map:
            points_map[org]["Organizing Points"] += 5
            points_map[org]["Total Points"] += 5

        # 5 points for co-organizing (associated)
        if assoc and assoc != "None" and assoc in points_map:
            points_map[assoc]["Organizing Points"] += 5
            points_map[assoc]["Total Points"] += 5

        # Points for placements
        results = e.get("results")
        if results:
            pos1 = results.get("pos1")
            pos2 = results.get("pos2")
            pos3 = results.get("pos3")
            pos4 = results.get("pos4")

            if pos1 and pos1 in points_map:
                points_map[pos1]["Placement Points"] += 20
                points_map[pos1]["Total Points"] += 20
            if pos2 and pos2 in points_map:
                points_map[pos2]["Placement Points"] += 14
                points_map[pos2]["Total Points"] += 14
            if pos3 and pos3 in points_map:
                points_map[pos3]["Placement Points"] += 10
                points_map[pos3]["Total Points"] += 10
            if pos4 and pos4 in points_map:
                points_map[pos4]["Placement Points"] += 6
                points_map[pos4]["Total Points"] += 6

    # Convert to list of records
    records = []
    for school, pts in points_map.items():
        records.append({
            "School": school,
            "Organizing Points (5 pts)": pts["Organizing Points"],
            "Placement Points": pts["Placement Points"],
            "Total Points": pts["Total Points"],
        })

    # Sort by total points descending
    records = sorted(records, key=lambda x: x["Total Points"], reverse=True)

    # Assign Rank (handling ties simply by index)
    for index, r in enumerate(records, 1):
        r["Rank"] = index

    # Render Leaderboard Table
    df = pd.DataFrame(records)
    df = df[["Rank", "School", "Organizing Points (5 pts)", "Placement Points", "Total Points"]]

    st.markdown("### 📊 Points Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    ui.section_title("Completed Events & Placements")

    # Filter completed events with results
    completed_events = [e for e in all_events if e.get("registration_status") == "Closed" and e.get("results")]

    if not completed_events:
        ui.empty_state("No completed event results recorded yet.", icon="🏆")
    else:
        for e in completed_events:
            with st.container():
                # We can style this using raw HTML card structure
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
