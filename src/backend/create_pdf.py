from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import io

from pdf_content import (
    CITATION_PARAGRAPHS,
    COMMON_SUMMARY_INTRO,
    DETAILED_REPORT_INTRO,
    DISCLAIMER_TEXT,
)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "../data/OSU-MM.png")


def _get_logo(width=3 * inch):
    """Return a centered reportlab Image of the OSU Master Melittologist logo if present."""
    if not os.path.exists(LOGO_PATH):
        return None
    try:
        from reportlab.lib.utils import ImageReader

        reader = ImageReader(LOGO_PATH)
        img_w, img_h = reader.getSize()
        if img_w <= 0 or img_h <= 0:
            return None
        aspect = img_h / img_w
        height = width * aspect
        logo = Image(LOGO_PATH, width=width, height=height)
        logo.hAlign = "CENTER"
        return logo
    except Exception:
        return None


def _make_styles():
    s = getSampleStyleSheet()
    body = ParagraphStyle("PdfBody", parent=s["BodyText"], wordWrap="CJK")
    bold_body = ParagraphStyle("PdfBoldBody", parent=s["BodyText"], fontName="Helvetica-Bold", wordWrap="CJK")
    small = ParagraphStyle("PdfSmall", parent=s["BodyText"], fontSize=8, wordWrap="CJK")
    center = ParagraphStyle("PdfCenter", parent=s["BodyText"], alignment=1)
    return s, body, bold_body, small, center


def _build_context_block(description, styles):
    """Return flowables with a context blurb and disclaimer."""
    s = styles
    context_style = ParagraphStyle(
        "PdfContext", parent=s["BodyText"], fontSize=9, leading=13,
        textColor=colors.HexColor("#333333"), wordWrap="CJK",
    )
    disclaimer_style = ParagraphStyle(
        "PdfDisclaimer", parent=s["BodyText"], fontSize=9, leading=13,
        textColor=colors.orangered, fontName="Helvetica-Oblique", wordWrap="CJK",
        backColor=colors.HexColor("#FFF7ED"), borderPadding=6,
    )
    elements = []
    elements.append(Paragraph(description, context_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(DISCLAIMER_TEXT, disclaimer_style))
    elements.append(Spacer(1, 16))
    return elements


def _build_citations_block(styles):
    """Acknowledgments and funding citations at end of report."""
    s = styles
    heading_style = ParagraphStyle(
        "PdfCitationsHeading", parent=s["Heading2"], fontSize=12, spaceAfter=8,
    )
    citation_style = ParagraphStyle(
        "PdfCitation", parent=s["BodyText"], fontSize=8, leading=11,
        fontName="Helvetica-Oblique", textColor=colors.grey, wordWrap="CJK",
        spaceAfter=8,
    )
    elements = [
        Paragraph("Acknowledgments", heading_style),
    ]
    for paragraph in CITATION_PARAGRAPHS:
        elements.append(Paragraph(paragraph, citation_style))
    return elements


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

    # Front matter: logo, title, how to read this summary
    logo = _get_logo(width=1.75 * inch)
    if logo:
        elements.append(logo)
        elements.append(Spacer(1, 0.15 * inch))

    title_style = ParagraphStyle(
        "CommonTitle", parent=s["Title"], fontSize=18, leading=22, alignment=1,
    )
    elements.append(Paragraph(f"{title} — {location}", title_style))
    elements.append(Spacer(1, 12))

    elements.extend(_build_context_block(COMMON_SUMMARY_INTRO, s))

    # Extract data
    num_rows_value = None
    unique_bees = None
    unique_plants = None
    common_bees = None
    common_plant = None
    common_plant_count = None
    cp_top_bees = None
    common_plant_sci = None

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
        elif metric == "mostCommonPlant.iNatTaxonName":
            common_plant_sci = value
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
        plant_label = common_plant
        if common_plant_sci and common_plant_sci != common_plant:
            plant_label = f"{common_plant} (<i>{common_plant_sci}</i>)"
        elements.append(Paragraph(f"<b>Most Frequently Observed Plant:</b> {plant_label}", body_style))
        elements.append(Spacer(1, 12))
    if common_plant_count is not None:
        elements.append(Paragraph(f"<b>Number of Observations of {common_plant}:</b> {common_plant_count}", body_style))
        elements.append(Spacer(1, 12))
    if cp_top_bees is not None:
        elements.append(Paragraph(f"<b>Top Bees Observed on {common_plant}:</b>", body_style))
        elements.extend(format_common_bees(cp_top_bees, body_style))
        elements.append(Spacer(1, 12))

    # End matter: citations
    elements.append(PageBreak())
    elements.append(KeepTogether(_build_citations_block(s)))

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
    logo = _get_logo(width=3 * inch)
    if logo:
        doc_elements.append(Spacer(1, page_h * 0.2))
        doc_elements.append(logo)
        doc_elements.append(Spacer(1, 0.4 * inch))

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
    doc_elements.append(Spacer(1, 0.2 * inch))
    doc_elements.append(Paragraph(location, cover_sub_style))
    doc_elements.append(Spacer(1, 0.3 * inch))

    summary_fields = [
        ("Total Observations", stats.get("numRows")),
        ("Unique Bee Species", stats.get("numUniqueBees")),
        ("Unique Plant Species", stats.get("numUniquePlants")),
        ("Males Observed", stats.get("totalMales")),
        ("Females Observed", stats.get("totalFemales")),
    ]
    for label, value in summary_fields:
        if value is not None:
            doc_elements.append(Paragraph(f"{label}: <b>{value}</b>", cover_meta_style))
            doc_elements.append(Spacer(1, 4))

    doc_elements.append(Spacer(1, 0.3 * inch))
    doc_elements.append(Paragraph("Oregon Bee Project", cover_meta_style))

    doc_elements.append(PageBreak())

    # --- Heatmap page (if data available) ---
    if filtered_df is not None:
        try:
            import detailed_report as dr
            heatmap_png = dr.heatmap_as_image(filtered_df)
            if heatmap_png:
                heatmap_img = Image(io.BytesIO(heatmap_png), width=7 * inch, height=4.5 * inch)
                heatmap_img.hAlign = "CENTER"
                doc_elements.append(Spacer(1, 0.3 * inch))
                doc_elements.append(Paragraph("Observation Density Map", s["Heading2"]))
                doc_elements.append(Spacer(1, 0.15 * inch))
                doc_elements.append(heatmap_img)
                doc_elements.append(PageBreak())
        except Exception:
            pass

    doc_elements.extend(_build_context_block(DETAILED_REPORT_INTRO, s))

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
