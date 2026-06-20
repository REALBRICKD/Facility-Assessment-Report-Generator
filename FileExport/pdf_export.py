from importlib import import_module
from io import BytesIO

try:
    reportlab_lib = import_module("reportlab.lib")
    enums_module = import_module("reportlab.lib.enums")
    pagesizes_module = import_module("reportlab.lib.pagesizes")
    styles_module = import_module("reportlab.lib.styles")
    units_module = import_module("reportlab.lib.units")
    platypus_module = import_module("reportlab.platypus")
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    reportlab_lib = None
    enums_module = None
    pagesizes_module = None
    styles_module = None
    units_module = None
    platypus_module = None

PDF_EXPORT_AVAILABLE = all(
    module is not None
    for module in (
        reportlab_lib,
        enums_module,
        pagesizes_module,
        styles_module,
        units_module,
        platypus_module,
    )
)

def _display_value(value, fallback="N/A"):
    if value in (None, ""):
        return fallback
    return str(value)

def _build_rows(report_data):
    claims = report_data["claims_summary"]
    return [
        ("Name of Facility", report_data.get("facility_name")),
        ("CCN", report_data.get("ccn")),
        ("State", report_data.get("state")),
        ("Location", report_data.get("location")),
        ("EMR", report_data.get("emr")),
        ("Census Capacity", report_data.get("census_capacity")),
        ("Current Census", report_data.get("current_census")),
        ("Type of Patient", report_data.get("patient_type")),
        ("Previous Coverage from MedElite", report_data.get("previous_coverage")),
        ("Previous Provider Performance from MedElite", report_data.get("previous_provider_performance")),
        ("Medical Coverage", report_data.get("medical_coverage")),
        ("Overall Star Rating", report_data.get("overall_rating")),
        ("Health Inspection", report_data.get("health_inspection_rating")),
        ("Staffing", report_data.get("staffing_rating")),
        ("Quality of Resident Care", report_data.get("quality_of_resident_care_rating")),
        ("Short Term Hospitalization", claims.get("str_hosp_score")),
        ("STR National Avg. for Hospitalization", claims.get("str_hosp_national_avg")),
        ("STR State National Avg. for Hospitalization", claims.get("str_hosp_state_avg")),
        ("Short Term ED Visit", claims.get("str_ed_score")),
        ("STR ED Visits National Avg.", claims.get("str_ed_national_avg")),
        ("STR ED Visits State Avg.", claims.get("str_ed_state_avg")),
        ("LT Hospitalization", claims.get("lt_hosp_score")),
        ("LT National Avg. for Hospitalization", claims.get("lt_hosp_national_avg")),
        ("LT State National Avg. for Hospitalization", claims.get("lt_hosp_state_avg")),
        ("ED Visit", claims.get("lt_ed_score")),
        ("LT ED Visits National Avg.", claims.get("lt_ed_national_avg")),
        ("LT ED Visits State Avg.", claims.get("lt_ed_state_avg")),
    ]

def build_pdf_export(report_data):
    if not PDF_EXPORT_AVAILABLE:
        raise RuntimeError("PDF export requires the 'reportlab' package. Install dependencies from requirements.txt.")

    colors = reportlab_lib.colors
    TA_CENTER = enums_module.TA_CENTER
    letter = pagesizes_module.letter
    ParagraphStyle = styles_module.ParagraphStyle
    getSampleStyleSheet = styles_module.getSampleStyleSheet
    inch = units_module.inch
    Paragraph = platypus_module.Paragraph
    SimpleDocTemplate = platypus_module.SimpleDocTemplate
    Spacer = platypus_module.Spacer
    Table = platypus_module.Table
    TableStyle = platypus_module.TableStyle

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    banner_style = ParagraphStyle(
        "Banner",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=4,
    )
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=4,
    )
    state_style = ParagraphStyle(
        "StateLine",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=14,
    )

    header_state = _display_value(report_data.get("state"))
    table_data = [[label, _display_value(value)] for label, value in _build_rows(report_data)]

    table = Table(table_data, colWidths=[2.7 * inch, 4.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story = [
        Paragraph("INFINITE — Managed by MEDELITE", banner_style),
        Paragraph("FACILITY ASSESSMENT SNAPSHOT", title_style),
        Paragraph(header_state, state_style),
        Spacer(1, 0.08 * inch),
        table,
    ]
    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()