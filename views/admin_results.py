import streamlit as st
import pandas as pd

import config
from modules import events as events_mod
from utils import ui, helpers


def render():
    ui.section_title("Competition Leaderboard & Results")

    all_events = events_mod.list_events()

    # Read all registrations to count participation points
    from utils import storage
    all_regs = storage.read_table("registrations")

    # Initialize points mapping for all schools
    schools_list = list(config.SCHOOLS.keys())
    points_map = {
        school: {
            "Organizing Points": 0,
            "Placement Points": 0,
            "Participation Points": 0,
            "Total Points": 0
        }
        for school in schools_list
    }

    # Calculate 4 points per approved participation registration
    for r in all_regs:
        if r.get("status") == "Approved":
            sch = r.get("school")
            if sch and sch in points_map:
                points_map[sch]["Participation Points"] += 4
                points_map[sch]["Total Points"] += 4

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
            "Participation Points (4 pts)": pts["Participation Points"],
            "Total Points": pts["Total Points"],
        })

    # Sort by total points descending
    records = sorted(records, key=lambda x: x["Total Points"], reverse=True)

    # Assign Rank (handling ties simply by index)
    for index, r in enumerate(records, 1):
        r["Rank"] = index

    # Render Leaderboard Table (HTML)
    table_rows = []
    for r in records:
        rank = r["Rank"]
        school = r["School"]
        org_pts = r["Organizing Points (5 pts)"]
        place_pts = r["Placement Points"]
        part_pts = r["Participation Points (4 pts)"]
        tot_pts = r["Total Points"]

        if rank == 1:
            rank_html = '<span style="background: #FFF9DB; color: #D08000; border: 1px solid #FFE066; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 13px;">🏆 1st</span>'
            row_bg = "background-color: #FFFDF5;"
        elif rank == 2:
            rank_html = '<span style="background: #F1F3F5; color: #495057; border: 1px solid #CED4DA; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 13px;">🥈 2nd</span>'
            row_bg = "background-color: #FAFAFA;"
        elif rank == 3:
            rank_html = '<span style="background: #FCE8E6; color: #C53030; border: 1px solid #FAD2CF; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 13px;">🥉 3rd</span>'
            row_bg = "background-color: #FFFDFD;"
        else:
            rank_html = f'<span style="color: #6B7280; font-weight: 700; font-size: 13px; padding-left: 10px;">{rank}</span>'
            row_bg = ""

        table_rows.append(f"""
        <tr style="{row_bg} border-bottom: 1px solid #E5E7EB;">
            <td style="padding: 14px 16px; text-align: center; vertical-align: middle;">{rank_html}</td>
            <td style="padding: 14px 16px; font-weight: 600; color: #1F2937; vertical-align: middle;">{school}</td>
            <td style="padding: 14px 16px; text-align: center; color: #4B5563; font-weight: 500; vertical-align: middle;">{org_pts}</td>
            <td style="padding: 14px 16px; text-align: center; color: #4B5563; font-weight: 500; vertical-align: middle;">{place_pts}</td>
            <td style="padding: 14px 16px; text-align: center; color: #4B5563; font-weight: 500; vertical-align: middle;">{part_pts}</td>
            <td style="padding: 14px 16px; text-align: center; font-weight: 800; font-size: 16px; color: #F37021; vertical-align: middle;">{tot_pts}</td>
        </tr>
        """)

    table_body = "".join(table_rows)

    html_table = f"""
    <style>
        .pts-table-container {{
            width: 100%;
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 25px;
            border: 1px solid #E5E7EB;
        }}
        .pts-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
        }}
        .pts-table th {{
            background: linear-gradient(135deg, #F37021, #FF8D48);
            color: white;
            font-weight: 700;
            padding: 16px;
            text-align: left;
            letter-spacing: 0.5px;
        }}
        .pts-table tr:hover {{
            background-color: #F8FAFC !important;
        }}
    </style>
    <div class="pts-table-container">
        <table class="pts-table">
            <thead>
                <tr>
                    <th style="text-align: center; width: 100px;">Rank</th>
                    <th>School</th>
                    <th style="text-align: center; width: 180px;">Organizing Points (5 pts)</th>
                    <th style="text-align: center; width: 150px;">Placement Points</th>
                    <th style="text-align: center; width: 180px;">Participation Points (4 pts)</th>
                    <th style="text-align: center; width: 130px; text-align: center;">Total Points</th>
                </tr>
            </thead>
            <tbody>
                {table_body}
            </tbody>
        </table>
    </div>
    """

    st.markdown("### 📊 Points Table")
    st.markdown(html_table.replace("\n", ""), unsafe_allow_html=True)

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
