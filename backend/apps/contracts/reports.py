"""PDF report generator using ReportLab."""
from __future__ import annotations

from io import BytesIO

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from .models import Contract

RISK_COLORS = {
    "high": colors.HexColor("#dc2626"),
    "medium": colors.HexColor("#f59e0b"),
    "low": colors.HexColor("#3b82f6"),
    "none": colors.HexColor("#16a34a"),
}


def build_report(contract: Contract) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm, title=f"Halal Analysis - {contract.title}",
    )
    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey)

    story = []
    story.append(Paragraph("Halal Contract Analyzer — Compliance Report", h1))
    story.append(Paragraph(f"<b>Contract:</b> {contract.title}", body))
    story.append(Paragraph(f"<b>Generated:</b> {contract.updated_at:%Y-%m-%d %H:%M UTC}", body))
    story.append(Spacer(1, 0.4 * cm))

    analysis = getattr(contract, "analysis", None)
    if analysis:
        data = [
            ["Risk score", f"{analysis.risk_score} / 100"],
            ["High-risk clauses", analysis.high_risk_count],
            ["Medium-risk clauses", analysis.medium_risk_count],
            ["Low-risk clauses", analysis.low_risk_count],
            ["Total clauses", analysis.clauses_count],
            ["Engine version", analysis.engine_version],
        ]
        t = Table(data, colWidths=[6 * cm, 8 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))
        if analysis.summary:
            story.append(Paragraph(analysis.summary, body))

    story.append(PageBreak())
    story.append(Paragraph("Clause-by-clause findings", h2))

    for clause in contract.clauses.all():
        color = RISK_COLORS.get(clause.risk_level, colors.black)
        story.append(Paragraph(
            f"<b>Clause {clause.position + 1}</b> — "
            f"<font color='{color.hexval()}'>{clause.risk_level.upper()}</font>"
            + (f" • {clause.category}" if clause.category else ""),
            h2,
        ))
        story.append(Paragraph(_escape(clause.text[:1500]), body))
        if clause.explanation:
            story.append(Paragraph(f"<b>Why flagged:</b> {_escape(clause.explanation)}", body))
        for ev in clause.evidences or []:
            story.append(Paragraph(
                f"<i>{ev.get('source', '')} — {ev.get('reference', '')}</i>: "
                f"{_escape(ev.get('text', ''))}",
                small,
            ))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f"<i>{settings.DISCLAIMER}</i>", small))

    doc.build(story)
    return buffer.getvalue()


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
