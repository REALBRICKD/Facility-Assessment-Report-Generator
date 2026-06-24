"""
Tests for Hosting.streamlit_client module.
"""

import sys
import types
import pytest

# Insert lightweight stubs for modules imported at top-level in streamlit_client
pkg = types.ModuleType("FileExport.reportlab_pdf_client")
pkg.build_pdf_export = lambda data: b"pdf"
sys.modules["FileExport.reportlab_pdf_client"] = pkg

pkg2 = types.ModuleType("FileExport.python_docx_client")
pkg2.build_docx_export = lambda data: b"docx"
sys.modules["FileExport.python_docx_client"] = pkg2

# Also provide legacy/alternate module name if referenced
pkg3 = types.ModuleType("FileExport.reportlab_client")
pkg3.build_pdf_export = lambda data: b"pdf"
sys.modules["FileExport.reportlab_client"] = pkg3

# Minimal API client stubs
api1 = types.ModuleType("API.cms_provider_info_client")
class DummyProv:
    def __init__(self, *a, **k):
        pass
    def build_cache(self, *a, **k):
        return None
    def get_facility_name_from_cache(self):
        return "Official Name"
    def get_state_from_cache(self):
        return "ST"
    def get_city_from_cache(self):
        return "City"
    def get_facility_location_from_cache(self):
        return "123 Main St"
    def get_census_capacity_from_cache(self):
        return 100
    def get_overall_star_rating_from_cache(self):
        return 4
    def get_health_inspection_rating_from_cache(self):
        return 5
    def get_staffing_rating_from_cache(self):
        return 3
    def get_quality_of_resident_care_rating_from_cache(self):
        return 4
api1.CMS_Provider_Info_Client = DummyProv
sys.modules["API.cms_provider_info_client"] = api1

api2 = types.ModuleType("API.cms_api_claims_quality_measure")
class DummyClaims:
    def __init__(self, *a, **k):
        pass
    def build_cache(self, *a, **k):
        return None
    def get_str_hosp_score_from_cache(self):
        return 1
    def get_str_hosp_state_avg_from_cache(self):
        return 2
    def get_str_hosp_national_avg_from_cache(self):
        return 3
    def get_str_ed_score_from_cache(self):
        return 4
    def get_str_ed_state_avg_from_cache(self):
        return 5
    def get_str_ed_national_avg_from_cache(self):
        return 6
    def get_lt_hosp_score_from_cache(self):
        return 7
    def get_lt_hosp_state_avg_from_cache(self):
        return 8
    def get_lt_hosp_national_avg_from_cache(self):
        return 9
    def get_lt_ed_score_from_cache(self):
        return 10
    def get_lt_ed_state_avg_from_cache(self):
        return 11
    def get_lt_ed_national_avg_from_cache(self):
        return 12
api2.CMS_API_Claims_Quality_Measure_Client = DummyClaims
sys.modules["API.cms_api_claims_quality_measure"] = api2

from Hosting import streamlit_client as sc


def test_normalize_ccn_valid():
    assert sc.normalize_ccn(" 123456 ") == "123456"


@pytest.mark.parametrize("bad", ["abc123", "12345", "1234567", "12 3456"]) 
def test_normalize_ccn_invalid(bad):
    with pytest.raises(ValueError):
        sc.normalize_ccn(bad)


def test_display_value_none_and_empty():
    assert sc.display_value(None) == "N/A"
    assert sc.display_value("") == "N/A"
    assert sc.display_value(0) == "0"


def test_normalize_numeric_input():
    assert sc.normalize_numeric_input("") is None
    assert sc.normalize_numeric_input(" 42 ") == 42
    with pytest.raises(ValueError):
        sc.normalize_numeric_input("3.14")


def test_build_location_line_address_na():
    # address None -> display_value returns N/A -> build_location_line returns N/A
    assert sc.build_location_line(None, "City", "ST") == "N/A"


def test_build_location_line_with_city_state():
    out = sc.build_location_line("123 Main St", "Anytown", "CA")
    assert out == "123 Main St, Anytown, CA"


def test_build_location_line_address_contains_city():
    out = sc.build_location_line("123 Main St, Anytown", "Anytown", "CA")
    assert out == "123 Main St, Anytown, CA"


def test_metric_card_html():
    html = sc.metric_card_html("Label", "Value", "Sublabel")
    assert "metric-card" in html
    assert "Label" in html and "Value" in html and "Sublabel" in html


def test_report_rows_basic():
    # minimal report data structure required by report_rows
    report_data = {
        "facility_name": "Fac",
        "ccn": "123456",
        "state": "ST",
        "location": "123 Main St, Anytown, CA",
        "emr": "EMR1",
        "census_capacity": 100,
        "current_census": 50,
        "patient_type": "Skilled",
        "previous_coverage": "Yes",
        "previous_provider_performance": "Good",
        "medical_coverage": "Med",
        "overall_rating": 4,
        "health_inspection_rating": 5,
        "staffing_rating": 3,
        "quality_of_resident_care_rating": 4,
        "claims_summary": {
            "str_hosp_score": 1,
            "str_hosp_state_avg": 2,
            "str_hosp_national_avg": 3,
            "str_ed_score": 4,
            "str_ed_state_avg": 5,
            "str_ed_national_avg": 6,
            "lt_hosp_score": 7,
            "lt_hosp_state_avg": 8,
            "lt_hosp_national_avg": 9,
            "lt_ed_score": 10,
            "lt_ed_state_avg": 11,
            "lt_ed_national_avg": 12,
        },
    }

    rows = sc.report_rows(report_data)
    assert isinstance(rows, list)

    # helper to find a value by field
    by_field = {r["Field"]: r["Value"] for r in rows}
    assert by_field["Name of Facility"] == "Fac"
    assert by_field["CCN"] == "123456"
    assert by_field["Short Term Hospitalization"] == "1"
