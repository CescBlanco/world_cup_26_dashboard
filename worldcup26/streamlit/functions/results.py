import pandas as pd
import streamlit as st
from dateutil import parser

from services.scraper_whoscored import *
from services.scraper_match_fotmob import *


#----------------------------------------SUBTITLE------------------------------------------------------
def write_subtitle(text):
    st.markdown(f"<h5 style='text-align:center;'>{text}</h5>", unsafe_allow_html=True)

#---------------------------------------DATA MATCH INFO---------------------------------------
def extract_variables_team_info_details(team_info):
    home_team = team_info["name"].values[0]
    away_team = team_info["name"].values[1]

    homeScore = team_info["ft_score"].values[0]
    awayScore = team_info["ft_score"].values[1]

    et_score_home= team_info["et_score"].values[0]
    et_score_away= team_info["et_score"].values[1]

    penalty_score_home= team_info["penalty_score"].values[0]
    penalty_score_away= team_info["penalty_score"].values[1]

    manager_name_home= team_info["manager_name"].values[0]
    manager_name_away= team_info["manager_name"].values[1]
    initial_formation_home= team_info["initial_formation"].values[0]
    initial_formation_away= team_info["initial_formation"].values[1]


    average_age_home= team_info["average_age"].values[0]
    average_age_away= team_info["average_age"].values[1]

    initial_captain_id_home= team_info["initial_captain_id"].values[0]
    initial_captain_id_away= team_info["initial_captain_id"].values[1]


    

    return (home_team, away_team,homeScore, awayScore, et_score_home, et_score_away, penalty_score_home, penalty_score_away, manager_name_home,
            manager_name_away,initial_formation_home, initial_formation_away, average_age_home, average_age_away, initial_captain_id_home,
                initial_captain_id_away )
#------------------------------------------CARD MATCH OVERVIEW-----------------------------------
def card_match_overview(home_team,away_team,homeScore, awayScore, color_home, color_away ,texto_estado ):
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
                    homeScore=homeScore, awayScore=awayScore,
                    color_home=color_home, color_away=color_away, 
                    texto_estado=texto_estado), unsafe_allow_html=True)

#-----------------------------------------CARD PRINCIPAL TEAM----------------------------------
def principal_card_team(homePhoto,manager_name, initial_formation, average_age ):
    
        st.markdown(f"""
                    <div style='text-align:center;'>
                        <img src='{homePhoto}' width='90'><br>
                    </div>
                """, unsafe_allow_html=True)
        
        st.write('')

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
def card_formations_subs(player_team, initial_captain_id, selected_view):

    first_eleven = player_team[player_team["isFirstEleven"] == True]
    subs = player_team[player_team["isFirstEleven"] != True]

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
def card_substitutions(df, player_team):
    substitutions = df[df['subbedInPlayerId'].notna()]
    player_team["playerId"] = player_team["playerId"].astype(int)
    player_team["subbedInPlayerId"] = player_team["subbedInPlayerId"].astype("Int64")

    sub_map = player_team.copy()
    sub_map["playerId"] = sub_map["playerId"].astype(int)
    sub_map = sub_map.set_index("playerId")["name"]

    for _, jugador in substitutions.iterrows():

        minute = int(jugador.get("subbedOutExpandedMinute"))
        period = jugador.get("subbedOutPeriod")

        sub_in_id = int(jugador["subbedInPlayerId"])
        sub_in_name = sub_map.get(sub_in_id, "Unknown")

        st.markdown(
                f"""
                <div style="text-align:left; font-size:12.5px;">
                    <span style="color:#bbb;">{minute}' ({period}): </span>
                    <strong style="color:#fff;"> {jugador['name']} </strong>
                    <span style="color:#ff4d4d;"> ↓ </span>
                    |
                    <span style="color:#4caf50;"> ↑ </span>
                    <strong style="color:#fff;">{sub_in_name}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
#--------------------------------------------------MATCH EVENTS WHOSCORED------------------------------------
def prepare_df_events(matchdict, teams_dict_id_name):
    events_dict= matchdict['events']
    df = pd.DataFrame(events_dict)
    df['nameTeam'] = df['teamId'].map(teams_dict_id_name)
    df['type'] = df['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['outcomeType'] = df['outcomeType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['period'] = df['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    return df

#----------------------------------------------EVENTS KEYS MATCH-----------------------------------------
def create_inicidents_for_teams(matchdict, teams_dict_id_name,players_dict, side='home'):
    if side == 'home':
        incidents = pd.DataFrame(matchdict['home']['incidentEvents'])
    else:
        incidents = pd.DataFrame(matchdict['away']['incidentEvents'])
    
    incidents['nameTeam'] = incidents['teamId'].map(teams_dict_id_name)
    incidents['type'] = incidents['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    incidents['outcomeType'] = incidents['outcomeType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    incidents['period'] = incidents['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    incidents['cardType'] = incidents['cardType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    incidents = incidents[['minute', 'second',	'teamId' ,'playerId' ,'expandedMinute', 
                                    'period' ,'type', 'relatedPlayerId','cardType', 'nameTeam','qualifiers']].copy()

    def is_own_goal(qualifiers):
        return 'OwnGoal' in str(qualifiers)
    
    def is_penalty_event(qualifiers):
        if isinstance(qualifiers, list):
            return any(
                q.get('type', {}).get('displayName') == 'Penalty'
                for q in qualifiers
            )
        return False


    tipos_excluir = [ "FormationSet","FormationChange","SubstitutionOff","SubstitutionOn","Pass", 'Tackle', 'BallTouch']

    incidents = incidents[~incidents["type"].isin(tipos_excluir)].reset_index(drop=True).copy()
    incidents['player_name'] = incidents['playerId'].astype('Int64').astype(str).map(players_dict)

    incidents['player_name_related'] = incidents['relatedPlayerId'].astype('Int64').astype(str).map(players_dict)
    incidents['is_own_goal'] = incidents['qualifiers'].apply(is_own_goal)
    incidents= incidents.drop(columns=['playerId','relatedPlayerId'])

    incidents['is_shootout'] = incidents['period'] == 'PenaltyShootout'

    incidents['is_match_penalty'] = incidents.apply(lambda row: is_penalty_event(row['qualifiers']) if not row['is_shootout'] else False,axis=1)
    return incidents

def minute_display(row):

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
    if period == 'SecondHalf':

        # normal time
        if minute < 90:
            return str(minute + 1)
        if 89 <= minute < 91:
            return f"{minute +1}"

        # added time 
        return f"90+{minute - 90}"

def event_category(row):

    if row.get('is_shootout', False):
        return 'shootout_penalty'

    if row.get('is_match_penalty', False):
        return 'match_penalty'

    if row['type'] == 'Goal':
        return 'goal'

    if row['type'] == 'Card':
        return 'card'

    return 'other'

def create_events_keys(matchdict, teams_dict_id_name,players_dict,  home, away):
    incidents_home= create_inicidents_for_teams(matchdict, teams_dict_id_name,players_dict,  side='home')
    incidents_away= create_inicidents_for_teams(matchdict, teams_dict_id_name,players_dict,  side='away')

    df = pd.concat([incidents_home, incidents_away], axis=0)
    # separar shootout
    df_shootout = df[df['is_shootout']].copy()
    df_match = df[~df['is_shootout']].copy()

    # ordenar partido normal
    df_match = df_match.sort_values(['minute', 'second']).reset_index(drop=True)
    tipos_excluir = ["ShotOnPost", "SavedShot"]

    df_match = df_match[~df_match["type"].isin(tipos_excluir)].reset_index(drop=True).copy()
    df_shootout = (df_shootout[~df_shootout["type"].isin(tipos_excluir)]
                   .drop(columns=['player_name_related', 'cardType']).reset_index(drop=True).sort_values(by=['expandedMinute']) 
                   .copy())
    
    df_match['minute_display'] = df_match.apply(minute_display, axis=1)
    df_match['event_category'] = df_match.apply(event_category, axis=1)

    if df_shootout.empty:
        df_shootout = df_shootout.assign(minute_display=pd.Series(dtype=str),event_category=pd.Series(dtype=str))
    else:
        df_shootout['minute_display'] = df_shootout.apply( lambda r: minute_display(r),axis=1)

        df_shootout['event_category'] = df_shootout.apply(  lambda r: event_category(r),  axis=1)
    
    return df_match, df_shootout

def card_icon(card_type):
    if pd.isna(card_type):
        return "🟨🟥"

    card_type = str(card_type).lower()

    if "red" in card_type and "yellow" in card_type:
        return "🟨🟥"
    elif "red" in card_type:
        return "🟥"
    elif "yellow" in card_type:
        return "🟨"
    else:
        return "🟨🟥"

def minute_badge(minute_display):
                        
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
def render_event(row, home_team, away_team):
    
    icon = ""

    if row['event_category'] == 'goal':
        icon = "⚽"

    elif row['event_category'] == 'card':
        icon = card_icon(row['cardType'])

    elif row['event_category'] == 'match_penalty':
        icon = "⚽ (P)"

    return icon

def card_events_key_match(df_match, home_team,away_team):
                        
    ht_index = df_match.index[(df_match['period'].shift(1) == 'FirstHalf') &(df_match['period'] == 'SecondHalf')]


    for i, row in df_match.iterrows():
        # 🔥 HT LINE
        if i in ht_index:
            st.markdown("<p style='text-align:center; font-weight:bold; margin:10px 0;'>HT</p>", unsafe_allow_html=True)


        icon = render_event(row, home_team, away_team)

        # =========================
        # ⚽ GOAL + 🅰️ ASSIST
        # =========================
        if row['event_category'] == 'goal':

            main_text = f"{icon} {row['player_name']}"

            assist_text = ""
            if pd.notna(row.get('player_name_related')):
                assist_text = f"🅰️ {row['player_name_related']}"

            if row['nameTeam'] == home_team:

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

            if row['nameTeam'] == home_team:
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

def card_penalty_shootout(df_shootout, home_team,away_team  ):
    col_left,col_mid, col_right = st.columns([5,1,5])
    

    home_pen = df_shootout[df_shootout['nameTeam'] == home_team]
    away_pen = df_shootout[df_shootout['nameTeam'] == away_team]

    # 🔥 igualar longitudes para que no se descuadre
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

def parse_score(score_str):
    if not score_str:
        return None

    score_str = str(score_str).strip()

    if ' : ' not in score_str:
        return None

    clean_score = score_str.replace('*', '').strip()
    home, away = clean_score.split(' : ')

    return {'home': int(home), 'away': int(away)}

def get_result(score):
    if not score:
        return None

    if score['home'] > score['away']:
        return 'home'
    if score['home'] < score['away']:
        return 'away'
    return 'draw'

def extract_match_info_details(matchdict):
    def added_time(p):
        limit = period_limits.get(p)
        end = period_ends.get(p)

        if limit is None or end is None:
            return None

        return end - limit
    # -------------------------
    # SCORES
    # -------------------------
    score = parse_score(matchdict.get('score'))
    ht_score = parse_score(matchdict.get('htScore'))
    ft_score = parse_score(matchdict.get('ftScore'))
    et_score = parse_score(matchdict.get('etScore'))
    pk_score = parse_score(matchdict.get('pkScore'))

    ft_result = get_result(ft_score)
    et_result = get_result(et_score)
    pk_result = get_result(pk_score)

    # winner logic
    if pk_result:
        winner = pk_result
    elif et_result and et_result != 'draw':
        winner = et_result
    else:
        winner = ft_result

    # -------------------------
    # TIMING
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

def parse_team(team):
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
    


def extract_players_team(matchdict):
    player_home= pd.DataFrame(matchdict['home']['players'])
    player_home['subbedOutPeriod'] = player_home['subbedOutPeriod'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    player_home['subbedInPeriod'] = player_home['subbedInPeriod'].apply( lambda x: x['displayName'] if isinstance(x, dict) else None)

    player_away= pd.DataFrame(matchdict['away']['players'])
    player_away['subbedOutPeriod'] = player_away['subbedOutPeriod'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)

    player_away['subbedInPeriod'] = player_away['subbedInPeriod'].apply( lambda x: x['displayName'] if isinstance(x, dict) else None)
    
    return player_home,player_away

def formatear_fecha_segura(f):
    if isinstance(f, str):
        try:
            fecha_obj = parser.parse(f, dayfirst=True)  # Esto entiende '23-05-2025' y '2025-05-23'
            return fecha_obj.strftime('%d/%m/%Y')
        except:
            return f  # Si falla el parseo, lo deja igual
    return str(f)

def results_filtres(df):
        col0, col1, col2 = st.columns([1,1,1])
        
        stages = sorted(df['stageName'].dropna().unique().tolist())
        
        with st.container():
            # ---------------------------
            # 1. STAGE (OBLIGATORIO)
            # ---------------------------
            with col0:
                stage_selected = st.selectbox( "🏆 Select stage",stages, index=len(stages) - 1)

            # Filtrar DF por stage
            #df_stage = df[df["matchround"] == stage_selected]
            #id_stage= df["stageName"].iloc[0] if not df.empty else None

            # ---------------------------
            # 2. GROUP (DEPENDIENTE)
            # ---------------------------
            use_group_filter = st.checkbox("🔁 Filter by group")
            groups = sorted(df['stageName'].dropna().unique().tolist())
            group_selected = None
            df_filtered = df

            with col1:
                if use_group_filter:
                    group_selected = st.selectbox( "🔁 Select group", groups, index=len(groups) - 1 if len(groups) > 0 else 0 )
                    df_filtered = df[df["stageName"] == group_selected]
                else:
                    st.info("Group filter disabled")
            
            # ---------------------------
            # 3. DATE (DEPENDIENTE)
            # --------------------------- 
            fechas = sorted(df_filtered['match_date'].dropna().unique().tolist())
            fechas_formateadas = [formatear_fecha_segura(f) for f in fechas]


            with col2:
                fecha_elegida = None
                if len(fechas) > 0:
                    fecha_label = st.selectbox("📆 Select date", fechas_formateadas )

                    idx = fechas_formateadas.index(fecha_label)
                    fecha_elegida = fechas[idx]
                
            # ---------------------------
            # FILTRO FINAL
            # ---------------------------
            partidos = df_filtered.copy()

            if fecha_elegida:
                partidos = partidos[partidos["match_date"] == fecha_elegida]
            return partidos, stage_selected, group_selected, fecha_elegida
        
def match_list_post_filter(partidos, stage_selected, group_selected, fecha_elegida):
    
    if not partidos.empty:
        st.markdown(f"""
            <h3 style='margin-top: 1em; color: #999;'>
                ⚽ Stage: <span style='color:white;'>{stage_selected} ,</span>
                {f" Group: <span style='color:white;'>{group_selected}, </span>" if group_selected else "All groups, "}
                {f" Matches from <span style='color:white;'>{formatear_fecha_segura(fecha_elegida)}</span>" if fecha_elegida else ""}
            </h3>
        """, unsafe_allow_html=True)

    for _, row in partidos.iterrows():
        with st.container():
            from datetime import time
            hora = row.get("match_time")
            if isinstance(hora, time):
                hora_str = hora.strftime('%H:%M')
            elif isinstance(hora, str):
                hora_str = hora
            else:
                hora_str = "-"
            
            estado = f"🕒 {hora_str}"
            if pd.notna(row.get('elapsed')):
                estado = "✅ Completed"
            else :
                estado = "Not started"
            
            resultado = ( f"{row.get('homeScore')}-{row.get('awayScore')}"if pd.notna(row.get('homeScore'))
                            and pd.notna(row.get('awayScore'))else "vs")
            home_team = row.get('homeTeamName', '')
            away_team = row.get('awayTeamName', '')
            homeTeamPhoto = row.get('homeTeamPhoto', '')
            awayTeamPhoto = row.get('awayTeamPhoto', '')
            partido_url = row.get('url_match', '')
            clave = f"ver_{partido_url}"

            # Crea una fila con dos columnas: partido (izquierda), detalles (derecha)
            col1, col2 = st.columns([0.70, 0.35])

            with col1:
                partido_html = f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 15px;
                    padding: 1.5em;
                    margin-bottom: 1em;
                    background-color: transparent;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
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
                if pd.notna(row.get('winnerField')):
                    if st.button("🔍 View match details", key=clave):
                        if st.session_state.get("partido_mostrado") == partido_url:
                            del st.session_state["partido_mostrado"]
                        else:
                            st.session_state["partido_mostrado"] = partido_url
                    
                else:
                    st.markdown('<span style="color:gray">Details are not yet available.</span>', unsafe_allow_html=True)

def prepare_data_fotmob_cache(data):
    colors_teams_fotmob= pd.DataFrame(data['content']['matchFacts']['playerOfTheMatch']['teamData'])
    color_home = colors_teams_fotmob['home']['color']
    color_away = colors_teams_fotmob['away']['color']

    name_home_fotmob= pd.DataFrame(data['header']['teams'])['name'].values[0]
    name_away_fotmob= pd.DataFrame(data['header']['teams'])['name'].values[1]
    id_home_fotmob= int(pd.DataFrame(data['header']['teams'])['id'].values[0])
    id_away_fotmob= int(pd.DataFrame(data['header']['teams'])['id'].values[1])

    team_dict_fotmob = {id_home_fotmob: name_home_fotmob,id_away_fotmob: name_away_fotmob}

    return color_home, color_away,name_home_fotmob, name_away_fotmob, id_home_fotmob, id_away_fotmob, team_dict_fotmob

def prepare_data_whoscored_cache(url_match_preview):
    match_id_whoscored = extract_match_id(url_match_preview)

    cache_data = load_match_cache_whoscored(match_id_whoscored)
    if cache_data:
        st.success(f"🟢 Data loaded from CACHE WHOSCORED (match {match_id_whoscored})")

        formation_mappings = cache_data["formation_mappings"]
        event_types_json = cache_data["event_types_json"]
        matchdict = cache_data["matchdict"]
        players_dict = cache_data["players_dict"]

    else:
        with st.spinner("🟡 No cache. Scraping match data..."):
            formation_mappings, event_types_json, matchdict, players_dict = extract_match_dict_url(url_match_preview)

        save_match_cache_whoscored( match_id_whoscored, formation_mappings, event_types_json,
                                    matchdict, players_dict)
        st.success(f"🔵 Cache created successfully for match {match_id_whoscored}")

    return formation_mappings, event_types_json, matchdict, players_dict
