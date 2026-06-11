import streamlit as st
import plotly.express as px

from functions.team_details import *
from services.load_data import load_all_players_fotmob

def render_team_detail(df: pd.DataFrame) -> None:
    """
    Render the complete team detail page.

    This function orchestrates the full team detail view, including:
    - Team performance analytics (bloc1 and bloc2)
    - Full squad roster
    - Team header information
    - Squad summary metrics
    - Top market value players
    - Players grouped by position
    - Navigation back to teams view

    Args:
        df (pd.DataFrame): Dataset containing team-level performance data.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required session state or columns are missing.
        RuntimeError: If any rendering step fails.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    try:
        # =========================
        # SELECTED TEAM
        # =========================
        team = st.session_state.selected_team

        # 🔹 Filter dataset for selected team
        team_data = df[df["team"] == team]

        # =========================
        # TEAM PERFORMANCE BLOCKS
        # =========================
        bloc1, bloc2 = st.columns([1.5, 4])

        with bloc1:
            team_details_bloc1(team_data)

        with bloc2:
            team_details_bloc2(team_data)

        st.divider()

        # =========================
        # TEAM SQUAD SECTION
        # =========================
        st.subheader("👕 Team Roster")

        # 🔹 Load full players dataset
        df_all_players = load_all_players_fotmob()

        # 🔹 Filter players for selected team
        players_team = df_all_players[ df_all_players["team_name"] == team]

        # =========================
        # TEAM HEADER
        # =========================
        team_header(players_team)

        # =========================
        # TEAM SUMMARY
        # =========================
        players_only = team_sumary(players_team)

        # =========================
        # FEATURED PLAYERS
        # =========================
        star_players_market_value(players_only)

        # =========================
        # SQUAD BREAKDOWN
        # =========================
        squad_by_position(players_only)

        # =========================
        # NAVIGATION
        # =========================
        if st.button("⬅ Back to Teams"):
            st.session_state.page = "teams"
            st.rerun()

    except Exception as e:
        raise RuntimeError(f"Failed to render team detail page: {e}")