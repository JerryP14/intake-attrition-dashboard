"""
Simulated data generation for testing and demonstration.
Creates realistic fake intake records with no PII.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import hashlib


def generate_encrypted_client_id(index: int) -> str:
    """Generate encrypted client ID from index."""
    hash_obj = hashlib.sha256(str(index).encode())
    return 'CLIENT_' + hash_obj.hexdigest()[:8].upper()


def generate_simulated_data(n_records: int = 300) -> pd.DataFrame:
    """
    Generate simulated intake data.
    
    Args:
        n_records: Number of client records to generate
        
    Returns:
        DataFrame with simulated client data
    """
    np.random.seed(42)  # For reproducibility
    
    referral_sources = [
        'Self Referral', 'Healthcare Provider', 'Community Agency',
        'Court System', 'Family/Friend', 'Social Services'
    ]
    
    intake_dates = [
        datetime.now() - timedelta(days=int(x))
        for x in np.random.randint(1, 180, n_records)
    ]
    
    data = {
        'client_id': [generate_encrypted_client_id(i) for i in range(n_records)],
        'intake_date': intake_dates,
        'referral_source': np.random.choice(referral_sources, n_records),
        'transportation_barrier': np.random.choice([True, False], n_records, p=[0.35, 0.65]),
        'housing_instability': np.random.choice([True, False], n_records, p=[0.30, 0.70]),
        'employment_status': np.random.choice(['Employed', 'Unemployed', 'Student'], n_records),
        'family_support': np.random.choice([True, False], n_records, p=[0.55, 0.45]),
        'missed_appointments': np.random.poisson(1, n_records),
        'contact_attempts': np.random.randint(0, 8, n_records),
        'wait_days': np.random.randint(0, 30, n_records),
        'intake_completed': np.random.choice([True, False], n_records, p=[0.80, 0.20]),
        'admitted': np.random.choice([True, False], n_records, p=[0.65, 0.35]),
    }
    
    df = pd.DataFrame(data)
    
    # Add some realistic correlations
    # Clients with transportation barriers are less likely to be admitted
    barrier_mask = df['transportation_barrier']
    df.loc[barrier_mask, 'admitted'] = np.random.choice(
        [True, False],
        barrier_mask.sum(),
        p=[0.50, 0.50]
    )
    
    # Clients with more contact attempts are less likely to be admitted
    high_contact_mask = df['contact_attempts'] > 3
    df.loc[high_contact_mask, 'admitted'] = np.random.choice(
        [True, False],
        high_contact_mask.sum(),
        p=[0.45, 0.55]
    )
    
    # Clients with longer wait times are less likely to be admitted
    long_wait_mask = df['wait_days'] > 21
    df.loc[long_wait_mask, 'admitted'] = np.random.choice(
        [True, False],
        long_wait_mask.sum(),
        p=[0.50, 0.50]
    )
    
    return df


def generate_appointment_id(client_id: str, index: int) -> str:
    hash_obj = hashlib.sha256(f"{client_id}-{index}".encode())
    return 'APPT_' + hash_obj.hexdigest()[:8].upper()


def generate_contact_id(client_id: str, index: int) -> str:
    hash_obj = hashlib.sha256(f"{client_id}-CONTACT-{index}".encode())
    return 'COMM_' + hash_obj.hexdigest()[:8].upper()


def generate_intervention_id(client_id: str, index: int) -> str:
    hash_obj = hashlib.sha256(f"{client_id}-INTERVENTION-{index}".encode())
    return 'INTV_' + hash_obj.hexdigest()[:8].upper()


def generate_simulated_appointments(clients_df: pd.DataFrame) -> pd.DataFrame:
    """Generate appointment history rows linked to each client."""
    appointment_types = ['Intake', 'Follow-up', 'Assessment', 'Referral', 'Case Management']
    statuses = ['Completed', 'Missed', 'Scheduled']
    locations = ['Clinic', 'Field Visit', 'Virtual', 'Community Site']

    appointments = []
    for _, row in clients_df.iterrows():
        client_id = row['client_id']
        intake_date = pd.to_datetime(row['intake_date'])
        total_appointments = max(1, min(np.random.poisson(2) + 1, 5))
        missed_left = int(row['missed_appointments'])

        for i in range(total_appointments):
            appointment_date = intake_date + timedelta(days=int(np.random.randint(0, 60)))
            if missed_left > 0:
                status = 'Missed'
                missed_left -= 1
            else:
                status = np.random.choice(statuses, p=[0.65, 0.10, 0.25])

            appointments.append({
                'appointment_id': generate_appointment_id(client_id, i),
                'client_id': client_id,
                'appointment_date': appointment_date,
                'appointment_type': np.random.choice(appointment_types),
                'status': status,
                'location': np.random.choice(locations),
                'notes': 'Follow-up required' if status == 'Missed' else ''
            })

    return pd.DataFrame(appointments)


def generate_simulated_communications(clients_df: pd.DataFrame) -> pd.DataFrame:
    """Generate communication attempt history for each client."""
    methods = ['Phone', 'Text', 'Email', 'In-person']
    outcomes = ['Reached', 'No Answer', 'Left Message', 'Scheduled', 'Rejected']

    records = []
    for _, row in clients_df.iterrows():
        client_id = row['client_id']
        intake_date = pd.to_datetime(row['intake_date'])
        attempts = int(row['contact_attempts'])
        attempts = max(attempts, 1)

        for i in range(attempts):
            attempt_date = intake_date + timedelta(days=int(np.random.randint(0, 45)))
            outcome = np.random.choice(outcomes, p=[0.35, 0.30, 0.20, 0.10, 0.05])
            records.append({
                'contact_id': generate_contact_id(client_id, i),
                'client_id': client_id,
                'attempt_date': attempt_date,
                'method': np.random.choice(methods),
                'result': outcome,
                'notes': 'Left voicemail' if outcome == 'Left Message' else ''
            })

    return pd.DataFrame(records)


def generate_simulated_interventions(clients_df: pd.DataFrame) -> pd.DataFrame:
    """Generate initial intervention notes for a subset of clients."""
    recommendations = [
        'Schedule barrier support session',
        'Arrange transportation assistance',
        'Connect with housing support',
        'Increase outreach frequency',
        'Offer peer mentor support',
    ]
    owned_by = ['Intake Coordinator', 'Counselor / Social Worker']

    interventions = []
    for _, row in clients_df.iterrows():
        client_id = row['client_id']
        if np.random.rand() < 0.25:
            interventions.append({
                'intervention_id': generate_intervention_id(client_id, 0),
                'client_id': client_id,
                'created_at': datetime.now() - timedelta(days=int(np.random.randint(1, 30))),
                'created_by': np.random.choice(owned_by),
                'note': 'Review transportation barrier and update follow-up plan.',
                'recommendation': np.random.choice(recommendations),
                'follow_up_by': 'Next Intake Coordinator' if np.random.rand() > 0.5 else 'Case Manager',
            })

    return pd.DataFrame(interventions)


def save_to_csv(df: pd.DataFrame, filepath: str = None) -> str:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        filepath: Path to save to (default: data/simulated_intake_data.csv)
        
    Returns:
        Path to saved file
    """
    if filepath is None:
        filepath = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'simulated_intake_data.csv'
        )
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")
    
    return filepath


if __name__ == '__main__':
    # Generate and save sample data
    df = generate_simulated_data(n_records=400)
    filepath = save_to_csv(df)
    print(f"\nGenerated {len(df)} records")
    print(df.head(10))
