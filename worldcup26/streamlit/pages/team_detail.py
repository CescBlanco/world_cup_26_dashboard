import streamlit as st
import plotly.express as px

from functions.team_details import *
from services.load_data import load_all_players_fotmob

def render_team_detail(df):

    team = st.session_state.selected_team

    team_data = df[df["team"] == team]

    bloc1, bloc2 = st.columns([1.5,4])

    with bloc1:
        team_details_bloc1(team_data)      
    with bloc2:
        team_details_bloc2(team_data)

    #----------------------------------------------------------------------------------
    
    st.subheader("👕 Team Roster")
    st.info('Working to integrated rating data for players...')
    df_all_players = load_all_players_fotmob()
    players_team = df_all_players[df_all_players["team_name"] == team]
     
    # =========================
    # TEAM HEADER
    # =========================

    team_header(players_team)

    # =========================
    # TEAM SUMMARY
    # =========================

    players_only=team_sumary(players_team)


    # =========================
    # STAR PLAYERS
    # =========================

    star_players_mk_value(players_only)

    # =========================
    # SQUAD BY POSITION
    # =========================
    squad_by_postion(players_only)

    if st.button("⬅ Back to Teams"):
        st.session_state.page = "teams"
        st.rerun()