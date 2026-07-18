"""
Risk scoring engine with rule-based and weighted factors.
All scores are capped at 100 to prevent extreme values.
"""

import pandas as pd
from typing import Dict, List


class RiskScorer:
    """Calculate client risk scores based on multiple factors."""

    FACTOR_WEIGHTS = {
        'missed_appointments': 25,
        'transportation_barrier': 20,
        'housing_instability': 20,
        'no_family_support': 15,
        'multiple_failed_contacts': 15,
        'long_wait_time': 10,
    }

    RISK_THRESHOLDS = {
        'low': (0, 30),
        'medium': (31, 60),
        'high': (61, 100),
    }

    MAX_SCORE = 100

    @classmethod
    def calculate_score(cls, client_data: Dict) -> int:
        """Calculate risk score for a single client."""
        score = 0

        if client_data.get('missed_appointments', 0) > 0:
            score += cls.FACTOR_WEIGHTS['missed_appointments']

        if client_data.get('transportation_barrier'):
            score += cls.FACTOR_WEIGHTS['transportation_barrier']

        if client_data.get('housing_instability'):
            score += cls.FACTOR_WEIGHTS['housing_instability']

        if not client_data.get('family_support'):
            score += cls.FACTOR_WEIGHTS['no_family_support']

        if client_data.get('contact_attempts', 0) > 2:
            score += cls.FACTOR_WEIGHTS['multiple_failed_contacts']

        if client_data.get('wait_days', 0) > 14:
            score += cls.FACTOR_WEIGHTS['long_wait_time']

        return min(score, cls.MAX_SCORE)

    @classmethod
    def get_risk_category(cls, score: int) -> str:
        """Classify score into risk category."""
        if score <= cls.RISK_THRESHOLDS['low'][1]:
            return 'Low Risk'
        if score <= cls.RISK_THRESHOLDS['medium'][1]:
            return 'Medium Risk'
        return 'High Risk'

    @classmethod
    def get_risk_level(cls, score: int) -> str:
        """Return a short label suitable for UI badges."""
        category = cls.get_risk_category(score)
        return category.replace(' Risk', '')

    @classmethod
    def calculate_all_scores(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate risk scores for all clients in DataFrame."""
        df = df.copy()
        df['risk_score'] = df.apply(lambda row: cls.calculate_score(row.to_dict()), axis=1)
        df['risk_category'] = df['risk_score'].apply(cls.get_risk_category)
        return df


def get_main_risk_factors(client_data: Dict) -> List[str]:
    """Identify the main risk factors for a client."""
    factors = []

    if client_data.get('missed_appointments', 0) > 0:
        factors.append('Missed appointments')

    if client_data.get('transportation_barrier'):
        factors.append('Transportation barrier')

    if client_data.get('housing_instability'):
        factors.append('Housing instability')

    if not client_data.get('family_support'):
        factors.append('No family support')

    if client_data.get('contact_attempts', 0) > 2:
        factors.append('Multiple failed contacts')

    if client_data.get('wait_days', 0) > 14:
        factors.append('Long wait time')

    return factors if factors else ['No major risk factors']


def get_risk_factor_details(client_data: Dict) -> List[Dict]:
    """Return structured factor details in priority order."""
    factors = []

    if client_data.get('transportation_barrier'):
        factors.append({
            'factor': 'Transportation Barrier',
            'impact': 'High',
            'detail': 'Transportation challenges may prevent the client from keeping intake or assessment appointments.',
            'weight': 20,
        })

    if client_data.get('housing_instability'):
        factors.append({
            'factor': 'Housing Instability',
            'impact': 'High',
            'detail': 'Housing instability can reduce stability and increase the risk of disengaging during intake.',
            'weight': 20,
        })

    if client_data.get('missed_appointments', 0) > 0:
        factors.append({
            'factor': 'Missed Appointments',
            'impact': 'High',
            'detail': f'The client has missed {int(client_data.get("missed_appointments", 0))} appointment(s), which suggests reduced engagement.',
            'weight': 25,
        })

    if not client_data.get('family_support'):
        factors.append({
            'factor': 'Limited Family Support',
            'impact': 'Medium',
            'detail': 'Limited family support may reduce follow-through during the intake process.',
            'weight': 15,
        })

    if client_data.get('contact_attempts', 0) > 2:
        factors.append({
            'factor': 'Multiple Failed Contacts',
            'impact': 'Medium',
            'detail': 'Repeated outreach attempts without response indicate a higher likelihood of disengagement.',
            'weight': 15,
        })

    wait_days = int(client_data.get('wait_days', 0))
    if wait_days > 14:
        factors.append({
            'factor': 'Long Wait Time',
            'impact': 'Medium',
            'detail': f'The intake wait time is {wait_days} days, which may increase dropout risk.',
            'weight': 10,
        })

    if not factors:
        factors.append({
            'factor': 'No Major Risk Factors',
            'impact': 'Low',
            'detail': 'The client is currently showing stable engagement and no major barriers were identified.',
            'weight': 0,
        })

    return sorted(factors, key=lambda item: item['weight'], reverse=True)


def get_recommended_actions(client_data: Dict) -> List[Dict]:
    """Generate recommended actions based on identified barriers."""
    actions = []

    if client_data.get('transportation_barrier'):
        actions.append({
            'title': 'Transportation Barrier',
            'items': [
                'Arrange transportation voucher',
                'Schedule telehealth when appropriate',
                'Offer a nearby community access point',
            ],
        })

    if client_data.get('housing_instability'):
        actions.append({
            'title': 'Housing Instability',
            'items': [
                'Refer to housing assistance resources',
                'Notify the case manager for immediate follow-up',
                'Prioritize a warm handoff to community support services',
            ],
        })

    if client_data.get('wait_days', 0) > 14:
        actions.append({
            'title': 'Long Wait Time',
            'items': [
                'Move the client to priority scheduling',
                'Increase follow-up frequency',
                'Send a reminder outreach message within 48 hours',
            ],
        })

    if client_data.get('missed_appointments', 0) > 0:
        actions.append({
            'title': 'Missed Appointments',
            'items': [
                'Increase outreach attempts',
                'Contact the emergency contact if permitted',
                'Review appointment barriers and reschedule promptly',
            ],
        })

    if client_data.get('employment_status') == 'Unemployed':
        actions.append({
            'title': 'Employment / Funding Concern',
            'items': [
                'Refer to a financial counselor',
                'Verify Medicaid or funding options',
                'Provide a resource list for immediate support',
            ],
        })

    if not client_data.get('family_support'):
        actions.append({
            'title': 'Limited Family Support',
            'items': [
                'Offer peer support engagement',
                'Coordinate with community support partners',
                'Invite the client to a family-oriented orientation if appropriate',
            ],
        })

    if not actions:
        actions.append({
            'title': 'Supportive Engagement',
            'items': [
                'Continue routine follow-up',
                'Maintain regular communication',
                'Reassess barriers at the next contact',
            ],
        })

    return actions
