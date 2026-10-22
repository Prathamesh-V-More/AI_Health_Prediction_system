import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask_mail import Message, Attachment
from app import mail


SEVERITY_COLORS = {
    "None":     colors.HexColor("#28a745"),
    "Mild":     colors.HexColor("#ffc107"),
    "Moderate": colors.HexColor("#fd7e14"),
    "Severe":   colors.HexColor("#dc3545"),
    "Critical": colors.HexColor("#6f0000"),
    "Unknown":  colors.HexColor("#6c757d"),
}


def generate_pdf_report(user, prediction_result, image_path=None):
    """
    Generate a styled PDF health report and return as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom styles ──────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#2c7be5"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#6c757d"),
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=13,
        textColor=colors.HexColor("#2c7be5"),
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
    )
    bold_style = ParagraphStyle(
        "Bold",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#333333"),
    )
    recommendation_style = ParagraphStyle(
        "Recommendation",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#155724"),
        backColor=colors.HexColor("#d4edda"),
        borderPad=8,
        spaceAfter=6,
        leading=16,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
        spaceBefore=10,
    )

    # ── Header ─────────────────────────────────────────────────
    story.append(Paragraph("🏥 AI Health Prediction System", title_style))
    story.append(Paragraph("Medical Image Analysis Report", subtitle_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c7be5")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Report meta ────────────────────────────────────────────
    now = datetime.utcnow().strftime("%B %d, %Y  %H:%M UTC")
    report_id = f"RPT-{user.id:04d}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    meta_data = [
        ["Report ID", report_id, "Date & Time", now],
    ]
    meta_table = Table(meta_data, colWidths=[3.5 * cm, 7 * cm, 3.5 * cm, 5.5 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#6c757d")),
        ("TEXTCOLOR", (2, 0), (2, 0), colors.HexColor("#6c757d")),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Patient Information ────────────────────────────────────
    story.append(Paragraph("Patient Information", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6")))
    story.append(Spacer(1, 0.2 * cm))

    patient_data = [
        ["Full Name", user.full_name, "Gender", user.gender],
        ["Email", user.email, "Age", f"{user.age} years"],
        ["Phone", user.phone, "Member Since", user.created_at.strftime("%B %Y")],
    ]
    patient_table = Table(patient_data, colWidths=[3.5 * cm, 7 * cm, 3.5 * cm, 5.5 * cm])
    patient_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#495057")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#495057")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Diagnosis Result ───────────────────────────────────────
    story.append(Paragraph("Diagnosis Result", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6")))
    story.append(Spacer(1, 0.2 * cm))

    severity = prediction_result.get("severity", "Unknown")
    sev_color = SEVERITY_COLORS.get(severity, colors.HexColor("#6c757d"))
    image_type_label = "Chest X-Ray" if prediction_result.get("image_type") == "xray" else "Skin Image"
    confidence = prediction_result.get("confidence", 0)

    diag_data = [
        ["Image Type", image_type_label],
        ["Predicted Disease", prediction_result.get("disease", "N/A")],
        ["Confidence Score", f"{confidence}%"],
        ["Severity Level", severity],
    ]
    diag_table = Table(diag_data, colWidths=[5 * cm, 14.5 * cm])
    diag_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#495057")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Highlight disease row
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#e8f0fe")),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (1, 1), (1, 1), 12),
        ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#2c7be5")),
        # Severity color
        ("TEXTCOLOR", (1, 3), (1, 3), sev_color),
        ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Confidence bar (visual) ────────────────────────────────
    story.append(Paragraph("Confidence Score Visualization", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6")))
    story.append(Spacer(1, 0.3 * cm))

    bar_width_total = 17 * cm
    filled = bar_width_total * (confidence / 100)
    empty = bar_width_total - filled

    bar_color = (
        colors.HexColor("#28a745") if confidence >= 80
        else colors.HexColor("#ffc107") if confidence >= 60
        else colors.HexColor("#dc3545")
    )

    bar_data = [[""]]
    bar_table = Table(bar_data, colWidths=[filled])
    bar_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bar_color),
        ("ROWHEIGHT", (0, 0), (-1, -1), 18),
        ("GRID", (0, 0), (-1, -1), 0, colors.white),
    ]))

    outer_data = [[bar_table, ""]]
    outer_table = Table(outer_data, colWidths=[filled, empty])
    outer_table.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#e9ecef")),
        ("ROWHEIGHT", (0, 0), (-1, -1), 18),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(outer_table)
    story.append(Paragraph(f"<para alignment='right'><b>{confidence}% confidence</b></para>", normal_style))
    story.append(Spacer(1, 0.5 * cm))

    # ── Recommendation ─────────────────────────────────────────
    story.append(Paragraph("Medical Recommendation", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6")))
    story.append(Spacer(1, 0.2 * cm))

    rec_text = prediction_result.get("recommendation", "Please consult a doctor.")
    story.append(Paragraph(f"✅  {rec_text}", recommendation_style))
    story.append(Spacer(1, 0.3 * cm))

    # ── Uploaded Image (if available) ─────────────────────────
    if image_path and os.path.exists(image_path):
        story.append(Paragraph("Analyzed Image", section_header_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6")))
        story.append(Spacer(1, 0.2 * cm))
        try:
            img = RLImage(image_path, width=8 * cm, height=8 * cm, kind="proportional")
            story.append(img)
        except Exception:
            story.append(Paragraph("(Image could not be embedded in report)", normal_style))
        story.append(Spacer(1, 0.3 * cm))

    # ── Disclaimer ─────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6")))
    story.append(Paragraph(
        "⚠️  DISCLAIMER: This report is generated by an AI system and is intended for informational "
        "purposes only. It does NOT constitute a medical diagnosis. Always consult a qualified "
        "healthcare professional for medical advice, diagnosis, or treatment.",
        disclaimer_style,
    ))
    story.append(Paragraph(
        "AI Health Prediction System  •  Confidential Patient Report",
        disclaimer_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def send_report_email(user, prediction_result, image_path=None):
    """Generate PDF and send it to the user's email."""
    pdf_bytes = generate_pdf_report(user, prediction_result, image_path)
    filename = f"health_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

    disease = prediction_result.get("disease", "N/A")
    severity = prediction_result.get("severity", "Unknown")
    confidence = prediction_result.get("confidence", 0)

    msg = Message(
        subject=f"🏥 Your Health Prediction Report — {disease}",
        recipients=[user.email],
        html=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;
                    border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2c7be5, #1a5cb8);
                        padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🏥 AI Health Prediction System</h1>
                <p style="color: #cce0ff; margin: 8px 0 0;">Your Medical Analysis Report is Ready</p>
            </div>

            <!-- Body -->
            <div style="padding: 30px; background: #ffffff;">
                <p style="font-size: 16px;">Hello <strong>{user.full_name}</strong>,</p>
                <p>Your medical image has been analyzed. Here is a summary of your results:</p>

                <!-- Result Card -->
                <div style="background: #f0f6ff; border-left: 4px solid #2c7be5;
                            border-radius: 6px; padding: 20px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; color: #666; width: 40%;">Predicted Disease</td>
                            <td style="padding: 8px; font-weight: bold; color: #2c7be5; font-size: 16px;">{disease}</td>
                        </tr>
                        <tr style="background: #e8f0fe;">
                            <td style="padding: 8px; color: #666;">Confidence Score</td>
                            <td style="padding: 8px; font-weight: bold;">{confidence}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; color: #666;">Severity Level</td>
                            <td style="padding: 8px; font-weight: bold; color: {'#dc3545' if severity in ['Severe','Critical'] else '#ffc107' if severity == 'Moderate' else '#28a745'};">{severity}</td>
                        </tr>
                    </table>
                </div>

                <p style="background: #d4edda; border-radius: 6px; padding: 15px; color: #155724;">
                    📋 <strong>Recommendation:</strong> {prediction_result.get('recommendation', 'Please consult a doctor.')}
                </p>

                <p>The full detailed PDF report is attached to this email. Please review it and
                share it with your healthcare provider if needed.</p>

                <div style="background: #fff3cd; border-radius: 6px; padding: 15px;
                            margin-top: 20px; color: #856404; font-size: 13px;">
                    ⚠️ <strong>Disclaimer:</strong> This is an AI-generated report for informational
                    purposes only. It does not replace professional medical advice.
                    Always consult a qualified doctor.
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f8f9fa; padding: 20px; text-align: center;
                        border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px; margin: 0;">
                    AI Health Prediction System &copy; {datetime.utcnow().year} &nbsp;|&nbsp;
                    This email was sent to {user.email}
                </p>
            </div>
        </div>
        """,
    )

    msg.attach(
        filename=filename,
        content_type="application/pdf",
        data=pdf_bytes,
    )

    mail.send(msg)
