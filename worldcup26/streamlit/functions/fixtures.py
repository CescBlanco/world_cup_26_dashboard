import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
from concurrent.futures import ThreadPoolExecutor
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from utils.mapping import NAME_MAPPING2

def safe_str(val):
    return "" if pd.isna(val) else str(val)

def safe_int(x):
    try:
        if pd.isna(x):
            return None
        return int(float(x))
    except:
        return None
    
def safe_image(url):
    if url and url != "None" and url != "":
        st.image(url, width=90)
    else:
        st.write("📷  Photo not available")
    
def match_status(row: pd.Series) -> str:
    """
    Determine the status of a match based on score availability.

    A match is considered:
    - "played" if status is 6
    - "played" if status is 3
    - "scheduled" otherwise

    Args:
        row (pd.Series): Match row containing score information.

    Returns:
        str: Match status ("played", "live, or "scheduled").

    Raises:
        KeyError: If required columns are missing.
    """

    # 🔹 Match already played if both scores exist
    if row.get("status") == 3:
        return "live"

    elif row.get("status") == 6:
        return "played"

    else:
        return "scheduled"

def build_event(row: pd.Series) -> dict:
    """
    Build a calendar event object from a match row.

    This function converts a match record into a structured event
    compatible with calendar visualizations. It includes:
    - Match title (dynamic depending on status)
    - Start datetime in ISO format
    - Styling (color based on status)
    - Extended metadata for tooltips/UI

    Args:
        row (pd.Series): Match data row containing teams, scores,
            datetime, and metadata.

    Returns:
        dict: Event object ready for calendar rendering.

    Raises:
        KeyError: If required fields are missing in the row.
    """

    # =========================
    # STATUS CONFIGURATION
    # =========================
    STATUS_COLORS = {
            "played": "#057C0B",      # verde
            "live": "#FF0000",        # rojo
            "scheduled": "#00E5FF"    # azul
        }

    # 🔹 Determine match status
    status = match_status(row)
    color = STATUS_COLORS[status]

    home = row["homeTeamName"]
    away = row["awayTeamName"]
    dt = row["match_datetime"]

    home_logo = None if pd.isna(row["homeTeamPhoto"]) else row["homeTeamPhoto"]
    away_logo = None if pd.isna(row["awayTeamPhoto"]) else row["awayTeamPhoto"]


    h_score = safe_int(row["homeScore"])
    a_score = safe_int(row["awayScore"])
    # =========================
    # EVENT TITLE
    # =========================
    # 🔹 Scheduled match (no score yet)
    if status == "played" and h_score is not None and a_score is not None:
        title = f"⚽ {home} {int(h_score)}-{int(a_score)} {away}"
    else:
        title = f"⚽ {home} vs {away}"
        
    # =========================
    # EVENT STRUCTURE
    # =========================
    return {
        "title": title,
        "start": dt.isoformat(),

        # 🔹 Styling for calendar UI
        "backgroundColor": color,
        "borderColor": color,

        # 🔹 Extra metadata for tooltips / UI rendering
        "extendedProps": {
        "home": safe_str(home),
        "away": safe_str(away),
        "home_logo":home_logo,
        "away_logo":away_logo,
        "status": status,

        "score": (
            f"{int(row['homeScore'])}-{int(row['awayScore'])}"
            if status == "played"
            else None
        ),

        "time": dt.strftime("%H:%M"),
        "stage": safe_str(row["stageName"]),
        "round": safe_str(row["matchround"]),
        
    }
}

def calendar_function(df: list[dict] | pd.DataFrame) -> dict:
    """
    Render an interactive calendar with match events.

    This function displays a full calendar view using a calendar
    component, showing matches in monthly and weekly views.

    Args:
        df (list[dict] | pd.DataFrame):
            List or DataFrame of event objects compatible with the
            calendar component.

    Returns:
        dict:
            State object returned by the calendar component, including
            user interactions (e.g., event clicks).
    """

    # =========================
    # CALENDAR CONFIGURATION
    # =========================
    state = calendar(
        events=df,
        options={
            "initialView": "dayGridMonth",
            "height": 750,
            "firstDay": 1,
            "nowIndicator": True,
            # 🔹 Header navigation controls
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },

            # 🔹 Time formatting (24h format)
            "eventTimeFormat": {
                "hour": "2-digit",
                "minute": "2-digit",
                "hour12": False
            },

            # 🔹 Ensure event time is displayed
            "displayEventTime": True,
            "dayMaxEvents": True,
            "navLinks": True,
        },
        key="wc_calendar"
    )

    return state

@st.dialog("🏟️ Match Overview")
def show_match_dialog(event):

    props = event.get("extendedProps", {})

    home = props.get("home")
    away = props.get("away")

    home_logo = props.get("home_logo")
    away_logo = props.get("away_logo")

    status = props.get("status")

    col1, col2, col3 = st.columns([1.5, 2, 1.5])

    with col1:
        if home_logo:
            st.image(home_logo, width=120)

        st.markdown(f"<div style='text-align:center'><b>{home.upper()}</b></div>",unsafe_allow_html=True)

    with col2:

        if status == "played":
            st.success(f"Final Score: {props.get('score')}")
        else:
            st.info(f"Kick-off: {props.get('time')}")

        st.write(f"🔁 Stage: {props.get('round').split(' ')[-1]}")
        st.write(f"🏆 Group: {props.get('stage').split(' ')[-1]}")
        

    with col3:
        if away_logo:
            st.image(away_logo, width=120)

        st.markdown( f"<div style='text-align:center'><b>{away.upper()}</b></div>", unsafe_allow_html=True)


def click_event_and_info(state: dict) -> None:
    """
    Render detailed match information when a calendar event is clicked.

    This function extracts the selected event from the calendar state
    and displays a detailed match overview, including:
    - Teams and logos
    - Competition stage and round
    - Score (if played)
    - Kick-off time (if scheduled)

    Args:
        state (dict): Calendar state object containing user interactions,
            including event click data.

    Returns:
        None
    """

    # =========================
    # EVENT CLICK HANDLING
    # =========================
    if state and state.get("eventClick"):

        event = state["eventClick"]["event"]
        show_match_dialog(event)

st.divider()

def parse_table_standings( data: dict, group_idx: int = 0) -> pd.DataFrame:
    """
    Parse standings table data from FotMob API response.

    This function extracts and transforms league standings data,
    including team statistics, qualification rules, and metadata.

    Args:
        data (dict):
            Raw JSON response from FotMob standings API.
        group_idx (int, optional):
            Index of the group/table to parse. Defaults to 0.

    Returns:
        pd.DataFrame:
            Cleaned standings table with team statistics and metadata.

    Raises:
        KeyError:
            If expected structure is missing in API response.
        IndexError:
            If group_idx is out of range.
    """

    # =========================
    # RAW TABLE EXTRACTION
    # =========================
    df_tables = pd.DataFrame( data[0]["data"]["tables"])[["leagueId", "leagueName", "legend", "table"]]

    group = pd.DataFrame(df_tables.iloc[group_idx]).T

    # =========================
    # LEGEND MAPPING
    # =========================
    legend = group["legend"].iloc[0]

    color_map = { item["color"]: { "title": item["title"], "tKey": item["tKey"] } for item in legend}

    # =========================
    # TEAMS DATAFRAME
    # =========================
    teams = pd.DataFrame(group["table"].iloc[0]["all"])

    # 🔹 Normalize team names
    teams["name"] = teams["name"].replace(NAME_MAPPING2)

    # 🔹 Split goals
    teams[["goals_for", "goals_against"]] = teams["scoresStr"].str.split( "-",expand=True)

    # 🔹 Map qualification info
    teams["competition"] = teams["qualColor"].map(lambda x: color_map.get(x, {}).get("title"))

    teams["tKey"] = teams["qualColor"].map(lambda x: color_map.get(x, {}).get("tKey"))

    # 🔹 Build team logo URL
    teams["team_logo"] = "https://images.fotmob.com/image_resources/logo/teamlogo/"  + teams["id"].astype(str) + ".png"

    # 🔹 Final column selection
    teams = teams[['qualColor','idx','name','id','team_logo','played','wins','draws',
                'losses',"goals_for","goals_against",'goalConDiff','pts','competition']]
    return teams

def extract_standings_groups_fotmob(group_idx: int = 0) -> pd.DataFrame:
    """
    Fetch and parse standings data from FotMob API.

    This function retrieves live standings data and converts it
    into a structured DataFrame using `parse_table_standings`.

    Args:
        group_idx (int, optional):
            Index of the standings group to extract. Defaults to 0.

    Returns:
        pd.DataFrame:
            Parsed standings table.

    Raises:
        requests.HTTPError:
            If the API request fails.
    """

    # 🔹 API request
    response = requests.get("https://www.fotmob.com/api/data/tltable?leagueId=77&teams=%5B5796%5D" )
    response.raise_for_status()

    data = response.json()

    # 🔹 Parse response
    return parse_table_standings(data, group_idx=group_idx)

def create_plot_standings(group_df: pd.DataFrame) -> None:
    """
    Render a standings table using a custom Streamlit layout.

    This function builds a visually structured league table with:
    - Team rankings
    - Match statistics
    - Goals and points
    - Qualification status

    Args:
        group_df (pd.DataFrame): Standings dataset.

    Returns:
        None
    """

    # =========================
    # HEADER COLUMNS
    # =========================
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([1, 4, 2, 2, 2, 2, 2, 2, 2, 2])

    with c1:
        st.write("")

    with c2:
        st.markdown(
            """
            <span style="font-size:14px; font-weight:bold;">
                Team
            </span><br>
            <small style="font-size:12px;">
                (Qualification Status)
            </small>
            """,
            unsafe_allow_html=True
        )

    headers = [
        ("Played Games", c3),
        ("Wins", c4),
        ("Draws", c5),
        ("Losses", c6),
        ("Goals Scored", c7),
        ("Goals Against", c8),
        ("Goal Diff", c9),
        ("Points", c10),
    ]

    for label, col in headers:
        with col:
            st.markdown(
                f"<p style='font-size:14px;'>{label}</p>",
                unsafe_allow_html=True
            )

    st.markdown(
        "<hr style='margin:4px 0 6px 0;'>",
        unsafe_allow_html=True
    )

    # =========================
    # TABLE ROWS
    # =========================
    for _, row in group_df.iterrows():

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([1, 5, 2, 2, 2, 2, 2, 2, 2, 2])

        with c1:
            st.image(row["team_logo"], width=40)

        with c2:
            st.markdown(
                f"<div style='font-size:13px; font-weight:bold;'>{row['idx']}. {row['name']}</div>",
                unsafe_allow_html=True
            )

            if pd.notna(row["competition"]):
                st.markdown(
                    f"<div style='font-size:10px; color: var(--text-color-secondary);opacity:0.6;'>{row['competition']}</div>",
                    unsafe_allow_html=True
                )


        # =========================
        # STATS COLUMNS
        # =========================
        with c3:
            st.write(str(row["played"]))

        with c4:
            st.write(str(row["wins"]))

        with c5:
            st.write(str(row["draws"]))

        with c6:
            st.write(str(row["losses"]))

        with c7:
            st.write(str(row["goals_for"]))

        with c8:
            st.write(str(row["goals_against"]))

        with c9:
            st.write(str(row["goalConDiff"]))

        with c10:
            st.write(str(row["pts"]))

def table_groups() -> None:
    """
    Render all tournament group standings in a segmented control.

    This function:
    - Fetches standings for all groups in parallel using ThreadPoolExecutor
    - Organizes groups into a structured UI (A–L)
    - Displays each group using a standings table renderer
    - Shows best third-place teams separately

    Returns:
        None

    Raises:
        RuntimeError: If data fetching or rendering fails.
    """

    try:


        # PARALLEL DATA FETCHING
        # =========================
        with ThreadPoolExecutor(max_workers=13) as executor:
            groups = list(executor.map( extract_standings_groups_fotmob, range(13)) )

        option = st.segmented_control('\n\n', 
                           ['GROUP A', 'GROUP B', 'GROUP C' , 'GROUP D', 'GROUP E', 'GROUP F', 'GROUP G', 'GROUP H', 'GROUP I',
                            'GROUP J', 'GROUP K', 'GROUP L', 'BEST 3RD PLACE TEAMS'],default='GROUP A')
    
        if option == 'GROUP A':
            with st.container(border=True):
                create_plot_standings(groups[0])

        elif option == 'GROUP B':
            with st.container(border=True):
                create_plot_standings(groups[1])

        elif option == 'GROUP C':
            with st.container(border=True):
                create_plot_standings(groups[2])
            
        elif option == 'GROUP D':
            with st.container(border=True):
                create_plot_standings(groups[3])

        elif option == 'GROUP E':
            with st.container(border=True):
                create_plot_standings(groups[4])

        elif option == 'GROUP F':
            with st.container(border=True): 
                create_plot_standings(groups[5])

        elif option == 'GROUP G':
            with st.container(border=True):
                create_plot_standings(groups[6])

        elif option == 'GROUP H':
            with st.container(border=True):
                create_plot_standings(groups[7])

        elif option == 'GROUP I':
            with st.container(border=True):
                create_plot_standings(groups[8])

        elif option == 'GROUP J':
            with st.container(border=True):
                create_plot_standings(groups[9])

        elif option == 'GROUP K':
            with st.container(border=True):
                create_plot_standings(groups[10])
        elif option == 'GROUP L':
            with st.container(border=True):
                create_plot_standings(groups[11])

        else:
            with st.container(border=True):
                create_plot_standings(groups[12])

    except Exception as e:
        raise RuntimeError(f"Failed to render table groups: {e}")
    
def prepare_playoffs_wc26(): 

    response = requests.get("https://www.fotmob.com/api/data/leagues?id=77&ccode3=NLD")
    response.raise_for_status()
    data = response.json()

    #Data rounds, except match for the 3rd place
    df_rounds= pd.DataFrame(data['playoff']['rounds'])
    # 1. Explotar la lista de matchups (mantiene el stage como repetido)
    df_exploded = df_rounds.explode('matchups', ignore_index=True)

    # 2. Normalizar el diccionario interno
    matchups_normalized = pd.json_normalize(df_exploded['matchups']).add_prefix('matchup_')

    df_final = df_exploded.drop(columns=['matchups']).join(matchups_normalized)
    df1 = df_final.explode('matchup_matches', ignore_index=True)
    matches = pd.json_normalize(df1['matchup_matches'], sep='_')

    df_clean = df1.drop(columns=['matchup_matches']).reset_index(drop=True)
    df_clean = df_clean.join(matches.reset_index(drop=True))
    df_playoff= df_clean[['stage' ,'status_utcTime',	'status_started',	'status_cancelled',	'status_finished', 'matchup_homeTeamShortName',
                            'matchup_awayTeamShortName', 'matchup_aggregatedWinner',	'matchup_aggregatedLoser'	,'matchup_aggregatedResult.homeScore',
                            'matchup_aggregatedResult.awayScore' ,'matchId',	'pageUrl',	'home_id',	'home_name'	,'home_shortName'	,'home_score',	'home_winner'	,
                            'away_id',	'away_name',	'away_shortName',	'away_score',	'away_winner']].copy()

    df_playoff['pageUrl']= "https://www.fotmob.com" + df_playoff['pageUrl']

    #Data only match to 3rd place
    df_3rd = pd.json_normalize(data['playoff']['bronzeFinal'])
    df_3rd_exp = df_3rd.explode('matches', ignore_index=True)
    df_matches = pd.json_normalize(df_3rd_exp['matches'])
    df_final_3rd = df_3rd_exp.drop(columns=['matches']).join(df_matches)
    df_3rd_final = df_final_3rd.rename(columns={ 'status.utcTime': 'status_utcTime', 'status.started': 'status_started', 'status.cancelled': 'status_cancelled', 'status.finished': 'status_finished',
                                                    'home.id': 'home_id','home.name': 'home_name','home.shortName': 'home_shortName','home.score': 'home_score','home.winner': 'home_winner',
                                                    'away.id': 'away_id','away.name': 'away_name','away.shortName': 'away_shortName','away.score': 'away_score','away.winner': 'away_winner',
                                                    'aggregatedWinner': 'matchup_aggregatedWinner','aggregatedLoser': 'matchup_aggregatedLoser','aggregatedResult_homeScore': 'matchup_aggregatedResult.homeScore',
                                                    'aggregatedResult_awayScore': 'matchup_aggregatedResult.awayScore', 'homeTeamShortName': 'matchup_homeTeamShortName','awayTeamShortName': 'matchup_awayTeamShortName',
                                                    'aggregatedWinner': "matchup_aggregatedWinner", 'aggregatedLoser':'matchup_aggregatedLoser','aggregatedResult.homeScore': 'matchup_aggregatedResult.homeScore', 
                                                    'aggregatedResult.awayScore': "matchup_aggregatedResult.awayScore",
                                                    })

    df_3rd_final= df_3rd_final[['stage' ,'status_utcTime',	'status_started',	'status_cancelled',	'status_finished', 'matchup_homeTeamShortName',
                            'matchup_awayTeamShortName', 'matchup_aggregatedWinner',	'matchup_aggregatedLoser'	,'matchup_aggregatedResult.homeScore',
                            'matchup_aggregatedResult.awayScore' ,'matchId',	'pageUrl',	'home_id',	'home_name'	,'home_shortName'	,'home_score',	'home_winner'	,
                            'away_id',	'away_name',	'away_shortName',	'away_score',	'away_winner']].copy()

    df_3rd_final['pageUrl']= "https://www.fotmob.com" + df_3rd_final['pageUrl']

    # =====================================================
    # FECHAS
    # =====================================================

    df = df_playoff.copy()

    df["date"] = pd.to_datetime(df["status_utcTime"]) + pd.Timedelta(hours=4)

    df["date_label"] = df["date"].dt.strftime("%d %b %H:%M")

    df_bronze= df_3rd_final.copy()
    df_bronze["date"] = pd.to_datetime(df_bronze["status_utcTime"]) + pd.Timedelta(hours=4)
    df_bronze["date_label"] = df_bronze["date"].dt.strftime("%d %b %H:%M")

    df_final_concat = pd.concat([df, df_bronze], ignore_index=True)
    df_final_concat['url_photo_home'] = "https://images.fotmob.com/image_resources/logo/teamlogo/"+ df_final_concat['home_id'].astype(str)+ ".png"

    df_final_concat['url_photo_away'] = "https://images.fotmob.com/image_resources/logo/teamlogo/"+ df_final_concat['away_id'].astype(str)+ ".png"
    return df_final_concat

# def create_plot_playoffs(df):

#     # =====================================================
#     # LAYOUT FOTMOB
#     # =====================================================
#     layout = {
#         "GER": (-6,14), "NOR": (-6,12),
#         "RSA": (-6,10), "NED": (-6,8),
#         "COD": (-6,6), "ESP": (-6,4),
#         "USA": (-6,2), "NZL": (-6,0),

#         "G3A": (-3,13), "2AB": (-3,9),
#         "2KL": (-3,5), "US3": (-3,1),

#         "EF1": (0,11), "EF5": (0,3),
#         "WQ1": (4,7),

#         "1CF": (18,13), "M3C": (18,9),
#         "1JH": (18,5), "1BE": (18,1),

#         "BRA": (21,14), "CIV": (21,12),
#         "MEX": (21,10), "ENG": (21,8),
#         "ARG": (21,6), "AUS": (21,4),
#         "CAN": (21,2), "COL": (21,0),

#         "EF3": (15,11), "EF7": (15,3),
#         "WQ3": (11,7),

#         "WS1": (7.5,7),
#         "LS1": (7.5,4.5)
#     }

#     # =====================================================
#     # CONEXIONES
#     # =====================================================
#     connections = [
#         ("GER","G3A"), ("NOR","G3A"),
#         ("RSA","2AB"), ("NED","2AB"),
#         ("COD","2KL"), ("ESP","2KL"),
#         ("USA","US3"), ("NZL","US3"),
#         ("G3A","EF1"), ("2AB","EF1"),
#         ("2KL","EF5"), ("US3","EF5"),
#         ("EF1","WQ1"), ("EF5","WQ1"),

#         ("BRA","1CF"), ("CIV","1CF"),
#         ("MEX","M3C"), ("ENG","M3C"),
#         ("ARG","1JH"), ("AUS","1JH"),
#         ("CAN","1BE"), ("COL","1BE"),
#         ("1CF","EF3"), ("M3C","EF3"),
#         ("1JH","EF7"), ("1BE","EF7"),
#         ("EF3","WQ3"), ("EF7","WQ3"),

#         ("WQ1","WS1"), ("WQ3","WS1")
#     ]
#     # =====================================================
#     # FIGURA MATPLOTLIB
#     # =====================================================
#     fig, ax = plt.subplots(figsize=(25, 15))

#     # ax.set_xlim(-8, 24)
#     # ax.set_ylim(-8, 16)
#     ax.axis("off")

#     fig.patch.set_facecolor('none')
#     ax.set_facecolor('none')

#     # =====================================================
# # 🔥 AUTO ZOOM PERFECTO (CLAVE)
# # =====================================================
#     xs = [x for x, y in layout.values()]
#     ys = [y for x, y in layout.values()]

#     box_w = 2.4
#     box_h = 1.2

#     pad = 3

#     ax.set_xlim(min(xs) - pad, max(xs) + pad + box_w)
#     ax.set_ylim(min(ys) - pad, max(ys) + pad)

#     # =====================================================
#     # CAJAS
#     # =====================================================
#     for _, row in df.iterrows():

#         key = row["home_shortName"]
#         if key not in layout:
#             continue

#         x, y = layout[key]

#         # rect (Plotly shape equivalent)
#         ax.add_patch(Rectangle(
#             (x, y - 0.6),
#             box_w,
#             box_h,
#             facecolor="none",
#             edgecolor="white",
#             linewidth=1
#         ))

#         # annotation (Plotly text equivalent)
#         ax.text(
#             x + box_w / 2,
#             y,
#             f"{row['home_shortName']} vs {row['away_shortName']}\n\n{row['date_label']}",
#             ha="center",
#             va="center",
#             fontsize=12,
#             color="white"
#         )

#     # =====================================================
#     # BRACKETS
#     # =====================================================
#     for parent, child in connections:

#         if parent not in layout or child not in layout:
#             continue

#         x0, y0 = layout[parent]
#         x1, y1 = layout[child]

#         if x1 > x0:
#             start_x = x0 + box_w
#             end_x = x1
#         else:
#             start_x = x0
#             end_x = x1 + box_w

#         mid_x = start_x + (end_x - start_x) * 0.35

#         ax.plot([start_x, mid_x], [y0, y0], color="white", linewidth=1.3)
#         ax.plot([mid_x, mid_x], [y0, y1], color="white", linewidth=1.3)
#         ax.plot([mid_x, end_x], [y1, y1], color="white", linewidth=1.3)

#     plt.tight_layout()

#     return fig

def create_plot_playoffs(df):

    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    from PIL import Image
    import requests
    from io import BytesIO

    # =====================================================
    # COPIA
    # =====================================================

    df = df.copy()

    # =====================================================
    # RENOMBRAR TBD
    # =====================================================

    tbd_map = {
        4653843: "TBD_L1",  # RSA/NED
        4653846: "TBD_R1",  # BRA/CIV
        4653849: "TBD_R2",  # SUI/COL
        4653845: "TBD_L2"
    }

    for match_id, code in tbd_map.items():

        mask = df["matchId"] == match_id

        if mask.any():
            df.loc[mask, "home_shortName"] = code

    # =====================================================
    # CACHE IMÁGENES
    # =====================================================

    img_cache = {}

    def load_image(url):

        if not isinstance(url, str):
            return None

        if url in img_cache:
            return img_cache[url]

        try:

            r = requests.get(url, timeout=5)

            img = Image.open(
                BytesIO(r.content)
            ).convert("RGBA")

            img = img.resize(
                (60, 60),
                Image.Resampling.LANCZOS
            )

            img_cache[url] = img

            return img

        except:
            return None

    def add_img(ax, url, x, y, zoom=0.35):

        img = load_image(url)

        if img is None:
            return

        imagebox = OffsetImage(
            img,
            zoom=zoom
        )

        ab = AnnotationBbox(
            imagebox,
            (x, y),
            frameon=False
        )

        ax.add_artist(ab)

    # =====================================================
    # LAYOUT
    # =====================================================

    layout = {

        # ---------------------------
        # DIECISEISAVOS IZQUIERDA
        # ---------------------------

        "GER": (-6, 14),
        "FRA": (-6, 12),

        "RSA": (-6, 10),
        "NED": (-6, 8),

        "POR": (-6, 6),
        "ESP": (-6, 4),

        "USA": (-6, 2),
        "EGY": (-6, 0),

        # ---------------------------
        # OCTAVOS IZQUIERDA
        # ---------------------------

        "G3A": (-2, 13),
        "TBD_L1": (-2, 9),

        "2KL": (-2, 5),
        "TBD_L2": (-2, 1),

        # ---------------------------
        # CUARTOS IZQUIERDA
        # ---------------------------

        "EF1": (2, 11),
        "EF5": (2, 3),

        # ---------------------------
        # SEMI IZQUIERDA
        # ---------------------------

        "WQ1": (6, 7),

        # ---------------------------
        # FINAL
        # ---------------------------

        "WS1": (10, 7),

        # ---------------------------
        # BRONCE
        # ---------------------------

        "LS1": (10, 4),

        # =====================================================
        # DERECHA
        # =====================================================

        "BRA": (26, 14),
        "CIV": (26, 12),

        "MEX": (26, 10),
        "ENG": (26, 8),

        "ARG": (26, 6),
        "AUS": (26, 4),

        "SUI": (26, 2),
        "COL": (26, 0),

        # OCTAVOS

        "TBD_R1": (22, 13),
        "M3C": (22, 9),

        "AR2": (22, 5),
        "TBD_R2": (22, 1),

        # CUARTOS

        "EF3": (18, 11),
        "EF7": (18, 3),

        # SEMI

        "WQ3": (14, 7),

        # FINAL DERECHO

        "WS2": (10, 7),
    }

    # =====================================================
    # CONEXIONES
    # =====================================================

    connections = [

        # --------------------
        # IZQUIERDA
        # --------------------

        ("GER", "G3A"),
        ("FRA", "G3A"),

        ("RSA", "TBD_L1"),
        ("NED", "TBD_L1"),

        ("POR", "2KL"),
        ("ESP", "2KL"),

        ("USA", "TBD_L2"),
        ("EGY", "TBD_L2"),

        ("G3A", "EF1"),
        ("TBD_L1", "EF1"),

        ("2KL", "EF5"),
        ("TBD_L2", "EF5"),

        ("EF1", "WQ1"),
        ("EF5", "WQ1"),

        # --------------------
        # DERECHA
        # --------------------

        ("BRA", "TBD_R1"),
        ("CIV", "TBD_R1"),

        ("MEX", "M3C"),
        ("ENG", "M3C"),

        ("ARG", "AR2"),
        ("AUS", "AR2"),

        ("SUI", "TBD_R2"),
        ("COL", "TBD_R2"),

        ("TBD_R1", "EF3"),
        ("M3C", "EF3"),

        ("AR2", "EF7"),
        ("TBD_R2", "EF7"),

        ("EF3", "WQ3"),
        ("EF7", "WQ3"),

        # --------------------
        # FINAL
        # --------------------

        ("WQ1", "WS1"),
        ("WQ3", "WS2"),
    ]

    # =====================================================
    # FIGURA
    # =====================================================

    fig, ax = plt.subplots(
        figsize=(26, 15)
    )

    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")

    ax.axis("off")

    box_w = 2.6
    box_h = 1.2

    ax.set_xlim(-10, 32)
    ax.set_ylim(-2, 16)

    # =====================================================
    # DIBUJAR CAJAS
    # =====================================================

    for _, row in df.iterrows():

        key = row["home_shortName"]

        if key not in layout:
            continue

        x, y = layout[key]

        ax.add_patch(
            Rectangle(
                (x, y - 0.6),
                box_w,
                box_h,
                facecolor="none",
                edgecolor="white",
                linewidth=0.8
            )
        )

        add_img(
            ax,
            row.get("url_photo_home"),
            x + 0.65,
            y + 0.15
        )

        add_img(
            ax,
            row.get("url_photo_away"),
            x + box_w - 0.65,
            y + 0.15
        )

        ax.text(
            x + box_w / 2,
            y - 0.25,
            f"{row['home_shortName']} vs {row['away_shortName']}",
            ha="center",
            va="center",
            fontsize=11,
            color="white",
            fontweight="bold"
        )

        ax.text(
            x + box_w / 2,
            y - 0.75,
            str(row["date_label"]),
            ha="center",
            va="center",
            fontsize=9,
            color="#cfcfcf"
        )

    # =====================================================
    # CONEXIONES
    # =====================================================

    for parent, child in connections:

        if parent not in layout:
            continue

        if child not in layout:
            continue

        x0, y0 = layout[parent]
        x1, y1 = layout[child]

        if x1 > x0:

            start_x = x0 + box_w
            end_x = x1

        else:

            start_x = x0
            end_x = x1 + box_w

        mid_x = start_x + (end_x - start_x) * 0.45

        ax.plot(
            [start_x, mid_x],
            [y0, y0],
            color="white",
            linewidth=1.3
        )

        ax.plot(
            [mid_x, mid_x],
            [y0, y1],
            color="white",
            linewidth=1.3
        )

        ax.plot(
            [mid_x, end_x],
            [y1, y1],
            color="white",
            linewidth=1.3
        )

    plt.tight_layout()

    return fig