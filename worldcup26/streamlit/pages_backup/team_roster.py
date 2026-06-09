from functions.team_roster import *


def render_team_roster(df):

    team_header(df)

    players_only=team_sumary(df)

    star_players_mk_value(players_only)

    squad_by_postion(players_only)