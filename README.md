# Facility Assessment Report Generator

## Overview

This is a Python/Streamlit application for building a facility-level assessment snapshot from CMS datasets and a small set of optional manual inputs. The app looks up a nursing facility by CCN, pulls provider profile data and claims-based quality measures from CMS datasets, then assembles a formatted report that can be reviewed in the browser or exported as Word and PDF documents.

The web application provides a page for the user to enter a valid 6-digit CCN, add contextual fields such as EMR, current census, patient type, and MedElite history, then fetch the report. It stores the resulting report in the Streamlit session state so the user can review the dashboard and download the generated files without repeating the lookup.

### How To Use The Application

1. Open the following link: https://facility-assessment-report-generator-070i.onrender.com/
2. Enter a 6-digit CCN.
3. Optionally override the facility name.
4. Fill in the manual fields for EMR, current census, patient type, previous coverage, previous provider performance, and medical coverage.
5. Select **Fetch Facility Data**.
6. Over the course of a few seconds, the application will build the .pdf and .docx files and provide download buttons.
7. Review the performance dashboard and download the generated PDF or Word report.

## Tech Stack & Override Logic

The technical stack is as follows: 
- Language: Python
- UI: Streamlit
- CMS API Calls: Requests API
- PDF Export: Reportlab
- Word Export: python-docx
- Testing: Pytest and Github Actions
## Core Architectural Design Decisions

The application is split into four main modules:

1. `Hosting/` handles the UI, form validation, session state, and download actions.
2. `API/` contains the CMS data clients that query and cache remote records.
3. `FileExport/` renders the final report into DOCX and PDF formats.
4. `Testing/` to house unit tests for the rest of the application.

## Data Flow Diagram

<img width="759" height="925" alt="Screenshot 2026-06-23 153524" src="https://github.com/user-attachments/assets/7e11afea-3051-433f-b343-242d7c5cde87" />

## Engineering Assumptions

Some engineering assumptions in this implementation are:

- The CMS dataset contracts are stable: provider fields and claims fields used by the app keep the same names and meanings over time.
- Users will supply business-context inputs (EMR, patient type, prior coverage/performance, medical coverage) accurately; these are not CMS-derived.
  - For invalid CCN inputs, the application will specify the input format for the user.
  - In the event of other invalid or empty inputs, that cell will be populated by a fallback value such as "N/A"
- Plaintext will suffice for company branding. Were that not the case, appending the logo as an image and using custom fonts/color schemes would be the next step of app implementation.
- Runtime environments running this app are expected to have network access to CMS APIs and dependencies installed for both exports (especially ReportLab for PDF generation).
- All data required by the application will be found in:
  - CMS Provider Info Dataset
  - CMS Claims Quality Measure Dataset
  - Manual user input through the webpage
- Data security measures such as encoding or backups are not required for an initial implementation.

## API Endpoints Queried

We will have to query the CMS Provider Info dataset (https://data.cms.gov/provider-data/dataset/4pq5-n9py) for the following features:
- location (provider_name)
- name of facility (provider_address)
- census capacity (number_of_certified_beds)
- overall star rating (overall_rating)
- Health Inspection (health_inspection_rating)
- Staffing (staffing_rating)
- Quality of Resident Care (qm_rating)

For the Hospitalization/ED metrics, we query by measure_code from the CMS Claims Quality Measure dataset (https://data.cms.gov/provider-data/dataset/ijh5-nb2v):
- "521": for short-term hospitalization metrics
- "522": for short-term ED metrics
- "551": for long-term hospitalization metrics
- "552": for long-term ED metrics

We will need manual input for:
- EMR
- current census
- type of patient
- medelite history (previous coverage from medelite)
- medical coverage
- Previous Provider Performance from Medelite

## Quick-Start Local Development Guide

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
streamlit run Hosting/streamlit_client.py
```

### 5. Testing
Unit tests are run automatically upon commit, though they have been provided in the `Testing\` module. 

- test_file_export_api.py validates:
  - Data is retrieved correctly from CMS Provider Info and Claims Quality Measure APIs
  - Data from datasets and user input are merged and processed properly for the generated report
  - Empty/invalid inputs are given correct fallback values
- test_streamlit_client.py validates:
  - Correct structure of exported report
  - Normalization of manual user inputs
  - Proper construction of facility addresses

## Notes

- `main.py` is only a thin entry point; all application logic starts in `Hosting/streamlit_client.py`.
- If you change the report schema in the API layer, update both export modules so the DOCX and PDF output stay in sync with the dashboard.
- If ReportLab is unavailable in a local environment, install the dependencies from `requirements.txt` before trying to use PDF export.
- The app uses the official legal name from the CMS API by default. However, if the user enters a custom name, it will override the official legal name on the final output.
