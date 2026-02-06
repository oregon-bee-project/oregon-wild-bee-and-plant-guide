from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

def generate_pdf_from_rows(rows, title="Bee Data Export"):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    body_style.wordWrap = "CJK"  
    elements = []

    # Title
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    
    headers = ["Metric", "Value"]
    table_data = [headers]

    for row in rows:
        metric = str(row.get("Metric", ""))
        value = row.get("Value", "")

        # Convert dicts/lists to readable strings
        if isinstance(value, (dict, list)):
            value = str(value)
        
        metric_p = Paragraph(metric, body_style)
        value_p = Paragraph(str(value), body_style)
        table_data.append([metric_p, value_p])

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer
