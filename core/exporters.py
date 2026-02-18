from __future__ import annotations
from typing import Dict, Any
from io import BytesIO
import pandas as pd

def export_excel(sheets: Dict[str, pd.DataFrame]) -> bytes:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in sheets.items():
            if df is None or df.empty:
                pd.DataFrame([{"Info":"Sin datos"}]).to_excel(writer, sheet_name=name[:31], index=False)
            else:
                df.to_excel(writer, sheet_name=name[:31], index=False)
    return bio.getvalue()

def export_pdf(title: str, meta: Dict[str, Any], sections: Dict[str, pd.DataFrame]) -> bytes:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    bio = BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for k, v in meta.items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", styles["BodyText"]))
    story.append(Spacer(1, 12))
    for sec, df in sections.items():
        story.append(Paragraph(sec, styles["Heading2"]))
        if df is None or df.empty:
            story.append(Paragraph("Sin datos.", styles["BodyText"]))
            story.append(Spacer(1, 8))
            continue
        data = [list(df.columns)] + df.astype(str).values.tolist()
        story.append(Table(data, hAlign="LEFT"))
        story.append(Spacer(1, 12))
    doc.build(story)
    return bio.getvalue()
