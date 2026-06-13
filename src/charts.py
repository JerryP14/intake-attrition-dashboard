"""
Plotly chart generation for dashboard visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict


def create_attrition_by_referral_source(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of attrition rate by referral source.
    """
    df_grouped = df.groupby('referral_source').agg({
        'client_id': 'count',
        'admitted': 'sum'
    }).reset_index()
    df_grouped.columns = ['referral_source', 'total', 'admitted']
    df_grouped['attrition_rate'] = (1 - df_grouped['admitted'] / df_grouped['total']) * 100
    
    fig = px.bar(
        df_grouped,
        x='referral_source',
        y='attrition_rate',
        title='Attrition Rate by Referral Source',
        labels={'attrition_rate': 'Attrition Rate (%)', 'referral_source': 'Referral Source'},
        color='attrition_rate',
        color_continuous_scale='Reds'
    )
    return fig


def create_attrition_by_barrier(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of attrition rate by transportation barrier presence.
    """
    df_barrier = df.groupby('transportation_barrier').agg({
        'client_id': 'count',
        'admitted': 'sum'
    }).reset_index()
    df_barrier.columns = ['has_barrier', 'total', 'admitted']
    df_barrier['attrition_rate'] = (1 - df_barrier['admitted'] / df_barrier['total']) * 100
    df_barrier['barrier_type'] = df_barrier['has_barrier'].map({True: 'Has Barrier', False: 'No Barrier'})
    
    fig = px.bar(
        df_barrier,
        x='barrier_type',
        y='attrition_rate',
        title='Attrition Rate by Transportation Barrier',
        labels={'attrition_rate': 'Attrition Rate (%)', 'barrier_type': 'Status'},
        color='barrier_type'
    )
    return fig


def create_wait_time_by_outcome(df: pd.DataFrame) -> go.Figure:
    """
    Create box plot of wait time by admission outcome.
    """
    df_wait = df.copy()
    df_wait['outcome'] = df_wait['admitted'].map({True: 'Admitted', False: 'Did Not Admit'})
    
    fig = px.box(
        df_wait,
        x='outcome',
        y='wait_days',
        title='Average Wait Time by Outcome',
        labels={'wait_days': 'Wait Days (days)', 'outcome': 'Outcome'},
        points='all'
    )
    return fig


def create_missed_appointments_by_risk(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of missed appointments by risk level.
    """
    fig = px.scatter(
        df,
        x='risk_category',
        y='missed_appointments',
        color='risk_category',
        size='contact_attempts',
        title='Missed Appointments by Risk Level',
        labels={'missed_appointments': 'Missed Appointments', 'risk_category': 'Risk Category'},
        category_orders={'risk_category': ['Low Risk', 'Medium Risk', 'High Risk']}
    )
    return fig


def create_high_risk_by_week(df: pd.DataFrame) -> go.Figure:
    """
    Create time series of high-risk clients by week.
    """
    df_time = df.copy()
    df_time['intake_date'] = pd.to_datetime(df_time['intake_date'])
    df_time['week'] = df_time['intake_date'].dt.isocalendar().week
    
    df_high_risk = df_time[df_time['risk_category'] == 'High Risk'].groupby('week').size().reset_index(name='count')
    
    fig = px.line(
        df_high_risk,
        x='week',
        y='count',
        title='High-Risk Clients by Week',
        labels={'count': 'Number of Clients', 'week': 'Week'},
        markers=True
    )
    return fig


def create_top_barriers(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of top barriers causing disengagement.
    """
    barriers = {
        'Transportation': df['transportation_barrier'].sum(),
        'Housing': df['housing_instability'].sum(),
        'No Family Support': (~df['family_support']).sum(),
        'Multiple Contact Failures': (df['contact_attempts'] > 2).sum(),
    }
    
    barrier_df = pd.DataFrame(list(barriers.items()), columns=['barrier', 'count'])
    barrier_df = barrier_df.sort_values('count', ascending=False)
    
    fig = px.bar(
        barrier_df,
        x='barrier',
        y='count',
        title='Top Barriers Causing Disengagement',
        labels={'count': 'Frequency', 'barrier': 'Barrier Type'},
        color='count',
        color_continuous_scale='Blues'
    )
    return fig


def create_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create histogram of risk score distribution.
    """
    fig = px.histogram(
        df,
        x='risk_score',
        nbins=20,
        title='Risk Score Distribution',
        labels={'risk_score': 'Risk Score', 'count': 'Number of Clients'},
        color_discrete_sequence=['#636EFA']
    )
    return fig
