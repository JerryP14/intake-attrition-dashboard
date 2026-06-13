"""
Intake Attrition Risk Dashboard - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Import custom modules
from src.risk_scoring import RiskScorer, get_main_risk_factors
from src.data_cleaning import validate_client_data, calculate_attrition_rate, calculate_admission_rate
from src.data_generator import generate_simulated_data, save_to_csv
from src import charts


# Page configuration
st.set_page_config(
    page_title="Intake Attrition Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown("""
    <style>
    .metric-card { padding: 20px; border-radius: 10px; background-color: #f0f2f6; }
    .high-risk { color: #d32f2f; font-weight: bold; }
    .medium-risk { color: #f57c00; font-weight: bold; }
    .low-risk { color: #388e3c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_or_generate_data():
    """Load data from CSV or generate if doesn't exist."""
    data_dir = Path(__file__).parent / 'data'
    csv_path = data_dir / 'simulated_intake_data.csv'
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        # Generate new data
        df = generate_simulated_data(n_records=400)
        save_to_csv(df, str(csv_path))
    
    # Validate data
    df, warnings = validate_client_data(df)
    
    # Calculate risk scores
    df = RiskScorer.calculate_all_scores(df)
    
    return df


def main():
    """Main application flow."""
    
    # Load data
    df = load_or_generate_data()
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Home / Overview", "Risk Dashboard", "Client Profile", "Analytics"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Stats**")
    st.sidebar.metric("Total Clients", len(df))
    st.sidebar.metric("Admission Rate", f"{calculate_admission_rate(df)*100:.1f}%")
    st.sidebar.metric("Attrition Rate", f"{calculate_attrition_rate(df)*100:.1f}%")
    st.sidebar.metric("High-Risk Clients", len(df[df['risk_category'] == 'High Risk']))
    
    # Page routing
    if page == "Home / Overview":
        show_home(df)
    elif page == "Risk Dashboard":
        show_risk_dashboard(df)
    elif page == "Client Profile":
        show_client_profile(df)
    elif page == "Analytics":
        show_analytics(df)


def show_home(df: pd.DataFrame):
    """Home / Overview page."""
    st.title("📊 Intake Attrition Risk Dashboard")
    st.markdown("Analyze client risk levels, appointment history, and intervention priorities.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", len(df))
    
    with col2:
        admission_rate = calculate_admission_rate(df)
        st.metric("Admission Rate", f"{admission_rate*100:.1f}%")
    
    with col3:
        attrition_rate = calculate_attrition_rate(df)
        st.metric("Attrition Rate", f"{attrition_rate*100:.1f}%")
    
    with col4:
        high_risk_count = len(df[df['risk_category'] == 'High Risk'])
        st.metric("High-Risk Clients", high_risk_count)
    
    st.markdown("---")
    
    st.subheader("Quick Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_dist = df['risk_category'].value_counts()
        st.write("**Clients by Risk Level**")
        st.bar_chart(risk_dist)
    
    with col2:
        source_dist = df['referral_source'].value_counts().head(10)
        st.write("**Clients by Referral Source**")
        st.bar_chart(source_dist)
    
    st.markdown("---")
    st.info("👉 Use the **Risk Dashboard** to filter clients and view detailed charts. Use **Client Profile** to see individual client details.")


def show_risk_dashboard(df: pd.DataFrame):
    """Risk Dashboard page with filters."""
    st.title("🎯 Risk Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=['Low Risk', 'Medium Risk', 'High Risk'],
            default=['Low Risk', 'Medium Risk', 'High Risk']
        )
    
    with col2:
        referral_filter = st.multiselect(
            "Filter by Referral Source",
            options=df['referral_source'].unique(),
            default=df['referral_source'].unique()
        )
    
    with col3:
        barrier_filter = st.radio(
            "Filter by Transportation Barrier",
            options=['All', 'Has Barrier', 'No Barrier'],
            horizontal=True
        )
    
    # Apply filters
    filtered_df = df[
        (df['risk_category'].isin(risk_filter)) &
        (df['referral_source'].isin(referral_filter))
    ]
    
    if barrier_filter == 'Has Barrier':
        filtered_df = filtered_df[filtered_df['transportation_barrier'] == True]
    elif barrier_filter == 'No Barrier':
        filtered_df = filtered_df[filtered_df['transportation_barrier'] == False]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} clients**")
    st.markdown("---")
    
    # Client Risk Table
    st.subheader("Client Risk Table")
    
    display_cols = [
        'client_id', 'intake_date', 'risk_score', 'risk_category',
        'missed_appointments', 'contact_attempts', 'wait_days'
    ]
    
    df_display = filtered_df[display_cols].copy()
    df_display['intake_date'] = pd.to_datetime(df_display['intake_date']).dt.strftime('%Y-%m-%d')
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Charts
    st.subheader("Risk Analysis Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(charts.create_attrition_by_referral_source(filtered_df), use_container_width=True)
        st.plotly_chart(charts.create_missed_appointments_by_risk(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(charts.create_attrition_by_barrier(filtered_df), use_container_width=True)
        st.plotly_chart(charts.create_wait_time_by_outcome(filtered_df), use_container_width=True)
    
    st.plotly_chart(charts.create_top_barriers(filtered_df), use_container_width=True)


def show_client_profile(df: pd.DataFrame):
    """Client Profile page."""
    st.title("👤 Client Profile")
    
    # Select client
    client_id = st.selectbox(
        "Select a Client",
        options=df['client_id'].unique(),
        help="Choose a client to view details"
    )
    
    client = df[df['client_id'] == client_id].iloc[0]
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Score", int(client['risk_score']))
    with col2:
        risk_category = client['risk_category']
        color = '#d32f2f' if risk_category == 'High Risk' else '#f57c00' if risk_category == 'Medium Risk' else '#388e3c'
        st.markdown(f"<div style='color: {color}; font-weight: bold; font-size: 20px;'>{risk_category}</div>", unsafe_allow_html=True)
    with col3:
        st.metric("Intake Date", pd.to_datetime(client['intake_date']).strftime('%Y-%m-%d'))
    with col4:
        status = "Admitted" if client['admitted'] else "Did Not Admit"
        st.metric("Status", status)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Main Risk Factors")
        factors = get_main_risk_factors(client.to_dict())
        for factor in factors:
            st.write(f"• {factor}")
        
        st.subheader("Barriers Present")
        st.write(f"• Transportation: {'Yes' if client['transportation_barrier'] else 'No'}")
        st.write(f"• Housing Instability: {'Yes' if client['housing_instability'] else 'No'}")
        st.write(f"• Family Support: {'Yes' if client['family_support'] else 'No'}")
    
    with col2:
        st.subheader("Contact & Appointment History")
        st.write(f"• Contact Attempts: {int(client['contact_attempts'])}")
        st.write(f"• Missed Appointments: {int(client['missed_appointments'])}")
        st.write(f"• Wait Days: {int(client['wait_days'])}")
        st.write(f"• Referral Source: {client['referral_source']}")
        st.write(f"• Employment: {client['employment_status']}")
    
    st.markdown("---")
    
    st.subheader("Recommended Follow-up Action")
    risk_score = client['risk_score']
    
    if risk_score >= 61:
        st.warning("🔴 **HIGH PRIORITY** - Schedule immediate outreach within 2 days. Consider barrier-specific interventions.")
    elif risk_score >= 31:
        st.info("🟡 **MEDIUM PRIORITY** - Schedule follow-up within 1 week. Address identified barriers.")
    else:
        st.success("🟢 **LOW PRIORITY** - Routine follow-up. Monitor for changes in status.")


def show_analytics(df: pd.DataFrame):
    """Analytics page."""
    st.title("📈 Analytics & Trends")
    
    st.subheader("Risk Score Distribution")
    st.plotly_chart(charts.create_risk_distribution(df), use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("High-Risk Clients Over Time")
        st.plotly_chart(charts.create_high_risk_by_week(df), use_container_width=True)
    
    with col2:
        st.subheader("Top Disengagement Factors")
        st.plotly_chart(charts.create_top_barriers(df), use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_score = df['risk_score'].mean()
        st.metric("Average Risk Score", f"{avg_score:.1f}")
    
    with col2:
        high_risk_pct = (len(df[df['risk_category'] == 'High Risk']) / len(df)) * 100
        st.metric("% High-Risk Clients", f"{high_risk_pct:.1f}%")
    
    with col3:
        avg_contacts = df['contact_attempts'].mean()
        st.metric("Average Contact Attempts", f"{avg_contacts:.1f}")


if __name__ == "__main__":
    main()
