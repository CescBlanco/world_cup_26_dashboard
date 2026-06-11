import pandas as pd
import os
DATA_PATH = "worldcup26/data/"


def load_teams() -> pd.DataFrame:
    """
    Load national teams information dataset.

    Reads the CSV file containing all national teams metadata and
    returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: National teams information dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "all_national_teams_info_20260525_185214.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Teams file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load teams dataset: {e}")

def load_fifa() -> pd.DataFrame:
    """
    Load FIFA ranking dataset.

    Reads the FIFA rankings CSV file and returns its contents
    as a pandas DataFrame.

    Returns:
        pd.DataFrame: FIFA rankings dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "fifa_ranking.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"FIFA ranking file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load FIFA rankings: {e}")

def load_elo() -> pd.DataFrame:
    """
    Load Elo ratings dataset.

    Reads the Elo ratings CSV file and returns its contents
    as a pandas DataFrame.

    Returns:
        pd.DataFrame: Elo ratings dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "elo_ratings.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Elo ratings file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load Elo ratings: {e}")

def load_all_players_fotmob() -> pd.DataFrame:
    """
    Load FotMob players dataset.

    Reads the CSV file containing player information collected
    from FotMob and returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: FotMob players dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "all_players_wc26_fotmob.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Players file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load players dataset: {e}")

def load_venues() -> pd.DataFrame:
    """
    Load World Cup 2026 venues dataset.

    Reads the Excel file containing stadium and venue information
    and returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: Venues dataset.

    Raises:
        FileNotFoundError: If the Excel file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "stadia_wc2026.xlsx"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Venues file not found: {file_path}")

    try:
        return pd.read_excel(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load venues dataset: {e}")

def load_fixtures() -> pd.DataFrame:
    """
    Load World Cup 2026 fixtures dataset.

    Reads the CSV file containing tournament fixtures and
    returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: Fixtures dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "fixtures_wc26_stages.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fixtures file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load fixtures dataset: {e}")

def load_all_matches_fotmob() -> pd.DataFrame:
    """
    Load FotMob matches dataset.

    Reads the CSV file containing match information collected
    from FotMob and returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: FotMob matches dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "all_matches_wc26_fotmob.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Matches file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load matches dataset: {e}")

def load_fixtures_pruebas() -> pd.DataFrame:
    """
    Load test fixtures dataset.

    Reads the CSV file containing Copa America fixtures used
    for testing and validation purposes.

    Returns:
        pd.DataFrame: Test fixtures dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        RuntimeError: If the file cannot be read.
    """

    file_path = DATA_PATH + "fixtures_copa_america.csv"

    # 🔹 Validate file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test fixtures file not found: {file_path}")

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise RuntimeError(f"Failed to load test fixtures dataset: {e}")
