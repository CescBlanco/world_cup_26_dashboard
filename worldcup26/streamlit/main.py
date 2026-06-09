import streamlit as st
import pandas as pd
from datetime import time

import os
import glob
import datetime

from services.load_data import load_teams, load_fifa, load_elo, load_all_players_fotmob, load_venues, load_fixtures
from assets.styles import apply_styles, calendar_styles
from services.transform_data import build_teams_dataset

from pages.teams import render_teams


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="World Cup 2026", page_icon="⚽", layout="wide")

# =========================================================
# STYLE
# =========================================================
apply_styles()

# =========================================================
# DATA
# =========================================================
df_teams = load_teams()
df_fifa = load_fifa()
df_elo = load_elo()

df_teams_dataset = build_teams_dataset(df_teams, df_fifa, df_elo)

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "teams"

if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([1, 8])

with col1:
    st.image(
        "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/77.png",
        width=150
    )

with col2:
    st.title("WORLD CUP 2026")
    st.caption("Football Analytics Platform")

st.divider()

st.markdown("""
    <style>
    div[data-testid="stButton"] > button {
        background-color: #1f1f1f !important;
        color: #eaeaea !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.2s ease;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #2a2a2a !important;
        border-color: #555 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.image("worldcup26/streamlit/assets/images/pngwing.com.png", width=200)

    st.title("⚽ World Cup 2026")

    if st.button("🏆 Teams"):
        st.session_state.page = "teams"

    if st.button("👕 Team Roster"):
        st.session_state.page = "rosters"

    if st.button("🏟️ Venues"):
        st.session_state.page = "venues"

    if st.button("📅 Fixtures"):
        st.session_state.page = "fixtures"

    if st.button("📊 Results"):
        st.session_state.page = "results"
    
    st.info(f"**Current page:** {st.session_state.page.title()}")
    st.divider()
    
    
    st.markdown("### Data Status")

    files = glob.glob("worldcup26/data/*.csv")

    if files:

        last_ts = max(os.path.getmtime(f) for f in files)
        last_dt = datetime.datetime.fromtimestamp(last_ts)

        days_old = (datetime.datetime.now() - last_dt).days
        last_updated = last_dt.strftime("%Y-%m-%d %H:%M")

        st.caption(f"Updated: {last_updated}")

        if days_old > 4:
            st.warning("⚠️ Data is older than 4 days.")
        else:
            st.success("✅ Data up to date")

    else:
        st.error("❌ No data files found")

# =========================================================
# PAGE: TEAMS
# =========================================================
if st.session_state.page == "teams":

    render_teams(df_teams_dataset)
