from API.cms_api_claims_quality_measure import CMS_API_Claims_Quality_Measure_Client
from API.cms_provider_info_client import CMS_Provider_Info_Client
from FileExport.python_docx_client import build_docx_export
from FileExport.reportlab_client import build_pdf_export

import streamlit as st

PROVIDER_DATASET_ID = "4pq5-n9py"
CLAIMS_DATASET_ID = "ijh5-nb2v"

def normalize_ccn(raw_ccn):
    """
    Handles ccn input and validates input
    """
    ccn_text = str(raw_ccn).strip()
    if not ccn_text.isdigit() or len(ccn_text) != 6:
        raise ValueError("CCN must be a 6-digit numeric value.")
    return ccn_text

def display_value(value, fallback="N/A"):
    """
    Displays a value or returns a fallback if the value is None or empty.
    """
    if value in (None, ""):
        return fallback
    return str(value)

def normalize_numeric_input(raw_value):
    numeric_text = str(raw_value).strip()
    if not numeric_text:
        return None
    try:
        return int(numeric_text)
    except ValueError as exc:
        raise ValueError("Input must be a whole number.") from exc

def build_location_line(address, city, state):
    """
    Append address, city, and state
    """
    address_text = display_value(address)
    city_text = str(city).strip() if city not in (None, "") else ""
    state_text = str(state).strip() if state not in (None, "") else ""
    if address_text == "N/A":
        return address_text
    parts = [address_text]
    if city_text and city_text not in address_text:
        parts.append(city_text)
    if state_text and state_text not in address_text:
        parts.append(state_text)
    if len(parts) > 1:
        return ", ".join(parts)
    return address_text

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_report_data(ccn_text, custom_name, emr, current_census, patient_type, previous_coverage, previous_provider_performance, medical_coverage):
    """
    Build both caches for a given ccn and return all the data used in the report
    """
    provider_client = CMS_Provider_Info_Client(PROVIDER_DATASET_ID)
    provider_client.build_cache(ccn_text, limit=1)

    claims_client = CMS_API_Claims_Quality_Measure_Client(CLAIMS_DATASET_ID)
    claims_client.build_cache(ccn_text, limit=100)

    official_name = provider_client.get_facility_name_from_cache()
    facility_name = custom_name.strip() or official_name

    return {
        "ccn": ccn_text,
        "state": provider_client.get_state_from_cache(),
        "city": provider_client.get_city_from_cache(),
        "facility_name": facility_name,
        "facility_address": provider_client.get_facility_location_from_cache(),
        "location": build_location_line(
            provider_client.get_facility_location_from_cache(),
            provider_client.get_city_from_cache(),
            provider_client.get_state_from_cache(),
        ),
        "census_capacity": provider_client.get_census_capacity_from_cache(),
        "emr": emr.strip(),
        "current_census": current_census,
        "patient_type": patient_type.strip(),
        "previous_coverage": previous_coverage,
        "previous_provider_performance": previous_provider_performance.strip(),
        "medical_coverage": medical_coverage.strip(),
        "overall_rating": provider_client.get_overall_star_rating_from_cache(),
        "health_inspection_rating": provider_client.get_health_inspection_rating_from_cache(),
        "staffing_rating": provider_client.get_staffing_rating_from_cache(),
        "quality_of_resident_care_rating": provider_client.get_quality_of_resident_care_rating_from_cache(),
        "claims_summary": {
            "str_hosp_score": claims_client.get_str_hosp_score_from_cache(),
            "str_hosp_state_avg": claims_client.get_str_hosp_state_avg_from_cache(),
            "str_hosp_national_avg": claims_client.get_str_hosp_national_avg_from_cache(),
            "str_ed_score": claims_client.get_str_ed_score_from_cache(),
            "str_ed_state_avg": claims_client.get_str_ed_state_avg_from_cache(),
            "str_ed_national_avg": claims_client.get_str_ed_national_avg_from_cache(),
            "lt_hosp_score": claims_client.get_lt_hosp_score_from_cache(),
            "lt_hosp_state_avg": claims_client.get_lt_hosp_state_avg_from_cache(),
            "lt_hosp_national_avg": claims_client.get_lt_hosp_national_avg_from_cache(),
            "lt_ed_score": claims_client.get_lt_ed_score_from_cache(),
            "lt_ed_state_avg": claims_client.get_lt_ed_state_avg_from_cache(),
            "lt_ed_national_avg": claims_client.get_lt_ed_national_avg_from_cache(),
        },
    }

def report_rows(report_data):
    claims = report_data["claims_summary"]
    return [
        {"Field": "Name of Facility", "Value": display_value(report_data["facility_name"])},
        {"Field": "CCN", "Value": display_value(report_data["ccn"])},
        {"Field": "State", "Value": display_value(report_data["state"])},
        {"Field": "Location", "Value": display_value(report_data["location"])},
        {"Field": "EMR", "Value": display_value(report_data.get("emr"))},
        {"Field": "Census Capacity", "Value": display_value(report_data["census_capacity"])},
        {"Field": "Current Census", "Value": display_value(report_data.get("current_census"))},
        {"Field": "Type of Patient", "Value": display_value(report_data.get("patient_type"))},
        {"Field": "Previous Coverage from MedElite", "Value": display_value(report_data.get("previous_coverage"))},
        {"Field": "Previous Provider Performance from MedElite", "Value": display_value(report_data.get("previous_provider_performance"))},
        {"Field": "Medical Coverage", "Value": display_value(report_data.get("medical_coverage"))},
        {"Field": "Overall Star Rating", "Value": display_value(report_data["overall_rating"])},
        {"Field": "Health Inspection", "Value": display_value(report_data["health_inspection_rating"])},
        {"Field": "Staffing", "Value": display_value(report_data["staffing_rating"])},
        {"Field": "Quality of Resident Care", "Value": display_value(report_data["quality_of_resident_care_rating"])},
        {"Field": "Short Term Hospitalization", "Value": display_value(claims["str_hosp_score"])},
        {"Field": "STR National Avg. for Hospitalization", "Value": display_value(claims["str_hosp_national_avg"])},
        {"Field": "STR State National Avg. for Hospitalization", "Value": display_value(claims["str_hosp_state_avg"])},
        {"Field": "Short Term ED Visit", "Value": display_value(claims["str_ed_score"])},
        {"Field": "STR ED Visits National Avg.", "Value": display_value(claims["str_ed_national_avg"])},
        {"Field": "STR ED Visits State Avg.", "Value": display_value(claims["str_ed_state_avg"])},
        {"Field": "LT Hospitalization", "Value": display_value(claims["lt_hosp_score"])},
        {"Field": "LT National Avg. for Hospitalization", "Value": display_value(claims["lt_hosp_national_avg"])},
        {"Field": "LT State National Avg. for Hospitalization", "Value": display_value(claims["lt_hosp_state_avg"])},
        {"Field": "ED Visit", "Value": display_value(claims["lt_ed_score"])},
        {"Field": "LT ED Visits National Avg.", "Value": display_value(claims["lt_ed_national_avg"])},
        {"Field": "LT ED Visits State Avg.", "Value": display_value(claims["lt_ed_state_avg"])},
    ]

def run_app():
    """
    Build webpage with Streamlit, build pdf and docx if submit button is pressed
    """
    st.set_page_config(page_title="Facility Assessment Snapshot", page_icon="🏥", layout="wide")
    st.markdown(
        """
        <style>
            :root {
                color-scheme: light;
            }
            .stApp {
                background: #FFFFFF;
                color: #000000;
            }
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            #MainMenu,
            footer {
                visibility: hidden;
                height: 0;
            }
            .block-container {
                max-width: 1180px;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiSelect div[data-baseweb="select"] > div {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border-color: #B8B8B8 !important;
            }
            .stTextInput input::placeholder,
            .stNumberInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: #666666 !important;
                opacity: 1;
            }
            div[data-testid="stFormSubmitButton"] button,
            div[data-testid="stButton"] button,
            div[data-testid="stDownloadButton"] button,
            button[kind="primary"],
            button[kind="secondary"] {
                background-color: #111111 !important;
                color: #FFFFFF !important;
                border: 1px solid #111111 !important;
            }
            .brand-banner {
                text-align: center;
                font-size: 1.2rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                color: #000000;
                text-transform: uppercase;
                margin-bottom: 0.15rem;
            }
            .brand-title {
                text-align: center;
                font-size: 1.6rem;
                font-weight: 800;
                color: #000000;
                margin-bottom: 0.25rem;
            }
            .brand-state {
                text-align: center;
                font-size: 1rem;
                font-weight: 700;
                color: #000000;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="brand-banner">INFINITE — Managed by MEDELITE</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-title">FACILITY ASSESSMENT SNAPSHOT</div>', unsafe_allow_html=True)

    if "report_data" not in st.session_state:
        st.session_state.report_data = None
    if "lookup_error" not in st.session_state:
        st.session_state.lookup_error = None

    with st.form("facility_lookup_form"):
        st.subheader("Manual Inputs")
        ccn_input = st.text_input("CCN", placeholder="Enter a 6-digit CMS Certification Number")
        custom_name = st.text_input("Facility Name Override (optional)", placeholder="Leave blank to use the CMS legal name")
        emr = st.text_input("EMR", placeholder="Enter EMR")
        current_census_input = st.text_input("Current Census", placeholder="Enter a whole number")
        patient_type = st.text_input("Type of Patient", placeholder="Enter type of patient")
        previous_coverage = st.selectbox("Previous Coverage from MedElite", options=("Yes", "No"))
        previous_provider_performance = st.text_input("Previous Provider Performance from MedElite", placeholder="Enter prior provider performance notes")
        medical_coverage = st.text_input("Medical Coverage", placeholder="Enter medical coverage")
        fetch_clicked = st.form_submit_button("Fetch Facility Data")

    if fetch_clicked:
        try:
            normalized_ccn = normalize_ccn(ccn_input)
            st.session_state.report_data = fetch_report_data(
                normalized_ccn,
                custom_name,
                emr,
                normalize_numeric_input(current_census_input),
                patient_type,
                previous_coverage,
                previous_provider_performance,
                medical_coverage,
            )
            st.session_state.lookup_error = None
        except Exception as exc:  # noqa: BLE001
            st.session_state.report_data = None
            st.session_state.lookup_error = str(exc)

    if st.session_state.lookup_error:
        st.error(st.session_state.lookup_error)

    if st.session_state.report_data:
        report_data = st.session_state.report_data
        st.markdown(f'<div class="brand-state">{display_value(report_data["state"])}</div>', unsafe_allow_html=True)
        st.table(report_rows(report_data))

        docx_bytes = build_docx_export(report_data)
        pdf_bytes = build_pdf_export(report_data)

        download_cols = st.columns(2)
        with download_cols[0]:
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"facility_assessment_{report_data['ccn']}.pdf",
                mime="application/pdf",
                type="primary",
            )
        with download_cols[1]:
            st.download_button(
                label="Download Word",
                data=docx_bytes,
                file_name=f"facility_assessment_{report_data['ccn']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )