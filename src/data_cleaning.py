"""
Data cleaning and validation utilities.
"""

import pandas as pd
import hashlib
from typing import Tuple


def generate_encrypted_id(name: str) -> str:
    """
    Generate encrypted ID from client name (no PII stored).
    
    Args:
        name: Client name (used only to generate hash)
        
    Returns:
        Hashed ID string
    """
    hash_obj = hashlib.sha256(name.encode())
    return 'CLIENT_' + hash_obj.hexdigest()[:8].upper()


def validate_client_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Validate and clean client data.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Tuple of (cleaned DataFrame, list of warnings)
    """
    df = df.copy()
    warnings = []
    
    # Validate required columns
    required_cols = [
        'client_id', 'intake_date', 'referral_source',
        'transportation_barrier', 'housing_instability',
        'missed_appointments', 'contact_attempts', 'wait_days'
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        warnings.append(f"Missing columns: {', '.join(missing_cols)}")
    
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates(subset=['client_id'])
    if len(df) < initial_rows:
        warnings.append(f"Removed {initial_rows - len(df)} duplicate records")
    
    # Validate numeric columns
    numeric_cols = ['missed_appointments', 'contact_attempts', 'wait_days']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Validate boolean columns
    bool_cols = ['transportation_barrier', 'housing_instability', 'employment_status', 'family_support']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    
    # Validate dates
    if 'intake_date' in df.columns:
        df['intake_date'] = pd.to_datetime(df['intake_date'], errors='coerce')
    
    if 'admitted' in df.columns:
        df['admitted'] = df['admitted'].astype(bool)
    
    return df, warnings


def calculate_attrition_rate(df: pd.DataFrame) -> float:
    """
    Calculate overall attrition rate.
    
    Args:
        df: Client DataFrame with 'admitted' column
        
    Returns:
        Attrition rate (0-1)
    """
    if len(df) == 0:
        return 0.0
    
    admitted = df['admitted'].sum() if 'admitted' in df.columns else 0
    return 1 - (admitted / len(df))


def calculate_admission_rate(df: pd.DataFrame) -> float:
    """
    Calculate overall admission rate.
    
    Args:
        df: Client DataFrame with 'admitted' column
        
    Returns:
        Admission rate (0-1)
    """
    if len(df) == 0:
        return 0.0
    
    admitted = df['admitted'].sum() if 'admitted' in df.columns else 0
    return admitted / len(df)
