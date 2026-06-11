import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
from concurrent.futures import ThreadPoolExecutor
import requests
from utils.mapping import NAME_MAPPING2


def match_status(row: pd.Series) -> str:
    """
    Determine the status of a match based on score availability.

    A match is considered:
    - "played" if both home and away scores are present
    - "scheduled" otherwise

    Args:
        row (pd.Series): Match row containing score information.

    Returns:
        str: Match status ("played" or "scheduled").

    Raises:
        KeyError: If required columns are missing.
    """

    # 🔹 Match already played if both scores exist
    return ("played" if pd.notna(row["homeScore"]) and pd.notna(row["awayScore"]) else "scheduled" )

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
    STATUS_COLORS = { "played": "#057C0B", "scheduled": "#00E5FF"}

    # 🔹 Determine match status
    status = match_status(row)
    color = STATUS_COLORS[status]

    home = row["homeTeamName"]
    away = row["awayTeamName"]
    dt = row["match_datetime"]

    # =========================
    # EVENT TITLE
    # =========================
    # 🔹 Scheduled match (no score yet)
    if status == "scheduled":
        title = f"⚽ {home} vs {away}"

    # 🔹 Completed match (show score)
    else:
        title =  f"⚽ {home} {int(row['homeScore'])}-{int(row['awayScore'])} {away}"
        

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
            "home": home,
            "away": away,
            "home_logo": row["homeTeamPhoto"],
            "away_logo": row["awayTeamPhoto"],
            "status": status,

            # 🔹 Score only for played matches
            "score": (
                f"{int(row['homeScore'])}-{int(row['awayScore'])}"
                if status == "played"
                else None
            ),

            "time": dt.strftime("%H:%M"),
            "stage": row["stageName"],
            "round": row["matchround"]
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
            "displayEventTime": True
        },
        key="wc_calendar"
    )

    return state

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
    if state.get("eventClick"):

        st.subheader("🏟️ MATCH OVERVIEW")

        with st.container(border=True):

            event = state["eventClick"]["event"]
            props = event.get("extendedProps", {})

            # 🔹 Match title
            st.caption(event["title"])
            st.write(" ")

            # =========================
            # LAYOUT COLUMNS
            # =========================
            col1, col2, col3 = st.columns([1, 4, 1])

            # =========================
            # HOME TEAM
            # =========================
            with col1:
                st.image(props.get("home_logo"), width=90)
                st.write(props.get("home"))

            # =========================
            # MATCH INFO
            # =========================
            with col2:

                st.write(f"🏆 Stage: {props.get('stage')}")
                st.write(f"🔁 Round: {props.get('round')}")

                # 🔹 Conditional rendering based on match status
                if props.get("status") == "played":
                    st.success(f"Final score: {props.get('score')}")
                else:
                    st.info(f"Kick-off: {props.get('time')}")

            # =========================
            # AWAY TEAM
            # =========================
            with col3:
                st.image(props.get("away_logo"), width=90)
                st.write(props.get("away"))

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
    Render all tournament group standings in a two-column layout.

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

        # =========================
        # PAGE TITLE
        # =========================
        st.subheader("🥇 TABLE GROUPS")

        # =========================
        # PARALLEL DATA FETCHING
        # =========================
        with ThreadPoolExecutor(max_workers=13) as executor:
            groups = list(executor.map( extract_standings_groups_fotmob, range(13)) )

        # =========================
        # LAYOUT COLUMNS
        # =========================
        block1, block2 = st.columns(2)

        # =========================
        # LEFT COLUMN (A, C, E, G, I, K)
        # =========================
        with block1:

            group_indices_left = [
                (0, "GROUP A"),
                (2, "GROUP C"),
                (4, "GROUP E"),
                (6, "GROUP G"),
                (8, "GROUP I"),
                (10, "GROUP K"),
            ]

            for idx, label in group_indices_left:

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style='text-align: center;'>
                            <h4>{label}</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    create_plot_standings(groups[idx])

        # =========================
        # RIGHT COLUMN (B, D, F, H, J, L)
        # =========================
        with block2:

            group_indices_right = [
                (1, "GROUP B"),
                (3, "GROUP D"),
                (5, "GROUP F"),
                (7, "GROUP H"),
                (9, "GROUP J"),
                (11, "GROUP L"),
            ]

            for idx, label in group_indices_right:

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style='text-align: center;'>
                            <h4>{label}</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    create_plot_standings(groups[idx])

        # =========================
        # DIVIDER
        # =========================
        st.divider()

        # =========================
        # BEST 3RD PLACE TEAMS
        # =========================
        st.markdown(
            "<div style='text-align: center;'><h4>BEST 3RD PLACE TEAMS</h4></div>",
            unsafe_allow_html=True
        )

        col2, col3, col4 = st.columns([1, 5, 1])

        with col3:
            with st.container(border=True):
                create_plot_standings(groups[12])

    except Exception as e:
        raise RuntimeError(f"Failed to render table groups: {e}")

