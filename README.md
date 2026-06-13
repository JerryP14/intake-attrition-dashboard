# Intake Attrition Risk Dashboard

A Streamlit-based dashboard for analyzing client intake attrition risk, appointment history, and intervention planning.

## Features

- **Client Risk Table**: View all clients with risk scores, categories, and follow-up status
- **Risk Score Calculator**: Rule-based scoring with weighted factors and caps
- **Dashboard Charts**: Visualize attrition trends, barriers, and wait times
- **Client Detail Pages**: Profile, risk explanation, appointment history, and contact attempts
- **Simulated Data**: Privacy-safe dataset generation with encrypted IDs

## Performance

- Dashboard loads in under 5 seconds
- Supports 100–500+ client records
- Role-based access (in planning)
- Encrypted client IDs (no PII stored)

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 3. Generate Sample Data

Data is auto-generated on first run. To regenerate:

```bash
python3 src/data_generator.py
```

## Development

### Code Quality

```bash
# Format code
black src/ app.py

# Lint
flake8 src/ app.py

# Run tests
pytest
```

### Project Structure

```
intake-attrition-dashboard/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/
│   └── simulated_intake_data.csv  # Generated client data
│
├── src/
│   ├── risk_scoring.py            # Risk calculation logic
│   ├── data_cleaning.py           # Data validation
│   ├── charts.py                  # Plotly visualizations
│   └── data_generator.py          # Data simulation
│
└── .github/
    └── copilot-instructions.md    # Dev guide
```

## Risk Scoring

### Factors & Weights (capped at 100)

- Missed appointment: +25
- Transportation barrier: +20
- Housing instability: +20
- No family support: +15
- Multiple failed contact attempts: +15
- Long wait time: +10

### Risk Categories

- **Low Risk**: 0–30
- **Medium Risk**: 31–60
- **High Risk**: 61+

## User Roles

- **Intake Coordinator**: View new clients, track appointments, prioritize follow-up
- **Counselor/Social Worker**: Review barriers, add notes, plan interventions
- **Program Manager**: View trends, track attrition rates, identify bottlenecks

## Next Steps

1. Customize risk scoring weights based on pilot data
2. Implement user authentication
3. Migrate to SQLite for larger datasets
4. Add notes/intervention tracking UI
5. Build ML model for risk prediction

## License

Internal Use Only
