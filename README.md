# Facility Assessment Report Generator

## Web App Link
https://facility-assessment-report-generator-070i.onrender.com/

## Overview

This is a Python/Streamlit application for building a facility-level assessment snapshot from CMS datasets and a small set of optional manual inputs. The app looks up a nursing facility by CCN, pulls provider profile data and claims-based quality measures from CMS datasets, then assembles a formatted report that can be reviewed in the browser or exported as Word and PDF documents.

The web application provides a page for the user to enter a valid 6-digit CCN, add contextual fields such as EMR, current census, patient type, and MedElite history, then fetch the report. It stores the resulting report in the Streamlit session state so the user can review the dashboard and download the generated files without repeating the lookup.

## Core Architectural Design Decisions

The application is split into three layers:

1. `Hosting/streamlit_client.py` handles the UI, form validation, session state, and download actions.
2. `API/` contains the CMS data clients that query and cache remote records.
3. `FileExport/` renders the final report into DOCX and PDF formats.

- CMS data is fetched by CCN and cached in memory so the app can render the full report from one lookup cycle.
- Provider metadata comes from the CMS Nursing Home Provider dataset (`4pq5-n9py`), which supplies the facility name, address, city, state, bed count, and star ratings.
- Claims quality measures come from the CMS claims dataset (`ijh5-nb2v`), which is flattened into a report-friendly schema for short-term and long-term hospitalization and ED visit measures.
- The Streamlit form validates the CCN as a 6-digit numeric value and normalizes the current census as a whole number before any CMS request is made.
- The report uses a shared data structure for on-screen display and export generation, which keeps the dashboard, DOCX output, and PDF output aligned.
- The UI applies custom CSS to keep the interface branded, hide Streamlit chrome, and present the key metrics as cards instead of a plain form-only workflow.

## Engineering Assumptions

Some engineering assumptions in this implementation are:

- The CMS dataset contracts are stable: provider fields and claims fields used by the app keep the same names and meanings over time.
- A valid 6-digit CCN is enough to identify a single provider record for report generation (provider lookup uses `limit=1`).
- Claims measures are represented by a known, fixed set of measure codes (`521`, `522`, `551`, `552`) that map to the scorecard fields.
- Static fallback benchmark values for state and national averages are acceptable when CMS values are unavailable.
- Data freshness can trade off against speed: Streamlit caching with a 1-hour TTL is considered sufficient for this workflow.
- Users will supply business-context inputs (EMR, patient type, prior coverage/performance, medical coverage) accurately; these are not CMS-derived.
- Runtime environments running this app are expected to have network access to CMS APIs and dependencies installed for both exports (especially ReportLab for PDF generation).

## Tech Stack & Override Logic

The technical stack is as follows: 
- Language: Python
- UI: Streamlit
- CMS API Calls: Requests
- PDF Export: Reportlab
- Word Export: python-docx

The app uses the legal name provided by the API for any given facility (if found) by default, or if the input value is just white space. When an override value is provided, the trimmed value is used instead. 

## API Endpoints Queried

We will have to query this dataset for the following features:
https://data.cms.gov/provider-data/dataset/4pq5-n9py
- location (provider_name)
- name of facility (provider_address)
- census capacity (number_of_certified_beds)
- overall star rating (overall_rating)
- Health Inspection (health_inspection_rating)
- Staffing (staffing_rating)
- Quality of Resident Care (qm_rating)

We will need manual input for:
- EMR
- current census
- type of patient
- medelite history (previous coverage from medelite)
- medical coverage
- Previous Provider Performance from Medelite

For the Hospitalization/ED metrics, we query by measure_code from this dataset:
https://data.cms.gov/provider-data/dataset/ijh5-nb2v
- "521": for short-term hospitalization metrics
- "522": for short-term ED metrics
- "551": for long-term hospitalization metrics
- "552": for long-term ED metrics

## Quick-Start Local Installation Guide

### 1. Prerequisites

- Python 3.10 or newer
- Internet access to query CMS data endpoints
- Windows, macOS, or Linux with a terminal

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The project depends on `streamlit`, `requests`, `python-docx`, and `reportlab`.

### 4. Run the app

```bash
streamlit run main.py
```

### 5. Use the application

1. Enter a 6-digit CCN.
2. Optionally override the facility name.
3. Fill in the manual fields for EMR, current census, patient type, previous coverage, previous provider performance, and medical coverage.
4. Select **Fetch Facility Data**.
5. Review the performance dashboard and download the generated PDF or Word report.

## Data Sources

- CMS Nursing Home Provider dataset: `https://data.cms.gov/provider-data/dataset/4pq5-n9py`
- CMS claims quality measure dataset: `https://data.cms.gov/provider-data/dataset/ijh5-nb2v`

## Notes

- `main.py` is only a thin entry point; all application logic starts in `Hosting/streamlit_client.py`.
- If you change the report schema in the API layer, update both export modules so the DOCX and PDF output stay in sync with the dashboard.
- If ReportLab is unavailable in a local environment, install the dependencies from `requirements.txt` before trying to use PDF export.
