# Intake Attrition Dashboard - Development Guide

## Project Overview
This is a Streamlit-based intake attrition risk dashboard for analyzing client risk levels, appointment history, and intervention tracking.

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python (risk scoring, data processing)
- **Data:** CSV with SQLite option
- **Analytics:** Pandas, Plotly
- **Dev Tools:** pytest, black, flake8

## Development Workflow

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run app.py
```

### Code Quality
```bash
black src/ app.py
flake8 src/ app.py
pytest
```

## Project Structure
- `app.py` - Main Streamlit application
- `src/risk_scoring.py` - Risk calculation logic
- `src/data_cleaning.py` - Data validation and cleaning
- `src/charts.py` - Plotly visualizations
- `src/data_generator.py` - Simulated data creation
- `data/` - CSV and database files

## Key Features
- Client Risk Table with filters
- Rule-based risk scoring (capped and weighted)
- Dashboard with 6 visualization charts
- Client detail pages with barrier analysis
- Role-based access planning (basic implementation)
- Encrypted client IDs (no PII)
