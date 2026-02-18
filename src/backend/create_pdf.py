from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# Styling
styles = getSampleStyleSheet()
body_style = styles["BodyText"]
body_style.wordWrap = "CJK"  
bold_body_style = ParagraphStyle(
    "BoldBody",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    wordWrap="CJK"
)

heading_style = styles["Heading2"]
elements = []

def format_common_bees(bees):
    items = []
    for bee in bees:
        name = bee.get("scientificName", "Unknown")
        count = bee.get("count", 0)
        text = f"\t• {name} — {count} observations"
        items.append(Paragraph(text, body_style))
        items.append(Spacer(1, 4))
    return items


def generate_pdf_from_rows(rows, title="Common Bee and Plant Report", location="Oregon"):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    # Title
    text=f"{title} - {location}"
    elements.append(Paragraph(text, styles["Title"]))
    elements.append(Spacer(1, 12))

    # Extract Data
    num_rows_value = None
    unique_bees = None
    unique_plants = None
    common_bees = None
    common_plant = None
    common_plant_count = None
    cp_top_bees = None
    remaining_rows = []

    for row in rows:
        if row.get("Metric") == "numRows":
            num_rows_value = row.get("Value")
        elif(row.get("Metric") == "numUniqueBees"):
            unique_bees = row.get("Value")
        elif(row.get("Metric") == "numUniquePlants"):
            unique_plants = row.get("Value")
        elif(row.get("Metric") == "mostCommonBees"):
            common_bees = row.get("Value")
        elif(row.get("Metric") == "mostCommonPlant.commonName"):
            common_plant = row.get("Value")
        elif(row.get("Metric") == "mostCommonPlant.count"):
            common_plant_count = row.get("Value")
        elif(row.get("Metric") == "mostCommonPlant.topBees"):
            cp_top_bees = row.get("Value")
            remaining_rows.append(row)

    # General Observations Stats
    elements.append(Paragraph("Summary Statistics", heading_style))
    elements.append(Spacer(1, 6))

    if num_rows_value is not None:
        text = f"<b>Number of Observations:</b> {num_rows_value}"
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 12))
    
    if unique_bees is not None:
        text = f"<b>Number of Unique Bees:</b> {unique_bees}"
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 12))
    
    if unique_plants is not None:
        text = f"<b>Number of Unique Plants:</b> {unique_plants}"
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 12))
    
    if common_bees is not None:
        text = "<b>Top 5 Common Bees:</b>"
        elements.append(Paragraph(text, body_style))
        elements.extend(format_common_bees(common_bees))
        elements.append(Spacer(1, 12))
    
    # Most frequently observed plant
    elements.append(Paragraph("Most Frequently Observed Plant", heading_style))
    elements.append(Spacer(1, 6))
    if common_plant is not None:
        text = f"<b>Most Frequently Observed Plant:</b> {common_plant}"
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 12))

    if common_plant_count is not None:
        text = f"<b>Number of Observations of {common_plant}:</b> {common_plant_count}"
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 12))
    
    if cp_top_bees is not None:
        text = f"<b>Top Bees Observed on {common_plant}:</b> "
        elements.append(Paragraph(text, body_style))
        elements.extend(format_common_bees(cp_top_bees))
        elements.append(Spacer(1, 12))

    # Add metadata
    doc.title = title
    doc.author = "Oregon Bee Project"
    doc.subject = "Common Bee and Plant Report"

    doc.build(elements)

    buffer.seek(0)
    return buffer
