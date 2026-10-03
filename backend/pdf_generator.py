from __future__ import annotations

import io
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer


def as_text(sheet: dict) -> str:
    lines = [f"FORMULAFORGE AI | {sheet['subject']}", ""]
    for topic in sheet.get("topics", []):
        lines.extend([topic["topic_name"].upper(), ""])
        for item in topic["formulas"]:
            lines.extend([f"Formula: {item['formula']}", f"Meaning: {item['meaning']}", f"Variables: {'; '.join(item['variables'])}", f"Use: {item['use']}", ""])
    lines.extend(["MOST FREQUENTLY USED FORMULAE", ""])
    for item in sheet.get("important_formulas", []):
        lines.extend([f"Formula: {item['formula']}", f"Meaning: {item['meaning']}", ""])
    return "\n".join(lines)


def as_pdf(sheet: dict) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", textColor=HexColor("#0F766E"), fontSize=22, leading=27)
    heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontName="Helvetica-Bold", textColor=HexColor("#0F172A"), spaceBefore=14, spaceAfter=8)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=14, spaceAfter=3)
    formula = ParagraphStyle("Formula", parent=body, fontName="Helvetica-Bold", fontSize=13, textColor=HexColor("#0F766E"), spaceAfter=6)
    story = [Paragraph("FormulaForge AI", title), Paragraph(escape(sheet["subject"]), styles["Subtitle"]), Spacer(1, 7 * mm)]
    for topic in sheet.get("topics", []):
        story.append(Paragraph(escape(topic["topic_name"]), heading))
        for item in topic["formulas"]:
            card = [Paragraph(escape(item["formula"]), formula), Paragraph(f"<b>Meaning:</b> {escape(item['meaning'])}", body), Paragraph(f"<b>Variables:</b> {escape('; '.join(item['variables']))}", body), Paragraph(f"<b>Use:</b> {escape(item['use'])}", body), Spacer(1, 3 * mm)]
            story.append(KeepTogether(card))
    if sheet.get("important_formulas"):
        story.append(Paragraph("Most Frequently Used Formulae", heading))
        for item in sheet["important_formulas"]:
            story.append(KeepTogether([Paragraph(escape(item["formula"]), formula), Paragraph(escape(item["meaning"]), body), Spacer(1, 2 * mm)]))
    document.build(story)
    return buffer.getvalue()
