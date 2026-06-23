"""
Data Ingestion Module
Reads CSV and Excel files from the data/raw/ folder.
"""

import pandas as pd
from pathlib import Path


def read_csv_file(filepath: str) -> pd.DataFrame:
    """
    Reads a CSV file and returns a pandas DataFrame.

    Args:
        filepath: Path to the CSV file

    Returns:
        DataFrame with the file's data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or corrupt
    """
    path = Path(filepath)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Check if it's actually a CSV
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected .csv file, got: {path.suffix}")

    try:
        df = pd.read_csv(filepath)

        # Check if file is empty
        if df.empty:
            raise ValueError(f"File is empty: {filepath}")

        print(f"\n✅ Successfully read {len(df)} rows from {path.name}")
        return df

    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty: {filepath}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Could not parse file: {e}")


def read_excel_file(filepath: str) -> pd.DataFrame:
    """Reads an Excel file and returns a pandas DataFrame."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() not in [".xlsx", ".xls"]:
        raise ValueError(f"Expected Excel file, got: {path.suffix}")

    try:
        df = pd.read_excel(filepath)

        if df.empty:
            raise ValueError(f"File is empty: {filepath}")

        print(f"\n✅ Successfully read {len(df)} rows from {path.name}")
        return df

    except Exception as e:
        raise ValueError(f"Could not read Excel file: {e}")
