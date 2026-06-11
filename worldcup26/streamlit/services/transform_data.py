from utils.mapping import *
import pandas as pd

def build_teams_dataset(df_teams: pd.DataFrame,df_fifa: pd.DataFrame,df_elo: pd.DataFrame) -> pd.DataFrame:
    """
    Build a consolidated teams dataset by combining team information,
    FIFA rankings, and Elo ratings.

    This function creates a normalized team name column using the
    NAME_MAPPING dictionary and performs two left joins to enrich
    the teams dataset with FIFA and Elo ranking information.

    Args:
        df_teams (pd.DataFrame): Base teams dataset containing at least
            the 'Squad' column.
        df_fifa (pd.DataFrame): FIFA rankings dataset containing at least
            the 'team' column.
        df_elo (pd.DataFrame): Elo ratings dataset containing at least
            the 'team' column.

    Returns:
        pd.DataFrame: Consolidated dataset containing team information,
        FIFA rankings, and Elo ratings sorted alphabetically by team name.

    Raises:
        TypeError: If any input is not a pandas DataFrame.
        KeyError: If required columns are missing from any dataset.
        RuntimeError: If the merge process fails.
    """

    # 🔹 Validate input types
    if not isinstance(df_teams, pd.DataFrame):
        raise TypeError("df_teams must be a pandas DataFrame")

    if not isinstance(df_fifa, pd.DataFrame):
        raise TypeError("df_fifa must be a pandas DataFrame")

    if not isinstance(df_elo, pd.DataFrame):
        raise TypeError("df_elo must be a pandas DataFrame")

    # 🔹 Validate required columns
    if "Squad" not in df_teams.columns:
        raise KeyError("Column 'Squad' not found in df_teams")

    if "team" not in df_fifa.columns:
        raise KeyError("Column 'team' not found in df_fifa")

    if "team" not in df_elo.columns:
        raise KeyError("Column 'team' not found in df_elo")

    try:
        # 🔹 Create a working copy to avoid modifying the original DataFrame
        df_teams = df_teams.copy()

        # 🔹 Normalize team names for dataset matching
        df_teams["team_merge"] = df_teams["Squad"].replace(NAME_MAPPING)

        # 🔹 Merge FIFA rankings
        df_merged = df_teams.merge(df_fifa,left_on="team_merge",right_on="team",how="left" ).drop(columns=["team"])

        # 🔹 Merge Elo ratings
        df_final = df_merged.merge( df_elo, left_on="team_merge", right_on="team", how="left")

        # 🔹 Return sorted consolidated dataset
        return df_final.sort_values("Squad").reset_index(drop=True)

    except Exception as e:
        raise RuntimeError(f"Failed to build teams dataset: {e}")