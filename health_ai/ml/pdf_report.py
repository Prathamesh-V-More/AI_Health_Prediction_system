"""
PDF report generator + email sender.
All heavy imports are lazy-loaded to keep app startup fast.
"""
import io
import os
from datetime import datetime


def generate_pdf(user, result, image_path=None):
    """Return PDF as bytes."""
    # Lazy import - only loads when first prediction is made
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (HRFlowable, SimpleDocTemplate,
                                    Paragraph, Spacer, Table, TableStyle)

    SEVERITY_COLORS = {
        "None":     colors.HexColor("#28a745"),
        "Mild":     colors.HexColor("#ffc107"),
        "Moderate": colors.HexColor("#fd7e14"),
        "Severe":   colors.HexColor("#dc3545"),
        "Critical": colors.HexColor("#6f0000"),
        "Unknown":  colors.HexColor("#6c757d"),
    }

    buf  = io.BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    def s(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    title_s = s("T", fontSize=22, textColor=colors.HexColor("#2c7be5"),
                spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold")
    sub_s   = s("S", fontSize=11, textColor=colors.HexColor("#6c757d"),
                spaceAfter=2, alignment=TA_CENTER)
    sec_s   = s("H", fontSize=13, textColor=colors.HexColor("#2c7be5"),
                fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body_s  = s("B", fontSize=10, textColor=colors.HexColor("#333333"), spaceAfter=4)
    rec_s   = s("R", fontSize=10, textColor=colors.HexColor("#155724"),
                backColor=colors.HexColor("#d4edda"), borderPad=8,
                spaceAfter=6, leading=16)
    disc_s  = s("D", fontSize=8, textColor=colors.HexColor("#999999"),
                alignment=TA_CENTER, spaceBefore=10)

    def hr():
        return HRFlowable(width="100%", thickness=0.5,
                          color=colors.HexColor("#dee2e6"))

    def tbl(data, widths, extra=None):
        t = Table(data, colWidths=widths)
        base = [
            ("FONTNAME",       (0,0),(-1,-1), "Helvetica"),
            ("FONTSIZE",       (0,0),(-1,-1), 10),
            ("GRID",           (0,0),(-1,-1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING",     (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",  (0,0),(-1,-1), 7),
            ("LEFTPADDING",    (0,0),(-1,-1), 8),
            ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0,0),(-1,-1),
             [colors.white, colors.HexColor("#f8f9fa")]),
        ]
        if extra:
            base.extend(extra)
        t.setStyle(TableStyle(base))
        return t

    # Header
    story += [
        Paragraph("AI Health Prediction System", title_s),
        Paragraph("Medical Image Analysis Report", sub_s),
        Spacer(1, 0.3*cm),
        HRFlowable(width="100%", thickness=2,
                   color=colors.HexColor("#2c7be5")),
        Spacer(1, 0.4*cm),
    ]

    # Meta
    now       = datetime.utcnow().strftime("%B %d, %Y  %H:%M UTC")
    report_id = f"RPT-{user.id:04d}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    story.append(tbl(
        [["Report ID", report_id, "Date & Time", now]],
        [3.5*cm, 7*cm, 3.5*cm, 5.5*cm],
        [("FONTNAME",(1,0),(1,0),"Helvetica-Bold"),
         ("FONTNAME",(3,0),(3,0),"Helvetica-Bold"),
         ("TEXTCOLOR",(0,0),(0,0),colors.HexColor("#6c757d")),
         ("TEXTCOLOR",(2,0),(2,0),colors.HexColor("#6c757d"))],
    ))
    story.append(Spacer(1, 0.5*cm))

    # Patient
    story += [Paragraph("Patient Information", sec_s), hr(), Spacer(1, 0.2*cm)]
    story.append(tbl(
        [
            ["Full Name", user.full_name, "Gender", user.gender or "-"],
            ["Email",     user.email,     "Age",    f"{user.age} years" if user.age else "-"],
            ["Phone",     user.phone or "-", "Member Since",
             user.created_at.strftime("%B %Y") if user.created_at else "-"],
        ],
        [3.5*cm, 7*cm, 3.5*cm, 5.5*cm],
        [("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
         ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
         ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#495057")),
         ("TEXTCOLOR",(2,0),(2,-1),colors.HexColor("#495057"))],
    ))
    story.append(Spacer(1, 0.5*cm))

    # Diagnosis
    story += [Paragraph("Diagnosis Result", sec_s), hr(), Spacer(1, 0.2*cm)]
    severity   = result.get("severity", "Unknown")
    sev_color  = SEVERITY_COLORS.get(severity, colors.HexColor("#6c757d"))
    img_label  = "Chest X-Ray" if result.get("image_type") == "xray" else "Skin Image"
    confidence = result.get("confidence", 0)
    disease    = result.get("disease", "N/A")

    story.append(tbl(
        [
            ["Image Type",        img_label],
            ["Predicted Disease", disease],
            ["Confidence Score",  f"{confidence}%"],
            ["Severity Level",    severity],
        ],
        [5*cm, 14.5*cm],
        [
            ("BACKGROUND", (0,1),(-1,1), colors.HexColor("#e8f0fe")),
            ("FONTNAME",   (1,1),(1,1),  "Helvetica-Bold"),
            ("FONTSIZE",   (1,1),(1,1),  12),
            ("TEXTCOLOR",  (1,1),(1,1),  colors.HexColor("#2c7be5")),
            ("TEXTCOLOR",  (1,3),(1,3),  sev_color),
            ("FONTNAME",   (1,3),(1,3),  "Helvetica-Bold"),
            ("FONTNAME",   (0,0),(0,-1), "Helvetica-Bold"),
            ("TEXTCOLOR",  (0,0),(0,-1), colors.HexColor("#495057")),
        ],
    ))
    story.append(Spacer(1, 0.5*cm))

    # Recommendation
    story += [Paragraph("Medical Recommendation", sec_s), hr(), Spacer(1, 0.2*cm)]
    story.append(Paragraph(
        f"  {result.get('recommendation', 'Consult a doctor.')}", rec_s))
    story.append(Spacer(1, 0.3*cm))

    # Uploaded image
    if image_path and os.path.exists(image_path):
        from reportlab.platypus import Image as RLImage
        story += [Paragraph("Analyzed Image", sec_s), hr(), Spacer(1, 0.2*cm)]
        try:
            story.append(RLImage(image_path, width=8*cm,
                                 height=8*cm, kind="proportional"))
        except Exception:
            story.append(Paragraph("(Image could not be embedded)", body_s))
        story.append(Spacer(1, 0.3*cm))

    # Disclaimer
    story += [
        Spacer(1, 0.5*cm),
        HRFlowable(width="100%", thickness=1,
                   color=colors.HexColor("#dee2e6")),
        Paragraph(
            "DISCLAIMER: This report is generated by an AI system for informational "
            "purposes only. It does NOT constitute a medical diagnosis. Always consult "
            "a qualified healthcare professional.", disc_s),
        Paragraph("AI Health Prediction System  -  Confidential Patient Report", disc_s),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.read()


def send_report_email(mail_instance, user, result, image_path=None):
    """Generate PDF and email it to the user."""
    from flask_mail import Message

    pdf_bytes  = generate_pdf(user, result, image_path)
    filename   = f"health_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    disease    = result.get("disease", "N/A")
    severity   = result.get("severity", "Unknown")
    confidence = result.get("confidence", 0)
    rec        = result.get("recommendation", "Please consult a doctor.")
    year       = datetime.utcnow().year

    sev_css = ("#dc3545" if severity in ("Severe","Critical")
               else "#ffc107" if severity == "Moderate"
               else "#28a745")

    msg = Message(
        subject=f"Your Health Prediction Report - {disease}",
        recipients=[user.email],
        html=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                    border:1px solid #e0e0e0;border-radius:10px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#2c7be5,#1a5cb8);
                      padding:30px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:22px;">AI Health Prediction System</h1>
            <p style="color:#cce0ff;margin:8px 0 0;">Your Medical Analysis Report is Ready</p>
          </div>
          <div style="padding:30px;background:#fff;">
            <p>Hello <strong>{user.full_name}</strong>,</p>
            <p>Your medical image has been analyzed. Summary:</p>
            <div style="background:#f0f6ff;border-left:4px solid #2c7be5;
                        border-radius:6px;padding:20px;margin:20px 0;">
              <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:8px;color:#666;width:40%;">Predicted Disease</td>
                    <td style="padding:8px;font-weight:bold;color:#2c7be5;font-size:16px;">{disease}</td></tr>
                <tr style="background:#e8f0fe;">
                    <td style="padding:8px;color:#666;">Confidence Score</td>
                    <td style="padding:8px;font-weight:bold;">{confidence}%</td></tr>
                <tr><td style="padding:8px;color:#666;">Severity Level</td>
                    <td style="padding:8px;font-weight:bold;color:{sev_css};">{severity}</td></tr>
              </table>
            </div>
            <p style="background:#d4edda;border-radius:6px;padding:15px;color:#155724;">
              <strong>Recommendation:</strong> {rec}
            </p>
            <p>The full PDF report is attached to this email.</p>
            <div style="background:#fff3cd;border-radius:6px;padding:15px;
                        margin-top:20px;color:#856404;font-size:13px;">
              This is an AI-generated report for informational purposes only.
              It does not replace professional medical advice.
            </div>
          </div>
          <div style="background:#f8f9fa;padding:20px;text-align:center;
                      border-top:1px solid #e0e0e0;">
            <p style="color:#999;font-size:12px;margin:0;">
              AI Health Prediction System &copy; {year}
            </p>
          </div>
        </div>
        """,
    )
    msg.attach(filename=filename, content_type="application/pdf", data=pdf_bytes)
    mail_instance.send(msg)
