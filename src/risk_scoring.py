"""
Risk scoring engine with rule-based and weighted factors.
All scores are capped at 100 to prevent extreme values.
"""

import pandas as pd
from typing import Dict, Tuple


class RiskScorer:
    """Calculate client risk scores based on multiple factors."""
    
    # Risk factor weights
    FACTOR_WEIGHTS = {
        'missed_appointments': 25,
        'transportation_barrier': 20,
        'housing_instability': 20,
        'no_family_support': 15,
        'multiple_failed_contacts': 15,
        'long_wait_time': 10,
    }
    
    # Risk category thresholds
    RISK_THRESHOLDS = {
        'low': (0, 30),
        'medium': (31, 60),
        'high': (61, 100),
    }
    
    # Score cap to prevent extreme values
    MAX_SCORE = 100
    
    @classmethod
    def calculate_score(cls, client_data: Dict) -> int:
        """
        Calculate risk score for a single client.
        
        Args:
            client_data: Dictionary with client attributes
            
        Returns:
            Risk score (0-100)
        """
        score = 0
        
        # Apply each risk factor
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
        
        # Cap at maximum
        return min(score, cls.MAX_SCORE)
    
    @classmethod
    def get_risk_category(cls, score: int) -> str:
        """
        Classify score into risk category.
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            Risk category: 'Low Risk', 'Medium Risk', or 'High Risk'
        """
        if score <= cls.RISK_THRESHOLDS['low'][1]:
            return 'Low Risk'
        elif score <= cls.RISK_THRESHOLDS['medium'][1]:
            return 'Medium Risk'
        else:
            return 'High Risk'
    
    @classmethod
    def calculate_all_scores(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate risk scores for all clients in DataFrame.
        
        Args:
            df: DataFrame with client data
            
        Returns:
            DataFrame with added 'risk_score' and 'risk_category' columns
        """
        df = df.copy()
        df['risk_score'] = df.apply(
            lambda row: cls.calculate_score(row.to_dict()), 
            axis=1
        )
        df['risk_category'] = df['risk_score'].apply(cls.get_risk_category)
        
        return df


def get_main_risk_factors(client_data: Dict) -> list:
    """
    Identify the main risk factors for a client.
    
    Args:
        client_data: Dictionary with client attributes
        
    Returns:
        List of contributing risk factors
    """
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
