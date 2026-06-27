"""
SQLite persistence layer for client intake data.
"""

import sqlite3
from pathlib import Path
from typing import Tuple

import pandas as pd

from .data_cleaning import validate_client_data
from .data_generator import (
    generate_simulated_data,
    save_to_csv,
    generate_simulated_appointments,
    generate_simulated_communications,
    generate_simulated_interventions,
    generate_intervention_id,
)
from .risk_scoring import RiskScorer


def get_data_paths() -> Tuple[Path, Path, Path]:
    data_dir = Path(__file__).parent.parent / 'data'
    csv_path = data_dir / 'simulated_intake_data.csv'
    db_path = data_dir / 'intake_data.db'
    return data_dir, csv_path, db_path


def save_table_to_db(df: pd.DataFrame, table_name: str, db_path: Path) -> None:
    """Persist a DataFrame into the SQLite database using the given table name."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)


def load_table_from_db(db_path: Path, table_name: str, parse_dates=None) -> pd.DataFrame:
    """Load a table from the SQLite database into a DataFrame."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql_query(query, conn, parse_dates=parse_dates or [])
    return df


def save_all_data_to_db(
    clients_df: pd.DataFrame,
    appointments_df: pd.DataFrame,
    communications_df: pd.DataFrame,
    interventions_df: pd.DataFrame,
    db_path: Path,
) -> None:
    """Persist all dashboard tables into SQLite."""
    save_table_to_db(clients_df, 'clients', db_path)
    save_table_to_db(appointments_df, 'appointments', db_path)
    save_table_to_db(communications_df, 'communications', db_path)
    save_table_to_db(interventions_df, 'interventions', db_path)


def append_intervention_to_db(intervention_data: dict, db_path: Path) -> None:
    """Append a single intervention note to the SQLite interventions table."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        pd.DataFrame([intervention_data]).to_sql('interventions', conn, if_exists='append', index=False)


def load_or_initialize_data(n_records: int = 400) -> dict:
    """Load intake data tables from SQLite or initialize them from simulated data."""
    data_dir, csv_path, db_path = get_data_paths()
    data_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        if csv_path.exists():
            clients_df = pd.read_csv(csv_path)
        else:
            clients_df = generate_simulated_data(n_records)
            save_to_csv(clients_df, str(csv_path))

        clients_df, _ = validate_client_data(clients_df)
        clients_df = RiskScorer.calculate_all_scores(clients_df)
        appointments_df = generate_simulated_appointments(clients_df)
        communications_df = generate_simulated_communications(clients_df)
        interventions_df = generate_simulated_interventions(clients_df)
        save_all_data_to_db(clients_df, appointments_df, communications_df, interventions_df, db_path)
        return {
            'clients': clients_df,
            'appointments': appointments_df,
            'communications': communications_df,
            'interventions': interventions_df,
        }

    try:
        clients_df = load_table_from_db(db_path, 'clients', parse_dates=['intake_date'])
        appointments_df = load_table_from_db(db_path, 'appointments', parse_dates=['appointment_date'])
        communications_df = load_table_from_db(db_path, 'communications', parse_dates=['attempt_date'])
        interventions_df = load_table_from_db(db_path, 'interventions', parse_dates=['created_at'])
    except Exception:
        clients_df = pd.read_csv(csv_path) if csv_path.exists() else generate_simulated_data(n_records)
        clients_df, _ = validate_client_data(clients_df)
        clients_df = RiskScorer.calculate_all_scores(clients_df)
        appointments_df = generate_simulated_appointments(clients_df)
        communications_df = generate_simulated_communications(clients_df)
        interventions_df = generate_simulated_interventions(clients_df)
        save_all_data_to_db(clients_df, appointments_df, communications_df, interventions_df, db_path)

    return {
        'clients': clients_df,
        'appointments': appointments_df,
        'communications': communications_df,
        'interventions': interventions_df,
    }


def refresh_database_from_csv() -> dict:
    """Regenerate the SQLite database from the existing CSV file and rebuild supplementary tables."""
    _, csv_path, db_path = get_data_paths()
    if not csv_path.exists():
        raise FileNotFoundError('CSV data file not found for refresh.')

    clients_df = pd.read_csv(csv_path)
    clients_df, _ = validate_client_data(clients_df)
    clients_df = RiskScorer.calculate_all_scores(clients_df)
    appointments_df = generate_simulated_appointments(clients_df)
    communications_df = generate_simulated_communications(clients_df)
    interventions_df = generate_simulated_interventions(clients_df)
    save_all_data_to_db(clients_df, appointments_df, communications_df, interventions_df, db_path)
    return {
        'clients': clients_df,
        'appointments': appointments_df,
        'communications': communications_df,
        'interventions': interventions_df,
    }
