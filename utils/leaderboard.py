import streamlit as st
import pandas as pd

import config
from utils import storage


def calculate_points() -> list[dict]:
    # Read tables
    all_events = storage.read_table("events")
    all_regs = storage.read_table("registrations")
    
    # Try reading aiu_records, default to empty list if file doesn't exist yet
    try:
        all_aiu = storage.read_table("aiu_records")
    except Exception:
        all_aiu = []

    # Initialize points mapping for all schools
    schools_list = list(config.SCHOOLS.keys())
    points_map = {
        school: {
            "Organizing Points": 0,
            "Placement Points": 0,
            "Participation Points": 0,
            "AIU Points": 0,
            "Total Points": 0,
        }
        for school in schools_list
    }

    # 1. Calculate participation points (4 pts per approved registration)
    for r in all_regs:
        if r.get("status") == "Approved":
            sch = r.get("school")
            if sch and sch in points_map:
                points_map[sch]["Participation Points"] += 4
                points_map[sch]["Total Points"] += 4

    # 2. Calculate points from each event (organizing and placement)
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

    # 3. Calculate points from AIU & Other achievements
    for record in all_aiu:
        school = record.get("school_name")
        pts = record.get("points", 0)
        try:
            pts_int = int(pts)
        except (ValueError, TypeError):
            pts_int = 0

        if school and school in points_map:
            points_map[school]["AIU Points"] += pts_int
            points_map[school]["Total Points"] += pts_int

    # Convert to list of records
    records = []
    for school, pts in points_map.items():
        records.append({
            "School": school,
            "Organizing Points (5 pts)": pts["Organizing Points"],
            "Placement Points": pts["Placement Points"],
            "Participation Points (4 pts)": pts["Participation Points"],
            "AIU & Other Points": pts["AIU Points"],
            "Total Points": pts["Total Points"],
        })

    # Sort by total points descending to assign global rank
    records = sorted(records, key=lambda x: x["Total Points"], reverse=True)

    # Assign Rank (handling ties simply by index)
    for index, r in enumerate(records, 1):
        r["Rank"] = index

    return records


def render_leaderboard_table(show_all_columns: bool):
    records = calculate_points()

    if show_all_columns:
        # Full view with filters for logged in users
        col_search, col_sort = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search School", placeholder="Enter school name to filter...", key="leaderboard_search")
        with col_sort:
            sort_by = st.selectbox("↕️ Sort by", ["Total Points", "School Name", "Organizing Points", "Placement Points", "Participation Points", "AIU & Other Points"], key="leaderboard_sort")

        # Apply search filter
        filtered_records = list(records)
        if search_query:
            filtered_records = [r for r in filtered_records if search_query.lower() in r["School"].lower()]

        # Apply sort filter
        if sort_by == "School Name":
            filtered_records = sorted(filtered_records, key=lambda x: x["School"])
        elif sort_by == "Organizing Points":
            filtered_records = sorted(filtered_records, key=lambda x: x["Organizing Points (5 pts)"], reverse=True)
        elif sort_by == "Placement Points":
            filtered_records = sorted(filtered_records, key=lambda x: x["Placement Points"], reverse=True)
        elif sort_by == "Participation Points":
            filtered_records = sorted(filtered_records, key=lambda x: x["Participation Points (4 pts)"], reverse=True)
        elif sort_by == "AIU & Other Points":
            filtered_records = sorted(filtered_records, key=lambda x: x["AIU & Other Points"], reverse=True)
        elif sort_by == "Total Points":
            filtered_records = sorted(filtered_records, key=lambda x: x["Total Points"], reverse=True)

        table_rows = []
        for r in filtered_records:
            rank = r["Rank"]
            school = r["School"]
            org_pts = r["Organizing Points (5 pts)"]
            place_pts = r["Placement Points"]
            part_pts = r["Participation Points (4 pts)"]
            aiu_pts = r["AIU & Other Points"]
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
                <td style="padding: 14px 16px; text-align: center; color: #4B5563; font-weight: 500; vertical-align: middle;">{aiu_pts}</td>
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
                        <th style="text-align: center; width: 160px;">AIU & Other Points</th>
                        <th style="text-align: center; width: 130px;">Total Points</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
        """
        st.markdown(html_table.replace("\n", ""), unsafe_allow_html=True)
    else:
        # Simple view for non-logged in users (Rank, School Name, Total Points)
        table_rows = []
        for r in records:
            rank = r["Rank"]
            school = r["School"]
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
                        <th style="text-align: center; width: 150px;">Total Points</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
        """
        st.markdown(html_table.replace("\n", ""), unsafe_allow_html=True)
