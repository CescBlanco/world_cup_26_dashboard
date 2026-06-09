from utils.mapping import *


def build_teams_dataset(df_teams, df_fifa, df_elo):

    df_teams = df_teams.copy()

    df_teams["team_merge"] = df_teams["Squad"].replace(NAME_MAPPING)

    df_merged = df_teams.merge(
        df_fifa,
        left_on="team_merge",
        right_on="team",
        how="left"
    ).drop(columns=["team"])

    df_final = df_merged.merge(
        df_elo,
        left_on="team_merge",
        right_on="team",
        how="left"
    )

    return df_final.sort_values("Squad").reset_index(drop=True)