"""Report generation: Excel, CSV, PDF. No Streamlit imports."""

import io
from collections import Counter

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import config
from utils import storage, helpers


def registrations_dataframe(event_id: str | None = None) -> pd.DataFrame:
    regs = storage.find_rows("registrations", event_id=event_id) if event_id else storage.read_table("registrations")
    events = {e["id"]: e.get("event_name", "") for e in storage.read_table("events")}

    rows = []
    for r in regs:
        rows.append({
            "Event": events.get(r.get("event_id"), r.get("event_id")),
            "School": r.get("school", ""),
            "Branch": r.get("branch", ""),
            "Vertical Head": r.get("vh_name", ""),
            "Captain": r.get("captain_name", ""),
            "Captain SRN": r.get("captain_srn", ""),
            "Vice-Captain": r.get("vice_captain_name", ""),
            "Vice-Captain SRN": r.get("vice_captain_srn", ""),
            "Status": r.get("status", ""),
            "Registered On": helpers.format_date(r.get("registered_at")),
        })
    return pd.DataFrame(rows)


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Registrations")
        ws = writer.sheets["Registrations"]
        for col_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in col_cells) + 2
            ws.column_dimensions[col_cells[0].column_letter].width = min(length, 40)
    return buffer.getvalue()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_pdf_bytes(df: pd.DataFrame, title: str = "Registration Report") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                             leftMargin=15 * mm, rightMargin=15 * mm,
                             topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    elements = [Paragraph("REVA InterSchool Competition Portal", styles["Title"]),
                Paragraph(title, styles["Heading2"]),
                Spacer(1, 8)]

    if df.empty:
        elements.append(Paragraph("No records found.", styles["Normal"]))
    else:
        data = [list(df.columns)] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(config.COLORS["primary"])),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(table)

    doc.build(elements)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# Analytics helpers (used by the admin dashboard)
# --------------------------------------------------------------------------
def registration_trend() -> pd.DataFrame:
    regs = storage.read_table("registrations")
    dates = [helpers.parse_date(r.get("registered_at")) for r in regs]
    dates = [d for d in dates if d]
    counter = Counter(dates)
    df = pd.DataFrame(sorted(counter.items()), columns=["Date", "Registrations"])
    return df


def event_wise_counts() -> pd.DataFrame:
    events = storage.read_table("events")
    rows = [{"Event": e.get("event_name", ""), "Registrations": len(storage.find_rows("registrations", event_id=e["id"]))}
            for e in events]
    return pd.DataFrame(rows)


def school_wise_counts() -> pd.DataFrame:
    regs = storage.read_table("registrations")
    counter = Counter(r.get("school", "Unknown") for r in regs)
    return pd.DataFrame(sorted(counter.items()), columns=["School", "Registrations"])


def branch_wise_counts() -> pd.DataFrame:
    regs = storage.read_table("registrations")
    counter = Counter(r.get("branch", "Unknown") for r in regs)
    return pd.DataFrame(sorted(counter.items()), columns=["Branch", "Registrations"])
