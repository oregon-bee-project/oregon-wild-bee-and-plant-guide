from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import io

LOGO_PATH = os.path.join(os.path.dirname(__file__), "../data/OSU-logo.png")


def _get_logo(width=2*inch):
    """Return a reportlab Image of the OSU logo if the file exists, else None."""
    if os.path.exists(LOGO_PATH):
        return Image(LOGO_PATH, width=width, height=width * 0.4)
    return None


def _make_styles():
    s = getSampleStyleSheet()
    body = ParagraphStyle("PdfBody", parent=s["BodyText"], wordWrap="CJK")
    bold_body = ParagraphStyle("PdfBoldBody", parent=s["BodyText"], fontName="Helvetica-Bold", wordWrap="CJK")
    small = ParagraphStyle("PdfSmall", parent=s["BodyText"], fontSize=8, wordWrap="CJK")
    center = ParagraphStyle("PdfCenter", parent=s["BodyText"], alignment=1)
    return s, body, bold_body, small, center


def format_common_bees(bees, body_style):
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
    s, body_style, bold_body_style, small_style, center_style = _make_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    # Logo header
    logo = _get_logo(width=1.8*inch)
    if logo:
        elements.append(logo)
        elements.append(Spacer(1, 6))

    # Title
    elements.append(Paragraph(f"{title} — {location}", s["Title"]))
    elements.append(Spacer(1, 12))

    # Extract data
    num_rows_value = None
    unique_bees = None
    unique_plants = None
    common_bees = None
    common_plant = None
    common_plant_count = None
    cp_top_bees = None

    for row in rows:
        metric = row.get("Metric")
        value = row.get("Value")
        if metric == "numRows":
            num_rows_value = value
        elif metric == "numUniqueBees":
            unique_bees = value
        elif metric == "numUniquePlants":
            unique_plants = value
        elif metric == "mostCommonBees":
            common_bees = value
        elif metric == "mostCommonPlant.commonName":
            common_plant = value
        elif metric == "mostCommonPlant.count":
            common_plant_count = value
        elif metric == "mostCommonPlant.topBees":
            cp_top_bees = value

    # Summary statistics
    elements.append(Paragraph("Summary Statistics", s["Heading2"]))
    elements.append(Spacer(1, 6))
    if num_rows_value is not None:
        elements.append(Paragraph(f"<b>Number of Observations:</b> {num_rows_value}", body_style))
        elements.append(Spacer(1, 12))
    if unique_bees is not None:
        elements.append(Paragraph(f"<b>Number of Unique Bees:</b> {unique_bees}", body_style))
        elements.append(Spacer(1, 12))
    if unique_plants is not None:
        elements.append(Paragraph(f"<b>Number of Unique Plants:</b> {unique_plants}", body_style))
        elements.append(Spacer(1, 12))
    if common_bees is not None:
        elements.append(Paragraph("<b>Top 5 Common Bees:</b>", body_style))
        elements.extend(format_common_bees(common_bees, body_style))
        elements.append(Spacer(1, 12))

    # Most common plant
    elements.append(Paragraph("Most Frequently Observed Plant", s["Heading2"]))
    elements.append(Spacer(1, 6))
    if common_plant is not None:
        elements.append(Paragraph(f"<b>Most Frequently Observed Plant:</b> {common_plant}", body_style))
        elements.append(Spacer(1, 12))
    if common_plant_count is not None:
        elements.append(Paragraph(f"<b>Number of Observations of {common_plant}:</b> {common_plant_count}", body_style))
        elements.append(Spacer(1, 12))
    if cp_top_bees is not None:
        elements.append(Paragraph(f"<b>Top Bees Observed on {common_plant}:</b>", body_style))
        elements.extend(format_common_bees(cp_top_bees, body_style))
        elements.append(Spacer(1, 12))

    doc.title = title
    doc.author = "Oregon Bee Project"
    doc.subject = "Common Bee and Plant Report"
    doc.build(elements)

    buffer.seek(0)
    return buffer


def generate_detailed_pdf(stats, title="Detailed Bee and Plant Report", location="Oregon", filtered_df=None):
    buffer = io.BytesIO()
    s, b_style, bold_b_style, small_style, center_style = _make_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    page_w, page_h = letter
    doc_elements = []

    # --- Cover page ---
    logo = _get_logo(width=3*inch)
    if logo:
        # Center logo vertically on the cover with spacers
        doc_elements.append(Spacer(1, page_h * 0.2))
        logo.hAlign = "CENTER"
        doc_elements.append(logo)
        doc_elements.append(Spacer(1, 0.4*inch))

    cover_title_style = ParagraphStyle(
        "CoverTitle", parent=s["Title"], fontSize=24, leading=30, alignment=1
    )
    cover_sub_style = ParagraphStyle(
        "CoverSub", parent=s["BodyText"], fontSize=14, leading=20, alignment=1
    )
    cover_meta_style = ParagraphStyle(
        "CoverMeta", parent=s["BodyText"], fontSize=11, leading=16, alignment=1, textColor=colors.grey
    )

    doc_elements.append(Paragraph(title, cover_title_style))
    doc_elements.append(Spacer(1, 0.2*inch))
    doc_elements.append(Paragraph(location, cover_sub_style))
    doc_elements.append(Spacer(1, 0.3*inch))

    summary_fields = [
        ("Total Observations", stats.get("numRows")),
        ("Unique Bee Species",  stats.get("numUniqueBees")),
        ("Unique Plant Species", stats.get("numUniquePlants")),
        ("Males Observed",      stats.get("totalMales")),
        ("Females Observed",    stats.get("totalFemales")),
    ]
    for label, value in summary_fields:
        if value is not None:
            doc_elements.append(Paragraph(f"{label}: <b>{value}</b>", cover_meta_style))
            doc_elements.append(Spacer(1, 4))

    doc_elements.append(Spacer(1, 0.3*inch))
    doc_elements.append(Paragraph("Oregon Bee Project", cover_meta_style))

    doc_elements.append(PageBreak())

    # --- Heatmap page (if data available) ---
    if filtered_df is not None:
        try:
            import detailed_report as dr
            heatmap_png = dr.heatmap_as_image(filtered_df)
            if heatmap_png:
                heatmap_img = Image(io.BytesIO(heatmap_png), width=7*inch, height=4.5*inch)
                heatmap_img.hAlign = "CENTER"
                doc_elements.append(Spacer(1, 0.3*inch))
                doc_elements.append(Paragraph("Observation Density Map", s["Heading2"]))
                doc_elements.append(Spacer(1, 0.15*inch))
                doc_elements.append(heatmap_img)
                doc_elements.append(PageBreak())
        except Exception:
            pass

    # --- Species detail pages ---
    h2_style = s["Heading2"]
    h3_style = s["Heading3"]

    doc_elements.append(Paragraph("Bee Species Detail", h2_style))
    doc_elements.append(Spacer(1, 8))

    bee_list = stats.get("beeList", [])
    for bee in bee_list:
        species_block = []
        name = bee.get("scientificName", "Unknown")
        species_block.append(Paragraph(name, h3_style))

        counts_text = (
            f"<b>Observations:</b> {bee.get('count', 0)} &nbsp;&nbsp; "
            f"<b>Male:</b> {bee.get('maleCount', 0)} &nbsp;&nbsp; "
            f"<b>Female:</b> {bee.get('femaleCount', 0)}"
        )
        species_block.append(Paragraph(counts_text, b_style))

        seasonal_text = (
            f"<b>Seasonal:</b> "
            f"Spring: {bee.get('springCount', 0)}, "
            f"Summer: {bee.get('summerCount', 0)}, "
            f"Fall: {bee.get('fallCount', 0)}, "
            f"Winter: {bee.get('winterCount', 0)}"
        )
        species_block.append(Paragraph(seasonal_text, b_style))

        top_plants = bee.get("topPlants", [])
        if top_plants:
            species_block.append(Spacer(1, 4))
            species_block.append(Paragraph("<b>Top Plants:</b>", b_style))
            for plant in top_plants:
                common = plant.get("commonName") or plant.get("scientificName") or plant.get("plantINatId", "")
                sci = plant.get("scientificName", "")
                p_count = plant.get("count", 0)
                label_parts = [f"\t• {common}"]
                if sci and sci != common:
                    label_parts.append(f" ({sci})")
                label_parts.append(f" — {p_count} obs.")
                species_block.append(Paragraph("".join(label_parts), small_style))
                species_block.append(Spacer(1, 2))

        species_block.append(Spacer(1, 10))
        doc_elements.append(KeepTogether(species_block))

    doc.title = title
    doc.author = "Oregon Bee Project"
    doc.subject = "Detailed Bee and Plant Report"
    doc.build(doc_elements)

    buffer.seek(0)
    return buffer
