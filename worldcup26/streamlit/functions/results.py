import pandas as pd
import streamlit as st

from datetime import datetime
from typing import Any


from services.scraper_whoscored import *
from services.scraper_match_fotmob import *


#----------------------------------------SUBTITLE------------------------------------------------------
def write_subtitle(text: str) -> None:
    """
    Render a centered subtitle in the Streamlit interface.

    This function displays a subtitle using custom HTML styling
    with centered alignment.

    Args:
        text (str): Subtitle text to display.

    Returns:
        None

    Raises:
        TypeError: If text is not a string.
    """

    # 🔹 Validate input type
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    st.markdown(
        f"<h5 style='text-align:center;'>{text}</h5>",
        unsafe_allow_html=True
    )

#---------------------------------------DATA MATCH INFO---------------------------------------
def extract_variables_team_info_details(
    team_info: pd.DataFrame
) -> tuple:
    """
    Extract key match and team information from a team details DataFrame.

    This function retrieves the most relevant match variables for both
    home and away teams, including scores, managers, formations,
    average age, and captain identifiers.

    Args:
        team_info (pd.DataFrame): Team information dataset containing
            match metadata.

    Returns:
        tuple:
            (
                home_team,
                away_team,
                home_score,
                away_score,
                et_score_home,
                et_score_away,
                penalty_score_home,
                penalty_score_away,
                manager_name_home,
                manager_name_away,
                initial_formation_home,
                initial_formation_away,
                average_age_home,
                average_age_away,
                initial_captain_id_home,
                initial_captain_id_away
            )

    Raises:
        TypeError: If team_info is not a DataFrame.
        KeyError: If required columns are missing.
        IndexError: If expected rows are unavailable.
    """

    # 🔹 Extract team names
    home_team = team_info["name"].values[0]
    away_team = team_info["name"].values[1]

    # 🔹 Full-time scores
    home_score = team_info["ft_score"].values[0]
    away_score = team_info["ft_score"].values[1]

    # 🔹 Extra-time scores
    et_score_home = team_info["et_score"].values[0]
    et_score_away = team_info["et_score"].values[1]

    # 🔹 Penalty shootout scores
    penalty_score_home = team_info["penalty_score"].values[0]
    penalty_score_away = team_info["penalty_score"].values[1]

    # 🔹 Managers
    manager_name_home = team_info["manager_name"].values[0]
    manager_name_away = team_info["manager_name"].values[1]

    # 🔹 Initial formations
    initial_formation_home = team_info["initial_formation"].values[0]
    initial_formation_away = team_info["initial_formation"].values[1]

    # 🔹 Average squad age
    average_age_home = team_info["average_age"].values[0]
    average_age_away = team_info["average_age"].values[1]

    # 🔹 Captains
    initial_captain_id_home = team_info["initial_captain_id"].values[0]
    initial_captain_id_away = team_info["initial_captain_id"].values[1]

    return ( home_team, away_team, home_score, away_score, et_score_home, et_score_away, penalty_score_home, penalty_score_away,manager_name_home, 
            manager_name_away, initial_formation_home, initial_formation_away, average_age_home, average_age_away, initial_captain_id_home, initial_captain_id_away)
#------------------------------------------CARD MATCH OVERVIEW-----------------------------------
def card_match_overview( home_team: str, away_team: str, home_score: int | float, away_score: int | float, color_home: str, color_away: str, match_status_text: str) -> None:
    """
    Render the main match overview card.

    This component displays:
    - Home and away team names
    - Match score
    - Custom team colors
    - Match status text

    Args:
        home_team (str): Home team name.
        away_team (str): Away team name.
        home_score (int | float): Home team score.
        away_score (int | float): Away team score.
        color_home (str): Home team display color.
        color_away (str): Away team display color.
        match_status_text (str): Additional match status text.

    Returns:
        None
    """
    st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; font-size: 28px; font-weight: bold;'>
                <span style='color:{color_home}; margin-right: 15px;'>{home_team}</span>
                <span style='color:white;'>{homeScore} : {awayScore}</span>
                <span style='color:{color_away}; margin-left: 15px;'>{away_team}</span>

            </div>
                <div style='display: flex; justify-content: center; align-items: center; color:#white; font-size:16px;'>
                    {texto_estado}
                </div>
            </div>
        """.format( home_team=home_team, away_team=away_team,
                    homeScore=home_score, awayScore=away_score,
                    color_home=color_home, color_away=color_away, 
                    texto_estado=match_status_text), unsafe_allow_html=True)

#-----------------------------------------CARD PRINCIPAL TEAM----------------------------------
def principal_card_team( team_photo: str, manager_name: str, initial_formation: str, average_age: float | int) -> None:       
        """
        Render the main team information card.

        This component displays:
        - Team image
        - Manager name
        - Initial formation
        - Average squad age

        Args:
            team_photo (str): Team logo or image URL.
            manager_name (str): Team manager name.
            initial_formation (str): Starting formation.
            average_age (float | int): Average squad age.

        Returns:
            None
        """

        # 🔹 Team image
        st.markdown(f"""
                    <div style='text-align:center;'>
                        <img src='{team_photo}' width='90'><br>
                    </div>
                """, unsafe_allow_html=True)
        
        st.write('')

        # 🔹 Team details
        st.markdown(
                f"""
                <p style='text-align:center; font-size:13px; margin:0; line-height:1.4;'>
                    Manager: {manager_name}<br>
                    Initial formation: {initial_formation} (Avg. age: {average_age})
                </p>
                """,
                unsafe_allow_html=True
            )
#-----------------------------------------CARD FORMATIONS/SUBS TEAMS-------------------------------
def card_formations_subs( player_team: pd.DataFrame, initial_captain_id: int | str, selected_view: str) -> pd.DataFrame:
    """
    Render either the starting lineup or substitutes list.

    Players are displayed with:
    - Shirt number
    - Player name
    - Position
    - Captain badge (if applicable)

    Args:
        player_team (pd.DataFrame): Team squad dataset.
        initial_captain_id (int | str): Captain player identifier.
        selected_view (str): View mode. Expected values:
            - "Starting XI"
            - "Substitutes"

    Returns:
        pd.DataFrame:
            DataFrame containing the starting eleven players.

    Raises:
        KeyError: If required columns are missing.
    """
    first_eleven = player_team[player_team["isFirstEleven"] == True]
    subs = player_team[player_team["isFirstEleven"] != True]

    # 🔹 Select players to display
    players_to_show = (first_eleven if selected_view == "Starting XI" else subs)

    st.markdown("<div style='padding-left:500px'>", unsafe_allow_html=True)

    for _, jugador in players_to_show.iterrows():

        es_capitan = jugador.get("playerId") == initial_captain_id
        icono_capitan = " 🟠 C" if es_capitan else ""

        st.markdown(
            f"""
            <p style='margin-top:10px; font-size:14px;'>
                <strong>#{jugador['shirtNo']}</strong>
                {jugador['name']}{icono_capitan}
                -
                <span style='color:gray;'>Position:</span>
                <strong>{jugador['position']}</strong>
            </p>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    return first_eleven

#-----------------------------------------CARD SUBSTITUTIONS TEAMS-----------------------------------------
def card_substitutions(matchdict: pd.DataFrame, teams_dict_id_name,
                         players_dict: dict) -> None:
    """
    Render substitution events for a team.
    """

    if matchdict.empty:
        st.info("No substitutions")
        return

    # Resolver nombres
    matchdict = matchdict.copy()
    matchdict['type'] = matchdict['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    matchdict['period'] = matchdict['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    matchdict['nameTeam'] = matchdict['teamId'].map(teams_dict_id_name)
    matchdict=matchdict[['minute', 'second', 'teamId', 'period'	,'type', 'relatedPlayerId', 'nameTeam']].copy()

    tipos_excluir = [ "FormationSet", "FormationChange", "Pass", "Goal", "Card"]
    matchdict = matchdict[~matchdict["type"].isin(tipos_excluir)].reset_index(drop=True).copy()
    
    matchdict["player_name"] = matchdict["relatedPlayerId"].astype("Int64").astype(str).map(players_dict)
    
    # Separar ON y OFF
    subs_off = matchdict[matchdict["type"] == "SubstitutionOff"].copy()

    subs_on = matchdict[ matchdict["type"] == "SubstitutionOn"].copy()

    # Evitar cruces cuando hay varias sustituciones simultáneas
    subs_off["sub_idx"] =  subs_off.groupby(["minute", "second", "teamId"]).cumcount()

    subs_on["sub_idx"] = subs_on.groupby(["minute", "second", "teamId"]).cumcount()
    subs = subs_off.merge( subs_on, on=["minute", "second", "teamId", "period", "sub_idx"],suffixes=("_off", "_on")
    )

    # Render
    for _, row in subs.iterrows():

        st.markdown(
            f"""
            <div style="text-align:left; font-size:12.5px;">
                <span style="color:#bbb;">{row['minute']}' ({row['period']}): </span>
                <strong style="color:#fff;">{row['player_name_on']}</strong>
                <span style="color:#ff4d4d;"> ↓ </span>
                |
                <span style="color:#4caf50;"> ↑ </span>
                <strong style="color:#fff;">{row['player_name_off']}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        
def prepare_df_events( matchdict: dict, teams_dict_id_name: dict) -> pd.DataFrame:
    """
    Convert raw WhoScored match events into a structured DataFrame.

    This function normalizes nested event attributes and enriches
    events with team names.

    Args:
        matchdict (dict): Match data dictionary obtained from
            WhoScored match center.
        teams_dict_id_name (dict): Mapping between team identifiers
            and team names.

    Returns:
        pd.DataFrame:
            Processed events DataFrame.

    Raises:
        TypeError: If inputs have invalid types.
        KeyError: If required keys are missing.
    """

    # 🔹 Validate input types
    if not isinstance(matchdict, dict):
        raise TypeError("matchdict must be a dictionary")

    if not isinstance(teams_dict_id_name, dict):
        raise TypeError(
            "teams_dict_id_name must be a dictionary"
        )

    if "events" not in matchdict:
        raise KeyError("events key not found in matchdict")

    # 🔹 Create events DataFrame
    events_df = pd.DataFrame(matchdict["events"])

    # 🔹 Map team names
    events_df["nameTeam"] = events_df["teamId"] .map(teams_dict_id_name)

    # 🔹 Normalize nested dictionaries
    events_df["type"] = events_df["type"].apply(lambda x:x["displayName"] if isinstance(x, dict) else None)

    events_df["outcomeType"] = events_df["outcomeType"].apply( lambda x: x["displayName"] if isinstance(x, dict) else None)

    events_df["period"] = events_df["period"].apply( lambda x: x["displayName"] if isinstance(x, dict) else None)

    return events_df
#----------------------------------------------EVENTS KEYS MATCH-----------------------------------------
def create_inicidents_for_teams(matchdict: dict,teams_dict_id_name: dict,players_dict: dict,side: str = "home") -> pd.DataFrame:
    """
    Create a processed incidents DataFrame for a specific team.

    This function extracts, enriches, and filters match incidents
    from the WhoScored match center dataset. It also identifies
    own goals, penalty events, and penalty shootout actions.

    Args:
        matchdict (dict): Match center data.
        teams_dict_id_name (dict): Team ID to team name mapping.
        players_dict (dict): Player ID to player name mapping.
        side (str, optional): Team side to extract incidents from.
            Allowed values:
            - "home"
            - "away"

    Returns:
        pd.DataFrame:
            Processed incidents dataset.

    Raises:
        TypeError: If input types are invalid.
        ValueError: If side is not valid.
        KeyError: If required match data is missing.
    """

    # 🔹 Validate side parameter
    if side not in ["home", "away"]:
        raise ValueError("side must be either 'home' or 'away'" )

    # 🔹 Extract incident events
    df = pd.DataFrame(  matchdict[side]["incidentEvents"])
    if 'cardType' not in df.columns:
        df['cardType'] = None
    # 🔹 Map team names
    df['nameTeam'] = df['teamId'].map(teams_dict_id_name)
    df['type'] = df['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['outcomeType'] = df['outcomeType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['period'] = df['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['cardType'] = df['cardType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)

    # 🔹 Keep only relevant columns
    df = df[["minute","second","teamId","playerId","expandedMinute","period","type","relatedPlayerId","cardType","nameTeam","qualifiers"]].copy()

    def is_own_goal(qualifiers: list | str) -> bool:
        """
        Identify own goal events.
        """
        return "OwnGoal" in str(qualifiers)

    def is_penalty_event( qualifiers: list | None) -> bool:
        """
        Identify penalty kick events.
        """

        if isinstance(qualifiers, list):

            return any( q.get("type", {}).get("displayName") == "Penalty" for q in qualifiers)

        return False

    # 🔹 Events not relevant for incident timeline
    excluded_event_types = ["FormationSet","FormationChange","SubstitutionOff","Error","Save","PenaltyFaced",
                            "SubstitutionOn","Pass","Tackle","BallTouch"]

    df = df[~df["type"].isin(excluded_event_types)].reset_index(drop=True).copy()

    # 🔹 Resolve player names
    df['player_name'] = df['playerId'].astype('Int64').astype(str).map(players_dict)

    df = df[
        ~((df['type'] == 'Card') & (df['player_name'].isna()))
    ].reset_index(drop=True)

    df['player_name_related'] = df['relatedPlayerId'].astype('Int64').astype(str).map(players_dict)

    # 🔹 Detect own goals
    df['is_own_goal'] = df['qualifiers'].apply(is_own_goal)

    df= df.drop(columns=['playerId','relatedPlayerId'])

    # 🔹 Detect shootout events
    df['is_shootout'] = df['period'] == 'PenaltyShootout'

    # 🔹 Detect match penalties
    df['is_match_penalty'] = df.apply(lambda row: is_penalty_event(row['qualifiers']) if not row['is_shootout'] else False,axis=1)

    return df


def minute_display(row: pd.Series) -> str:
    """
    Convert raw event minute information into a football-friendly
    display format.

    This function formats match minutes according to the match period,
    including first-half stoppage time, second-half stoppage time,
    and penalty shootouts.

    Args:
        row (pd.Series): Event row containing at least:
            - minute
            - period

    Returns:
        str:
            Formatted minute string.

            Examples:
            - "12"
            - "45+2"
            - "90+4"
            - "PEN"

    Raises:
        KeyError: If required fields are missing.
        ValueError: If minute cannot be converted to an integer.
    """

    # 🔹 Penalty shootout events
    if row['period'] == 'PenaltyShootout':
        return 'PEN'

    minute = int(row['minute'])
    period = row['period']

    # =========================
    # 🟢 FIRST HALF
    # =========================
    if period == 'FirstHalf':

        # normal time
        if minute < 45:
            return str(minute + 1)

        # added time
        return f"45+{minute - 45}"

    # =========================
    # 🔴 SECOND HALF
    # =========================
    elif period == 'SecondHalf':

        # normal time
        if minute < 90:
            return str(minute + 1)
        if 89 <= minute < 91:
            return f"{minute +1}"

        # added time 
        return f"90+{minute - 90}"

    elif period == 'FirstPeriodOfExtraTime':
        if minute < 105:
            return str(minute + 1)
        return f"105+{minute-105}"

    elif period == 'SecondPeriodOfExtraTime':
        if minute < 120:
            return str(minute + 1)
        return f"120+{minute-120}"
    return str(minute + 1)

def event_category(row: pd.Series) -> str:
    """
    Classify a match event into a simplified category.

    Categories are used for timeline rendering and icon selection.

    Args:
        row (pd.Series): Event row.

    Returns:
        str:
            Event category.

            Possible values:
            - "goal"
            - "card"
            - "match_penalty"
            - "shootout_penalty"
            - "other"
    """

    # 🔹 Penalty shootout event
    if row.get('is_shootout', False):
        return 'shootout_penalty'

    # 🔹 Match penalty

    if row['type'] == 'MissedShots' and row.get('is_match_penalty', False):
        return 'missed_penalty'
    
    if row.get('is_match_penalty', False):
        return 'match_penalty'

    if row['type'] == 'Goal':
        if row.get('is_match_penalty', False):
            return 'match_penalty'
        return 'goal'

    # 🔹 Card
    if row['type'] == 'Card':
        return 'card'

    return 'other'

def create_events_keys( matchdict: dict, teams_dict_id_name: dict, players_dict: dict, home: str, away: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build processed event datasets for timeline visualization.

    This function combines incidents from both teams, separates
    regular match events from penalty shootout events, classifies
    event types, and prepares display metadata.

    Args:
        matchdict (dict): Match center data.
        teams_dict_id_name (dict): Team ID mapping.
        players_dict (dict): Player ID mapping.
        home (str): Home team name.
        away (str): Away team name.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]:
            (
                match_events,
                penalty_shootout_events
            )

    Raises:
        TypeError: If input types are invalid.
        KeyError: If required match information is missing.
    """

    # 🔹 Extract incidents
    incidents_home= create_inicidents_for_teams(matchdict, teams_dict_id_name,players_dict,  side='home')
    incidents_away= create_inicidents_for_teams(matchdict, teams_dict_id_name,players_dict,  side='away')

    # 🔹 Combine both teams
    df = pd.concat([incidents_home, incidents_away], axis=0)

    # 🔹 Team used for rendering (own goals go to the opposite side)
    team_swap = {
        home: away,
        away: home
    }
    df['render_team'] = df['nameTeam']

    df.loc[
        df['is_own_goal'],
        'render_team'
    ] = df.loc[
        df['is_own_goal'],
        'nameTeam'
    ].map(team_swap)

    
    # 🔹 Split shootout events
    df_shootout = df[df['is_shootout']].copy()
    df_match = df[~df['is_shootout']].copy()

    # 🔹 Sort timeline
    df_match = df_match.sort_values(['minute', 'second']).reset_index(drop=True)
    
    tipos_excluir = ["ShotOnPost", "SavedShot"]
    df_match = df_match[~df_match["type"].isin(tipos_excluir)].reset_index(drop=True).copy()

    df_shootout = (df_shootout[~df_shootout["type"].isin(tipos_excluir)]
                   .drop(columns=['player_name_related', 'cardType']).reset_index(drop=True).sort_values(by=['expandedMinute']) 
                   .copy())
    
    # 🔹 Display metadata
    df_match['minute_display'] = df_match.apply(minute_display, axis=1)
    df_match['event_category'] = df_match.apply(event_category, axis=1)

    if df_shootout.empty:
        df_shootout = df_shootout.assign(minute_display=pd.Series(dtype=str),event_category=pd.Series(dtype=str))
    else:
        df_shootout['minute_display'] = df_shootout.apply( lambda r: minute_display(r),axis=1)

        df_shootout['event_category'] = df_shootout.apply(  lambda r: event_category(r),  axis=1)
    
    return df_match, df_shootout


def card_icon(card_type: str | None) -> str:
    """
    Return the appropriate card icon representation.

    Args:
        card_type (str | None): Card type description.

    Returns:
        str:
            Card icon.

            Examples:
            - 🟨
            - 🟥
            - 🟨🟥
    """

    
    if pd.isna(card_type):
        return "🟨🟥"

    card_type = str(card_type).lower()

    if "secondyellow" in card_type or "second yellow" in card_type:
        return "🟨🟥"

    if "red" in card_type and "yellow" in card_type:
        return "🟨🟥"

    elif "red" in card_type:
        return "🟥"

    elif "yellow" in card_type:
        return "🟨"

    return "🟨🟥"

def minute_badge(minute_display: str) -> str:
    """
    Generate an HTML badge displaying the match minute.

    Args:
        minute_display (str): Formatted minute text.

    Returns:
        str:
            HTML snippet representing the minute badge.
    """
                        
    return f"""
    <div style="
        background-color:#888;
        color:white;
        padding:3px 8px;
        border-radius:5px;
        font-size:12px;
        text-align:center;
        width:60px;
        margin:auto;">
        {minute_display}'
    </div>
    """

def render_event( row: pd.Series,home_team: str, away_team: str) -> str:
    """
    Determine the visual icon for a match event.

    Args:
        row (pd.Series): Event row.
        home_team (str): Home team name.
        away_team (str): Away team name.

    Returns:
        str:
            Event icon representation.
    """
    
    icon = ""

    if row['event_category'] == 'goal':
        icon = "⚽"

    elif row['event_category'] == 'card':
        icon = card_icon(row['cardType'])

    elif row['event_category'] == 'missed_penalty':
        icon = "❌ (P)"

    elif row['event_category'] == 'match_penalty':
        icon = "⚽ (P)"

    return icon

def card_events_key_match( df_match: pd.DataFrame, home_team: str, away_team: str) -> None:
    """
    Render the complete match timeline.

    Events are displayed chronologically with:
    - Goals
    - Assists
    - Cards
    - Penalties
    - Half-time separator

    Args:
        df_match (pd.DataFrame): Processed match events.
        home_team (str): Home team name.
        away_team (str): Away team name.

    Returns:
        None

    Raises:
        TypeError: If df_match is not a DataFrame.
    """

    # 🔹 Detect parts match transition             
    period_labels = {
        ('FirstHalf', 'SecondHalf'): 'HT',
        ('SecondHalf', 'FirstPeriodOfExtraTime'): 'AET',
        ('SecondHalf', 'SecondPeriodOfExtraTime'): 'AET',
        ('FirstHalf', 'FirstPeriodOfExtraTime'): 'AET', 
        ('FirstPeriodOfExtraTime', 'SecondPeriodOfExtraTime'): 'AET HT',
    }

    # 🔹 Render event timeline
    for i, row in df_match.iterrows():

        if i > 0:
            previous_period = df_match.loc[i-1, 'period']
            current_period = row['period']

            label = period_labels.get((previous_period, current_period))

            if label:
                st.markdown(
                    f"<p style='text-align:center; font-weight:bold; margin:10px 0;'>{label}</p>",
                    unsafe_allow_html=True
                )


        icon = render_event(row, home_team, away_team)

        # =========================
        # ⚽ GOAL + 🅰️ ASSIST
        # =========================
        if row['event_category'] == 'goal':

            if row['is_own_goal']:
                main_text = f"{icon} {row['player_name']} (OG)"
            else:
                main_text = f"{icon} {row['player_name']}"

            assist_text = ""
            if pd.notna(row.get('player_name_related')):
                assist_text = f"🅰️ {row['player_name_related']}"

            if row['render_team'] == home_team:

                left = f"""
                <div style='text-align: right; line-height:1.2;font-size:13px '>
                    <div>{main_text}</div>
                    <div style='font-size:13px; color:gray;'>{assist_text}</div>
                </div>
                """
                right = ""

            else:

                left = ""
                right = f"""
                <div style='text-align:left; line-height:1.2;font-size:13px '>
                    <div>{main_text}</div>
                    <div style='font-size:13px; color:gray;'>{assist_text}</div>
                </div>
                """

        # =========================
        # 🟨🟥 CARDS / 🔁 / OTROS
        # =========================
        else:

            text = f"{icon} {row['player_name']}"

            if row['render_team'] == home_team:
                left = f"<p style='text-align:right; font-size:13px '>{text}</p>"
                right = ""

            else:
                left = ""
                right = f"<p style='text-align:left; font-size:13px'>{text}</p>"

        # =========================
        # 🧱 RENDER COLUMNS
        # =========================
        col_left, col_mid, col_right = st.columns([5, 1, 5])

        with col_left:
            st.markdown(left, unsafe_allow_html=True)

        with col_mid:
            st.markdown(minute_badge(row['minute_display']), unsafe_allow_html=True)

        with col_right:
            st.markdown(right, unsafe_allow_html=True)

def card_penalty_shootout( df_shootout: pd.DataFrame, home_team: str, away_team: str) -> None:
    """
        Render penalty shootout results.

        This component displays penalty attempts side-by-side
        for both teams using goal and miss indicators.

        Args:
            df_shootout (pd.DataFrame): Penalty shootout events.
            home_team (str): Home team name.
            away_team (str): Away team name.

        Returns:
            None

        Raises:
            TypeError: If df_shootout is not a DataFrame.
        """
     # 🔹 Create layout columns
    col_left,col_mid, col_right = st.columns([5,1,5])
    
    # 🔹 Split penalties by team
    home_pen = df_shootout[df_shootout['nameTeam'] == home_team]
    away_pen = df_shootout[df_shootout['nameTeam'] == away_team]

    # 🔹 Align shootout attempts
    max_len = max(len(home_pen), len(away_pen))

    home_list = home_pen.to_dict('records')
    away_list = away_pen.to_dict('records')
    
    with col_mid:
            st.markdown(
            f"<div style='text-align:center; margin:10px 0;  font-size:13px '>{minute_badge('PEN')}</div>",
            unsafe_allow_html=True
        )
            
    for i in range(max_len):

        left = ""
        right = ""

        if i < len(home_list):
            r = home_list[i]
            icon = "⚽" if r['type'] == 'Goal' else "❌"
            left = f"{icon} {r['player_name']}"

        if i < len(away_list):
            r = away_list[i]
            icon = "⚽" if r['type'] == 'Goal' else "❌"
            right = f"{icon} {r['player_name']}"

        with col_left:
            st.markdown(f"<p style='text-align:right; margin:0;  font-size:13px '>{left}</p>", unsafe_allow_html=True)
        
        with col_right:
            st.markdown(f"<p style='text-align:left; margin:0;  font-size:13px '>{right}</p>", unsafe_allow_html=True)
            
#------------------------------------------------------------------------------------

def parse_score(score_str: str | None) -> dict[str, int] | None:
    """
    Parse a score string into a dictionary containing home and away goals.

    Expected format:
        "2 : 1"
        "3* : 3"  (asterisks are removed automatically)

    Args:
        score_str (str | None):
            Score string in the format "home : away".

    Returns:
        dict[str, int] | None:
            Dictionary with:
                - home (int): Home team goals.
                - away (int): Away team goals.
            Returns None if the score string is empty, invalid,
            or does not match the expected format.

    Raises:
        TypeError:
            If score_str is not a string or None.
        ValueError:
            If score values cannot be converted to integers.
    """

    # Validate empty values
    if not score_str:
        return None

    if not isinstance(score_str, str):
        raise TypeError("score_str must be a string or None")
    
    score_str = str(score_str).strip()

    # Expected separator format
    if ' : ' not in score_str:
        return None

    clean_score = score_str.replace('*', '').strip()
    try:
        home, away = clean_score.split(" : ")
        return {"home": int(home), "away": int(away)}
    except ValueError as exc:
        raise ValueError(f"Invalid score format: {score_str}") from exc


def get_result(score: dict[str, int] | None) -> str | None:
    """
    Determine the match result based on a score dictionary.

    Args:
        score (dict[str, int] | None):
            Dictionary containing:
                - home (int)
                - away (int)

    Returns:
        str | None:
            One of:
                - "home" if the home team won.
                - "away" if the away team won.
                - "draw" if the match ended level.
                - None if score is None.

    Raises:
        TypeError:
            If score is not a dictionary or None.
        KeyError:
            If required keys are missing.
    """
    if not score:
        return None
    
    if not isinstance(score, dict):
        raise TypeError("score must be a dictionary or None")

    if score['home'] > score['away']:
        return 'home'
    if score['home'] < score['away']:
        return 'away'
    return 'draw'

def extract_match_info_details(matchdict: dict) -> dict:
    """
    Extract detailed match information from a WhoScored match dictionary.

    This function parses scores, match results, venue information,
    match timing, stoppage time, extra time, penalties, and duration
    metrics into a structured dictionary.

    Args:
        matchdict (dict):
            Raw match data returned by WhoScored.

    Returns:
        dict:
            Structured match information containing:

            - Scores (HT, FT, ET, PK)
            - Match results
            - Winner
            - Venue information
            - Attendance
            - Referee
            - Match duration metrics
            - Added time statistics
            - Extra time and penalties flags

    Raises:
        TypeError:
            If matchdict is not a dictionary.
        KeyError:
            If required match fields are missing.
        ValueError:
            If score parsing fails.
    """
    if not isinstance(matchdict, dict):
        raise TypeError("matchdict must be a dictionary")
    
    def added_time(period: str) -> int | None:
        """
        Calculate stoppage time for a specific period.

        Args:
            period (str):
                Match period identifier.

        Returns:
            int | None:
                Added time in minutes or None if unavailable.
        """
        limit = period_limits.get(period)
        end = period_ends.get(period)

        if limit is None or end is None:
            return None

        return end - limit
    
    # -------------------------
    # Parse score structures
    # -------------------------
    score = parse_score(matchdict.get('score'))
    ht_score = parse_score(matchdict.get('htScore'))
    ft_score = parse_score(matchdict.get('ftScore'))
    et_score = parse_score(matchdict.get('etScore'))
    pk_score = parse_score(matchdict.get('pkScore'))

    ft_result = get_result(ft_score)
    et_result = get_result(et_score)
    pk_result = get_result(pk_score)

    # Determine final winner priority:
    # Penalties > Extra Time > Full Time
    if pk_result:
        winner = pk_result
    elif et_result and et_result != 'draw':
        winner = et_result
    else:
        winner = ft_result

    # -------------------------
    # Match timing information
    # -------------------------
    period_limits = matchdict.get('periodMinuteLimits', {})
    period_ends = matchdict.get('periodEndMinutes', {})

    max_period = str(matchdict.get('maxPeriod', 2))

    first_half_added_time = added_time('1')
    second_half_added_time = added_time('2')
    extra_first_half_added_time = added_time('3')
    extra_second_half_added_time = added_time('4')

    total_added_time = sum(added_time(p) or 0 for p in period_limits.keys())
    # -------------------------
    # MATCH INFO
    # -------------------------
    match_info = {
        # basic info
        'start_time': matchdict.get('startTime'),
        'elapsed': matchdict.get('elapsed'),

        # scores
        'score': score,
        'ht_score': ht_score,
        'ft_score': ft_score,
        'et_score': et_score,
        'pk_score': pk_score,

        # results
        'match_result': {
            'full_time': ft_result,
            'extra_time': et_result,
            'penalties': pk_result,
            'winner': winner
        },

        # venue
        'venue_name': matchdict.get('venueName'),
        'attendance': matchdict.get('attendance'),
        'referee': matchdict.get('referee'),

        # timing structure
        'max_period': matchdict.get('maxPeriod'),
        'max_minute': matchdict.get('maxMinute'),
        'expanded_max_minute': matchdict.get('expandedMaxMinute'),

        # flags
        'has_extra_time': matchdict.get('maxPeriod', 2) > 2,
        'has_penalties': bool(pk_score),

        # stoppage time
        'first_half_added_time': first_half_added_time,
        'second_half_added_time': second_half_added_time,
        'extra_first_half_added_time': extra_first_half_added_time,
        'extra_second_half_added_time': extra_second_half_added_time,

        # totals
        'total_added_time': total_added_time,

        # duration
        'actual_match_duration': matchdict.get('maxMinute'),

        'scheduled_match_duration': period_limits.get(
            max_period,
            120 if int(max_period) > 2 else 90
        )
    }
    return match_info

def parse_team(team: dict) -> dict:
        """
        Extract and normalize team information from a WhoScored team object.

        Args:
            team (dict):
                Team dictionary from match data.

        Returns:
            dict:
                Structured team information including:

                - Team identifiers
                - Team name
                - Manager information
                - Average age
                - Score breakdown
                - Formation information
                - Captain identifier

        Raises:
            TypeError:
                If team is not a dictionary.
        """
        if not isinstance(team, dict):
            raise TypeError("team must be a dictionary")

        formations = team.get('formations') or []
        first_formation = formations[0] if len(formations) > 0 else {}

        return {
            'team_id': team.get('teamId'),
            'h_a': team.get('field'),
            'name': team.get('name'),
            'country_name': team.get('countryName'),
            'manager_name': team.get('managerName'),
            'average_age': team.get('averageAge'),

            # scores
            'ht_score': team.get('scores', {}).get('halftime'),
            'ft_score': team.get('scores', {}).get('fulltime'),
            'running_score': team.get('scores', {}).get('running'),
            'et_score': team.get('scores', {}).get('extratime'),
            'penalty_score': team.get('scores', {}).get('penalty'),

            # formation
            'initial_formation': first_formation.get('formationName'),
            'initial_captain_id': first_formation.get('captainPlayerId'),

        }
    


def extract_players_team(matchdict: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract home and away player datasets from match data.

    This function converts player collections into DataFrames and
    normalizes substitution period fields.

    Args:
        matchdict (dict):
            Match dictionary containing home and away team data.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]:
            A tuple containing:

            - Home team players DataFrame.
            - Away team players DataFrame.

    Raises:
        TypeError:
            If matchdict is not a dictionary.
        KeyError:
            If home or away player information is missing.
    """
    if not isinstance(matchdict, dict):
        raise TypeError("matchdict must be a dictionary")

    # Home team players
    df_home= pd.DataFrame(matchdict['home']['players'])
    df_home['subbedOutPeriod'] = df_home['subbedOutPeriod'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df_home['subbedInPeriod'] = df_home['subbedInPeriod'].apply( lambda x: x['displayName'] if isinstance(x, dict) else None)

    # Away team players
    df_away= pd.DataFrame(matchdict['away']['players'])
    df_away['subbedOutPeriod'] = df_away['subbedOutPeriod'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df_away['subbedInPeriod'] = df_away['subbedInPeriod'].apply( lambda x: x['displayName'] if isinstance(x, dict) else None)
    
    return df_home,df_away

def formatear_fecha_segura(f: Any) -> str:
    """
    Safely format a date value into DD/MM/YYYY format.

    This function attempts to parse string dates using dateutil.parser
    and convert them into a standardized format. If parsing fails,
    the original value is returned as a string.

    Args:
        f (Any):
            Date value to format. Can be a string, datetime object,
            or any other type.

    Returns:
        str:
            Formatted date string in DD/MM/YYYY format if parsing succeeds.
            Otherwise, the original value converted to string.

    Raises:
        TypeError:
            If the provided value cannot be converted to string.
    """
    if isinstance(f, str):
        try:
            # Supports multiple formats such as:
            # - 23-05-2025
            # - 2025-05-23
            fecha_obj = datetime.strptime(f, "%Y-%m-%d")
            return fecha_obj.strftime("%d/%m/%Y")
        
        except Exception:
            # Return original value when parsing fails
            return f  # Si falla el parseo, lo deja igual
    return str(f)

def results_filtres(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str | None, Any]:
        """
        Render fixture filters and return the filtered dataset.

        Available filters:
            - Tournament stage
            - Group (optional)
            - Match date

        Args:
            df (pd.DataFrame):
                DataFrame containing fixture information.

        Returns:
            tuple:
                (
                    pd.DataFrame,  # Filtered matches
                    str,           # Selected stage
                    str | None,    # Selected group
                    Any            # Selected date
                )

        Raises:
            TypeError:
                If df is not a pandas DataFrame.

            KeyError:
                If required columns are missing:
                    - stageName
                    - match_date

            ValueError:
                If no stages are available in the dataset.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        col0, col1, col2 = st.columns([1,1,1])
        
        with st.container():
            # ---------------------------
            # Stage filter
            # ---------------------------
            with col0:
                from zoneinfo import ZoneInfo

                hoy = pd.Timestamp.now(tz=ZoneInfo("Europe/Madrid")).normalize().tz_localize(None)
                stages = sorted(df['matchround'].dropna().unique().tolist())
                if not stages:
                    raise ValueError("No stages available in dataframe")
                
                 # Buscar stage que contiene la fecha de hoy
                stage_por_defecto = stages[0]

                for stage in stages:
                    fechas_stage = pd.to_datetime(
                        df.loc[df["matchround"] == stage, "match_date"]
                    ).dt.normalize()
                    
                    if hoy in fechas_stage.values:
                        stage_por_defecto = stage
                        break

                indice_stage = stages.index(stage_por_defecto)
                
                stage_selected = st.selectbox( "🏆 Select stage",stages, index=indice_stage)
                df_filtered_stage_selected = df[df["matchround"] == stage_selected]

            # NOTE:
            # The current implementation stores the selected stage
            # but does not directly filter the dataframe using it.

            id_stage= df_filtered_stage_selected["round_id"].iloc[0]
            # ---------------------------
            # Group filter
            # ---------------------------
            use_group_filter = st.checkbox("🔁 Filter by group")
            groups = sorted(df_filtered_stage_selected['stageName'].dropna().unique().tolist())
            group_selected = None
            df_filtered = df_filtered_stage_selected

            with col1:
                if use_group_filter:
                    group_selected = st.selectbox( "🔁 Select group", groups, index=len(groups) - 1 if len(groups) > 0 else 0 )
                    df_filtered = df_filtered[df_filtered["stageName"] == group_selected]
                else:
                    st.info("Group filter disabled")
            
            # ---------------------------
            # Date filter
            # --------------------------- 
            fechas = sorted(df_filtered['match_date'].dropna().unique().tolist())
            fechas_formateadas = [formatear_fecha_segura(f) for f in fechas]       

            with col2:
                fecha_elegida = None
                if len(fechas) > 0:
                    
                    indice_hoy = min( range(len(fechas)), key=lambda i: abs(pd.Timestamp(fechas[i]).normalize() - hoy))
                    fecha_label = st.selectbox("📆 Select date", fechas_formateadas, index=indice_hoy)

                    idx = fechas_formateadas.index(fecha_label)
                    fecha_elegida = fechas[idx]
                
            # ---------------------------
            # Final filtering
            # ---------------------------
            partidos = df_filtered.copy()

            if fecha_elegida:
                partidos = partidos[partidos["match_date"] == fecha_elegida]

            partidos["match_datetime_sort"] = pd.to_datetime(
                partidos["match_date"].astype(str) + " " + partidos["match_time"].astype(str),
                errors="coerce"
            )

            partidos = partidos.sort_values("match_datetime_sort", ascending=True)
            
            return partidos, stage_selected, group_selected, fecha_elegida, id_stage
        
def match_list_post_filter(partidos: pd.DataFrame,stage_selected: str,group_selected: str | None,fecha_elegida: Any,id_stage : str) -> None:
    """
    Render the list of matches after applying filters.

    Displays:
        - Match status
        - Teams and logos
        - Match result
        - Match time
        - Match details button

    Args:
        partidos (pd.DataFrame):
            Filtered matches dataframe.

        stage_selected (str):
            Selected competition stage.

        group_selected (str | None):
            Selected group filter.

        fecha_elegida (Any):
            Selected match date.

    Returns:
        None

    Raises:
        TypeError:
            If partidos is not a pandas DataFrame.

        KeyError:
            If required match columns are missing.
    """
    if not isinstance(partidos, pd.DataFrame):
        raise TypeError( "partidos must be a pandas DataFrame")
    # Mostrar nombre del stage
    if int(id_stage) <= 3:
        stage_display = id_stage
    else:
        stage_display = stage_selected
    # Display filter summary
    if not partidos.empty:
        st.markdown(f"""
            <h3 style='margin-top: 1em; color: #999;'>
                ⚽ Stage: <span style='color:white;'>{stage_display} ,</span>
                {f" Group: <span style='color:white;'>{group_selected}, </span>" if group_selected else "All groups, "}
                {f" Matches from <span style='color:white;'>{formatear_fecha_segura(fecha_elegida)}</span>" if fecha_elegida else ""}
            </h3>
        """, unsafe_allow_html=True)
    # ------------------------------------
    # Autoabrir si solo hay 1 partido jugado
    # ------------------------------------
    partidos_finalizados = partidos[ partidos["status"] == 6]

    if len(partidos_finalizados) == 1:

        url_unica = partidos_finalizados.iloc[0]["url_match"]

        if  st.session_state.get("partido_mostrado") != url_unica:
            st.session_state["partido_mostrado"] = url_unica

    elif len(partidos_finalizados) > 1:

        partido_actual = st.session_state.get("partido_mostrado")

        if ( partido_actual is not None and partido_actual not in partidos["url_match"].values):
            st.session_state.pop("partido_mostrado", None )     

    for _, row in partidos.iterrows():
        with st.container():

            from datetime import time

            # ---------------------------
            # Match time formatting
            # ---------------------------
            hora = row.get("match_time")
            if isinstance(hora, time):
                hora_str = hora.strftime('%H:%M')
            elif isinstance(hora, str):
                hora_str = hora
            else:
                hora_str = "-"
            
            # ---------------------------
            # Match status
            # ---------------------------
            if row.get('status')==6:
                estado = "✅ Completed"

            elif row.get('status')==3:
                estado= "🔴 Live"
            else :
                estado = f"🕒 Scheduled ({hora_str})"
            
            # ---------------------------
            # Match score
            # ---------------------------
            resultado = ("vs" if row.get("status") == 3 else ( f"{int(row.get('homeScore'))}-{int(row.get('awayScore'))}"
                    if pd.notna(row.get('homeScore')) and pd.notna(row.get('awayScore')) else "vs"))
            
            home_team = row.get('homeTeamName', '')
            away_team = row.get('awayTeamName', '')
            homeTeamPhoto = row.get('homeTeamPhoto', '')
            awayTeamPhoto = row.get('awayTeamPhoto', '')
            partido_url = row.get('url_match', '')
            clave = f"ver_{partido_url}"

            # Layout:
            # Left -> Match card
            # Right -> Details button
            col1, col2 = st.columns([0.70, 0.35])

            with col1:
                partido_abierto = (
                    st.session_state.get("partido_mostrado")
                    == partido_url
                )

                card_border = (
                    "2px solid #4CAF50"
                    if partido_abierto
                    else "1px solid #e0e0e0"
                )

                card_shadow = (
                    "0 0 12px rgba(76,175,80,0.25)"
                    if partido_abierto
                    else "2px 2px 8px rgba(0,0,0,0.05)"
                )

                card_background = (
                    "rgba(76,175,80,0.05)"
                    if partido_abierto
                    else "transparent"
                )

                partido_html = f"""
                <div style="
                        border: {card_border};
                        border-radius: 15px;
                        padding: 1.5em;
                        margin-bottom: 1em;
                        background-color: {card_background};
                        box-shadow: {card_shadow};
                    ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 14px; color: #999;">{estado}</div>
                        <div style="text-align: center; flex: 1;">
                            <img src="{homeTeamPhoto}" width="30" style="vertical-align: middle;">
                            <strong style="margin: 0 1em; font-size: 18px;">{home_team}</strong>
                            <span style="font-size: 16px; font-weight: bold; color: #999;">{resultado}</span>
                            <strong style="margin: 0 1em; font-size: 18px;">{away_team}</strong>
                            <img src="{awayTeamPhoto}" width="30" style="vertical-align: middle;">
                        </div>
                    </div>
                </div>
                """
                st.markdown(partido_html, unsafe_allow_html=True)

            with col2:

                status = row.get("status")
                partido_jugado = status == 6
                # Match details are only available once a winner field exists.

                if partido_jugado:

                    varios_partidos = len(partidos_finalizados) > 1

                    partido_abierto = st.session_state.get("partido_mostrado")== partido_url
                
                    if varios_partidos:

                        if partido_abierto:

                            if st.button(  "❌ Hide details", key=f"hide_{clave}"):

                                st.session_state.pop("partido_mostrado",None) 
                                st.rerun()

                        else:
                            if st.button("🔍 View match details", key=clave):

                                st.session_state[ "partido_mostrado"] = partido_url
                                st.rerun()

                    else:

                        pass

                else:

                    st.markdown(
                        """
                        <span style="color:gray">
                            Details are not yet available.
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

def get_valid_color(team: str,current_color: str,team_colors: dict[str, Any]) -> str:
    """
    Return a valid team color, replacing invalid FotMob colors.

    FotMob occasionally returns '#000000' as a placeholder or
    incorrect team color. When this occurs, the function attempts
    to retrieve a valid color from the lightMode configuration and,
    if necessary, from the darkMode configuration.

    Priority order:
        1. current_color
        2. lightMode[team]
        3. darkMode[team]

    Args:
        team (str):
            Team side identifier ('home' or 'away').

        current_color (str):
            Color obtained from the matchFacts section.

        team_colors (dict[str, Any]):
            Team color configuration from:
            data['data']['general']['teamColors']

    Returns:
        str:
            A valid hexadecimal color string.

    Raises:
        TypeError:
            If team is not a string or team_colors is not a dictionary.

        ValueError:
            If team is not 'home' or 'away'.
    """
    if not isinstance(team, str):
        raise TypeError("team must be a string")

    if not isinstance(team_colors, dict):
        raise TypeError("team_colors must be a dictionary")

    if team not in {"home", "away"}:
        raise ValueError("team must be either 'home' or 'away'")

    invalid_colors = {'#000000', '#100f10'}
    current_color = (current_color or '').lower()
    
    # Current color is valid
    if current_color not in invalid_colors:
        return current_color

    # Try light mode
    light_color = team_colors.get('lightMode', {}).get(team)

    if light_color and light_color.lower() not in invalid_colors:
        return light_color

    # Try dark mode
    dark_color = team_colors.get('darkMode', {}).get(team)

    if dark_color and dark_color.lower() not in invalid_colors:
        return dark_color

    # Fallback
    return current_color

def prepare_data_fotmob_cache( data: dict[str, Any]) -> tuple[str,str,str,str,int,int,dict[int, str]]:
    """
    Extract and prepare FotMob match metadata from cached data.

    This function retrieves team colors, team names, team IDs,
    and builds a team ID-to-name mapping dictionary from the
    FotMob match response structure.

    Args:
        data (dict[str, Any]):
            FotMob match JSON response.

    Returns:
        tuple:
            (
                str,             # Home team color
                str,             # Away team color
                str,             # Home team name
                str,             # Away team name
                int,             # Home team ID
                int,             # Away team ID
                dict[int, str]   # Team ID → Team name mapping
            )

    Raises:
        TypeError:
            If data is not a dictionary.

        KeyError:
            If required FotMob fields are missing.

        ValueError:
            If team identifiers cannot be converted to integers.
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    
    # Extract team color information
    colors_teams_fotmob= pd.DataFrame(data['content']['matchFacts']['playerOfTheMatch']['teamData'])
    color_home = colors_teams_fotmob['home']['color']
    color_away = colors_teams_fotmob['away']['color']

    # Replace invalid FotMob colors using team color configuration
    team_colors = data['general']['teamColors']
    color_home = get_valid_color('home', color_home, team_colors)
    color_away = get_valid_color('away', color_away, team_colors)

    # Extract team metadata
    name_home_fotmob= pd.DataFrame(data['header']['teams'])['name'].values[0]
    name_away_fotmob= pd.DataFrame(data['header']['teams'])['name'].values[1]
    id_home_fotmob= int(pd.DataFrame(data['header']['teams'])['id'].values[0])
    id_away_fotmob= int(pd.DataFrame(data['header']['teams'])['id'].values[1])

    match_id = data["general"]["matchId"]
    if match_id == '4653856':
        if name_home_fotmob == "England":
            color_home = "#FFFFFF"
        elif name_away_fotmob == "England":
            color_away = "#FFFFFF"
    # Create lookup dictionary
    team_dict_fotmob = {id_home_fotmob: name_home_fotmob,id_away_fotmob: name_away_fotmob}

    return color_home, color_away,name_home_fotmob, name_away_fotmob, id_home_fotmob, id_away_fotmob, team_dict_fotmob

def prepare_data_whoscored_cache( url_match_preview: str) -> tuple[dict, dict, dict, dict]:
    """
    Load WhoScored match data from cache or scrape it if unavailable.

    This function checks whether the requested match data exists
    in the local cache. If cached data is found, it is loaded
    directly. Otherwise, the match page is scraped and the
    resulting data is stored in the cache for future use.

    Args:
        url_match_preview (str):
            WhoScored match URL.

    Returns:
        tuple[dict, dict, dict, dict]:
            (
                formation_mappings,
                event_types_json,
                matchdict,
                players_dict
            )

    Raises:
        TypeError:
            If url_match_preview is not a string.

        ValueError:
            If a match ID cannot be extracted from the URL.

        RuntimeError:
            If scraping fails or cache creation cannot be completed.

        KeyError:
            If required cached keys are missing.
    """

    if not isinstance(url_match_preview, str):
        raise TypeError("url_match_preview must be a string")

    # Extract match identifier from URL
    match_id_whoscored = extract_match_id(url_match_preview)

    if not match_id_whoscored:
        raise ValueError("Could not extract match ID from URL")

    # Attempt cache retrieval
    cache_data = load_match_cache_whoscored(match_id_whoscored)
    if cache_data:
        #st.badge(f"🟢 Data loaded from CACHE WHOSCORED (match {match_id_whoscored})", color="green")

        formation_mappings = cache_data["formation_mappings"]
        event_types_json = cache_data["event_types_json"]
        matchdict = cache_data["matchdict"]
        players_dict = cache_data["players_dict"]

    else:
        with st.badge("🟡 No cache. Scraping match data...",color="yellow"):
            formation_mappings, event_types_json, matchdict, players_dict = extract_match_dict_url(url_match_preview)

        # Save newly scraped data
        save_match_cache_whoscored( match_id_whoscored, formation_mappings, event_types_json,
                                    matchdict, players_dict)
        #st.badge(f"🔵 Cache created successfully for match {match_id_whoscored}",  color="blue")

    return formation_mappings, event_types_json, matchdict, players_dict