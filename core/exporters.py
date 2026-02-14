# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Any
import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_excel(results: Dict[str, Any]) -> bytes:
    """
    results: dict con DataFrames y dicts de totales
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for k, v in results.items():
            if isinstance(v, pd.DataFrame):
                sheet = k[:31]
                v.to_excel(writer, sheet_name=sheet, index=False)
            elif isinstance(v, dict):
                df = pd.DataFrame([v])
                sheet = (k + "_tot")[:31]
                df.to_excel(writer, sheet_name=sheet, index=False)
    return output.getvalue()

def export_pdf_memoria(meta: Dict[str, Any], tables: Dict[str, pd.DataFrame], totals: Dict[str, Dict[str, Any]]) -> bytes:
    """
    PDF simple de memoria de cálculo.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    story = []

    title = meta.get("titulo", "Memoria de Predimensionamiento")
    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 0.3*cm))

    if meta.get("proyecto"):
        story.append(Paragraph(f"<b>Proyecto:</b> {meta['proyecto']}", styles["Normal"]))
    if meta.get("ubicacion"):
        story.append(Paragraph(f"<b>Ubicación:</b> {meta['ubicacion']}", styles["Normal"]))
    if meta.get("fecha"):
        story.append(Paragraph(f"<b>Fecha:</b> {meta['fecha']}", styles["Normal"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("<b>Resumen</b>", styles["Heading2"]))
    for mod, tot in totals.items():
        story.append(Paragraph(f"<b>{mod}</b>", styles["Heading3"]))
        for kk, vv in tot.items():
            if isinstance(vv, (int, float, str)):
                story.append(Paragraph(f"- {kk}: {vv}", styles["Normal"]))
        story.append(Spacer(1, 0.2*cm))

    # Tablas clave (limitadas a primeras filas para tamaño)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>Tablas de resultados</b>", styles["Heading2"]))

    for name, df in tables.items():
        story.append(Paragraph(f"<b>{name}</b>", styles["Heading3"]))
        dff = df.copy()
        if len(dff) > 25:
            dff = dff.head(25)
            story.append(Paragraph("(Se muestran las primeras 25 filas.)", styles["Italic"]))
        # convertir a lista (robusto ante tablas vacías)
        if dff is None:
            data = [["(no data)"]]
        else:
            if dff.shape[1] == 0:
                data = [["(no columns)"]]
            elif len(dff) == 0:
                data = [list(dff.columns), ["(no rows)"]]
            else:
                data = [list(dff.columns)] + dff.fillna("").astype(str).values.tolist()
        t = Table(data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.35*cm))

    doc.build(story)
    return buffer.getvalue()
