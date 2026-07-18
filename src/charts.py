"""
Plotly chart generation for dashboard visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_attrition_by_referral_source(df: pd.DataFrame) -> go.Figure:
    """Create bar chart of attrition rate by referral source."""
    df_grouped = df.groupby('referral_source').agg({'client_id': 'count', 'admitted': 'sum'}).reset_index()
    df_grouped.columns = ['referral_source', 'total', 'admitted']
    df_grouped['attrition_rate'] = (1 - df_grouped['admitted'] / df_grouped['total']) * 100

    fig = px.bar(
        df_grouped,
        x='referral_source',
        y='attrition_rate',
        title='Attrition Rate by Referral Source',
        labels={'attrition_rate': 'Attrition Rate (%)', 'referral_source': 'Referral Source'},
        color='attrition_rate',
        color_continuous_scale='Reds',
    )
    return fig


def create_attrition_by_barrier(df: pd.DataFrame) -> go.Figure:
    """Create bar chart of attrition rate by transportation barrier presence."""
    df_barrier = df.groupby('transportation_barrier').agg({'client_id': 'count', 'admitted': 'sum'}).reset_index()
    df_barrier.columns = ['has_barrier', 'total', 'admitted']
    df_barrier['attrition_rate'] = (1 - df_barrier['admitted'] / df_barrier['total']) * 100
    df_barrier['barrier_type'] = df_barrier['has_barrier'].map({True: 'Has Barrier', False: 'No Barrier'})

    fig = px.bar(
        df_barrier,
        x='barrier_type',
        y='attrition_rate',
        title='Attrition Rate by Transportation Barrier',
        labels={'attrition_rate': 'Attrition Rate (%)', 'barrier_type': 'Status'},
        color='barrier_type',
    )
    return fig


def create_wait_time_by_outcome(df: pd.DataFrame) -> go.Figure:
    """Create box plot of wait time by admission outcome."""
    df_wait = df.copy()
    df_wait['outcome'] = df_wait['admitted'].map({True: 'Admitted', False: 'Did Not Admit'})

    fig = px.box(
        df_wait,
        x='outcome',
        y='wait_days',
        title='Wait Time by Admission Outcome',
        labels={'wait_days': 'Wait Days (days)', 'outcome': 'Outcome'},
        points='all',
    )
    return fig


def create_missed_appointments_by_risk(df: pd.DataFrame) -> go.Figure:
    """Create scatter plot of missed appointments by risk level."""
    fig = px.scatter(
        df,
        x='risk_category',
        y='missed_appointments',
        color='risk_category',
        size='contact_attempts',
        title='Missed Appointments by Risk Level',
        labels={'missed_appointments': 'Missed Appointments', 'risk_category': 'Risk Category'},
        category_orders={'risk_category': ['Low Risk', 'Medium Risk', 'High Risk']},
    )
    return fig


def create_high_risk_by_week(df: pd.DataFrame) -> go.Figure:
    """Create time series of high-risk clients by week."""
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
        markers=True,
    )
    return fig


def create_top_barriers(df: pd.DataFrame) -> go.Figure:
    """Create bar chart of top barriers causing disengagement."""
    barriers = {
        'Transportation': int(df['transportation_barrier'].sum()),
        'Housing': int(df['housing_instability'].sum()),
        'No Family Support': int((~df['family_support']).sum()),
        'Multiple Contact Failures': int((df['contact_attempts'] > 2).sum()),
        'Long Wait Time': int((df['wait_days'] > 14).sum()),
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
        color_continuous_scale='Blues',
    )
    return fig


def create_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """Create donut chart of risk distribution."""
    counts = df['risk_category'].value_counts().reindex(['Low Risk', 'Medium Risk', 'High Risk']).fillna(0)
    fig = px.pie(
        counts,
        values=counts.values,
        names=counts.index,
        hole=0.45,
        title='Risk Distribution',
        color_discrete_sequence=['#2e7d32', '#f59e0b', '#d32f2f'],
    )
    return fig


def create_intake_funnel(df: pd.DataFrame) -> go.Figure:
    """Create a simple intake funnel for the dashboard."""
    stages = {
        'Referral': len(df),
        'Initial Contact': int((df['contact_attempts'] > 0).sum()),
        'Assessment': int(df['intake_completed'].sum()),
        'Scheduled': int(((df['intake_completed']) & (~df['admitted'])).sum()),
        'Admitted': int(df['admitted'].sum()),
        'Dropped Before Admission': int((~df['admitted']).sum()),
    }
    funnel_df = pd.DataFrame(list(stages.items()), columns=['stage', 'count'])
    fig = go.Figure(go.Funnel(y=funnel_df['stage'], x=funnel_df['count'], textinfo='value+percent initial'))
    fig.update_layout(title='Intake Funnel', xaxis_title='Clients', yaxis_title='Stage')
    return fig


def create_average_wait_time_by_referral(df: pd.DataFrame) -> go.Figure:
    """Create average wait time chart by referral source."""
    summary = df.groupby('referral_source')['wait_days'].mean().reset_index().sort_values('wait_days', ascending=False)
    fig = px.bar(
        summary,
        x='referral_source',
        y='wait_days',
        title='Average Wait Time by Referral Source',
        labels={'wait_days': 'Average Wait Days', 'referral_source': 'Referral Source'},
        color='wait_days',
        color_continuous_scale='Purples',
    )
    return fig


def create_referral_source_analysis(df: pd.DataFrame) -> go.Figure:
    """Compare referral sources by admission rate and average risk."""
    summary = df.groupby('referral_source').agg(
        admission_rate=('admitted', 'mean'),
        average_risk=('risk_score', 'mean'),
        clients=('client_id', 'count'),
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary['referral_source'], y=summary['admission_rate'] * 100, name='Admission Rate (%)'))
    fig.add_trace(go.Scatter(x=summary['referral_source'], y=summary['average_risk'], mode='lines+markers', name='Average Risk Score', yaxis='y2'))
    fig.update_layout(
        title='Referral Source Analysis',
        xaxis_title='Referral Source',
        yaxis_title='Admission Rate (%)',
        yaxis2={'title': 'Average Risk Score', 'overlaying': 'y', 'side': 'right'},
    )
    return fig


def create_transportation_trends(df: pd.DataFrame) -> go.Figure:
    """Compare transportation barriers with admission outcomes."""
    grouped = df.groupby(['transportation_barrier', 'admitted']).size().reset_index(name='count')
    grouped['status'] = grouped['transportation_barrier'].map({True: 'Transportation Barrier', False: 'No Transportation Barrier'})
    grouped['outcome'] = grouped['admitted'].map({True: 'Admitted', False: 'Did Not Admit'})
    fig = px.bar(
        grouped,
        x='status',
        y='count',
        color='outcome',
        barmode='group',
        title='Transportation Barriers vs Admission Outcomes',
        labels={'count': 'Clients', 'status': 'Transportation Status', 'outcome': 'Outcome'},
    )
    return fig

