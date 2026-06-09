import pandas as pd

DATA_PATH = "worldcup26/data/"


def load_teams():
    return pd.read_csv(DATA_PATH + "all_national_teams_info_20260525_185214.csv")

def load_fifa():
    return pd.read_csv(DATA_PATH + "fifa_ranking.csv")

def load_elo():
    return pd.read_csv(DATA_PATH + "elo_ratings.csv")

def load_all_players_fotmob():
    return pd.read_csv(DATA_PATH + "all_players_wc26_fotmob.csv")

def load_venues():
    return pd.read_excel(DATA_PATH + "stadia_wc2026.xlsx")

def load_fixtures():
    return pd.read_csv(DATA_PATH + "fixtures_wc26_stages.csv")

def load_all_matches_fotmob():
    return pd.read_csv(DATA_PATH + "all_matches_wc26_fotmob.csv")

def load_fixtures_pruebas():
    return pd.read_csv(DATA_PATH + "fixtures_copa_america.csv")
