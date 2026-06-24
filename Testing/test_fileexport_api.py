"""
Tests for file export API clients and CMS API client.
"""

import io
import zipfile
import xml.etree.ElementTree as ET
import types
import pytest

from FileExport import reportlab_pdf_client as pdf_client
from FileExport import python_docx_client as docx_client


def make_minimal_report():
    return {
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


def test_build_docx_export_returns_bytes():
    data = make_minimal_report()
    b = docx_client.build_docx_export(data)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 0


def test_build_docx_export_includes_care_compare_hyperlink():
    data = make_minimal_report()
    b = docx_client.build_docx_export(data)

    with zipfile.ZipFile(io.BytesIO(b)) as docx_package:
        relationships = ET.fromstring(docx_package.read("word/_rels/document.xml.rels"))

    targets = [
        rel.attrib["Target"]
        for rel in relationships
        if rel.attrib.get("Type") == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
    ]

    assert "https://www.medicare.gov/care-compare/details/nursing-home/123456" in targets


def test_build_docx_export_uses_helvetica_font():
    data = make_minimal_report()
    b = docx_client.build_docx_export(data)

    with zipfile.ZipFile(io.BytesIO(b)) as docx_package:
        document_xml = docx_package.read("word/document.xml")

    assert b"Helvetica" in document_xml


def test_build_pdf_export_returns_bytes():
    data = make_minimal_report()
    b = pdf_client.build_pdf_export(data)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 0


from API import cms_api_claims_quality_measure as claims_mod


def test_parse_vertical_results_formats_and_preserves_str():
    client = claims_mod.CMS_API_Claims_Quality_Measure_Client("dummy")
    # provide rows with numeric and non-numeric adjusted_score
    rows = [
        {"measure_code": "521", "adjusted_score": "25.58"},
        {"measure_code": "522", "adjusted_score": "abc"},
        {"measure_code": "551", "adjusted_score": None},
    ]
    parsed = client._parse_vertical_results(rows)
    assert parsed["str_hosp_score"] == "25.58"
    assert parsed["str_ed_score"] == "abc"
    # fallback keys exist
    assert "lt_hosp_score" in parsed


def test_get_empty_fallback_contains_expected_keys():
    client = claims_mod.CMS_API_Claims_Quality_Measure_Client("dummy")
    fb = client._get_empty_fallback()
    expected = [
        "str_hosp_score",
        "str_hosp_state_avg",
        "str_hosp_national_avg",
        "lt_ed_national_avg",
    ]
    for k in expected:
        assert k in fb


def test_cms_api_client_build_cache_monkeypatched(monkeypatch):
    from API import cms_api_client

    class DummyResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"results": [{"provider_name": "X"}]}

    def fake_post(url, json, timeout):
        return DummyResp()

    monkeypatch.setattr("requests.post", fake_post)
    client = cms_api_client.CMS_API_Client("d")
    client.build_cache("123456", limit=1)
    assert client._record_cache.get("provider_name") == "X"


def test_claims_build_cache_computes_state_benchmarks(monkeypatch):
    from API import cms_api_claims_quality_measure as claims_mod_local

    class DummyResp:
        def __init__(self, results):
            self._results = results

        def raise_for_status(self):
            return None

        def json(self):
            return {"results": self._results}

    facility_rows = [
        {"measure_code": "521", "adjusted_score": "28.910176", "state": "OH"},
        {"measure_code": "522", "adjusted_score": "11.824824", "state": "OH"},
        {"measure_code": "551", "adjusted_score": "", "state": "OH"},
        {"measure_code": "552", "adjusted_score": "", "state": "OH"},
    ]

    state_rows = {
        "521": [
            {"measure_code": "521", "adjusted_score": "10", "state": "OH"},
            {"measure_code": "521", "adjusted_score": "14", "state": "OH"},
        ],
        "522": [
            {"measure_code": "522", "adjusted_score": "8", "state": "OH"},
            {"measure_code": "522", "adjusted_score": "12", "state": "OH"},
        ],
        "551": [
            {"measure_code": "551", "adjusted_score": "1", "state": "OH"},
            {"measure_code": "551", "adjusted_score": "3", "state": "OH"},
        ],
        "552": [
            {"measure_code": "552", "adjusted_score": "0.5", "state": "OH"},
            {"measure_code": "552", "adjusted_score": "1.5", "state": "OH"},
        ],
    }

    national_rows = {
        "521": [
            {"measure_code": "521", "adjusted_score": "10", "state": "OH"},
            {"measure_code": "521", "adjusted_score": "14", "state": "FL"},
            {"measure_code": "521", "adjusted_score": "18", "state": "TX"},
        ],
        "522": [
            {"measure_code": "522", "adjusted_score": "8", "state": "OH"},
            {"measure_code": "522", "adjusted_score": "12", "state": "FL"},
            {"measure_code": "522", "adjusted_score": "16", "state": "TX"},
        ],
        "551": [
            {"measure_code": "551", "adjusted_score": "1", "state": "OH"},
            {"measure_code": "551", "adjusted_score": "3", "state": "FL"},
            {"measure_code": "551", "adjusted_score": "5", "state": "TX"},
        ],
        "552": [
            {"measure_code": "552", "adjusted_score": "0.5", "state": "OH"},
            {"measure_code": "552", "adjusted_score": "1.5", "state": "FL"},
            {"measure_code": "552", "adjusted_score": "2.5", "state": "TX"},
        ],
    }

    def fake_post(url, json, timeout):
        conditions = json["conditions"]
        facility_ccn = next((c["value"] for c in conditions if c["property"] == "cms_certification_number_ccn"), None)
        state = next((c["value"] for c in conditions if c["property"] == "state"), None)
        measure_code_condition = next((c["value"] for c in conditions if c["property"] == "measure_code"), None)

        if facility_ccn == "725000":
            return DummyResp(facility_rows)
        if state == "OH" and measure_code_condition:
            return DummyResp(state_rows["521"] + state_rows["522"] + state_rows["551"] + state_rows["552"])
        if measure_code_condition:
            return DummyResp(national_rows["521"] + national_rows["522"] + national_rows["551"] + national_rows["552"])

        return DummyResp([])

    monkeypatch.setattr("requests.post", fake_post)
    client = claims_mod_local.CMS_API_Claims_Quality_Measure_Client("dummy")
    client.build_cache("725000", limit=4)

    assert client.get_str_hosp_score_from_cache() == "28.91"
    assert client.get_lt_hosp_score_from_cache() == "N/A"
    assert client.get_str_hosp_state_avg_from_cache() == "12.00"
    assert client.get_lt_hosp_state_avg_from_cache() == "2.00"
    assert client.get_lt_ed_state_avg_from_cache() == "1.00"
