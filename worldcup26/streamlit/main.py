import streamlit as st
import os
import glob
import datetime

from services.load_data import load_teams, load_fifa, load_elo, load_all_players_fotmob, load_venues, load_fixtures, load_fixtures_pruebas
from assets.styles import apply_styles, calendar_styles
from services.transform_data import build_teams_dataset

from pages_backup.teams import render_teams
from pages_backup.team_detail import render_team_detail
from pages_backup.team_roster import render_team_roster
from pages_backup.venues import render_venues
from pages_backup.fixtures import render_fixtures
from pages_backup.results import render_results

# =============================================================================
# WORLD CUP 2026 ANALYTICS PLATFORM
# =============================================================================
#
# Interactive football analytics application built with Streamlit.
#
# Main modules:
#
# - Teams
# - Team Profiles
# - Rosters
# - Venues
# - Fixtures
# - Results & Match Analysis
#
# The platform combines multiple data providers to deliver
# tournament information, match insights and advanced tactical
# visualizations.
#
# =============================================================================


# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
#
# Configure Streamlit page settings:
#
# - Browser title
# - Application icon
# - Layout mode
#
# =============================================================================
st.set_page_config(page_title="World Cup 2026", page_icon="⚽", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0e1117 !important;
    color: #fafafa !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# GLOBAL STYLING
# =============================================================================
#
# Load and apply the custom visual theme used across the application.
#
# Includes:
#
# - Colors
# - Typography
# - Containers
# - Buttons
# - Layout adjustments
#
# =============================================================================
apply_styles()

# =============================================================================
# DATA LOADING
# =============================================================================
#
# Load all datasets required by the platform.
#
# Sources:
#
# - Team information
# - FIFA rankings
# - Elo ratings
#
# These datasets are merged into a single enriched dataframe used
# throughout the application.
#
# =============================================================================
df_teams = load_teams()
df_fifa = load_fifa()
df_elo = load_elo()

df_teams_dataset = build_teams_dataset(df_teams, df_fifa, df_elo)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
#
# Initialize navigation state and selected entities.
#
# Stored values:
#
# - Current page
# - Selected team
#
# Session state allows navigation between views without losing context.
#
# =============================================================================
if "page" not in st.session_state:
    st.session_state.page = "match results"

if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

# =============================================================================
# APPLICATION HEADER
# =============================================================================
#
# Render the main application header:
#
# - FIFA World Cup logo
# - Platform title
# - Application subtitle
#
# =============================================================================

col1, col2 = st.columns([1, 8])

with col1:
    st.image("https://images.fotmob.com/image_resources/logo/leaguelogo/dark/77.png",width=150)

with col2:
    st.title("WORLD CUP 2026")
    st.caption("Football Analytics Platform")

st.divider()

# =============================================================================
# GLOBAL BUTTON STYLING
# =============================================================================
#
# Inject custom CSS for all Streamlit buttons.
#
# Goals:
#
# - Consistent dark theme
# - Hover effects
# - Rounded corners
# - Improved visual hierarchy
#
# =============================================================================

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

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
#
# Main application navigation panel.
#
# Available sections:
#
# - Teams
# - Team Rosters
# - Venues
# - Match schedule
# - Results
#
# Navigation is managed through Streamlit session state.
#
# =============================================================================

with st.sidebar:

    st.image("worldcup26/streamlit/assets/images/pngwing.com.png", width=200)

    st.title("⚽ World Cup 2026")

    if st.button("🏆 Teams"):
        st.session_state.page = "teams"

    if st.button("👕 Team Roster"):
        st.session_state.page = "rosters"

    if st.button("🏟️ Venues"):
        st.session_state.page = "venues"

    if st.button("📅 Match schedule"):
        st.session_state.page = "match schedule"

    if st.button("📊 Results"):
        st.session_state.page = "match results"
    
    st.info(f"**Current page:** {st.session_state.page.title()}")
    st.divider()
    
# =============================================================================
# DATA STATUS MONITOR
# =============================================================================
#
# Check the freshness of local datasets by inspecting the latest
# modification timestamp.
#
# Status indicators:
#
# - Up to date
# - Outdated (> 4 days)
# - Missing files
#
# =============================================================================
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



# =============================================================================
# PAGE ROUTER
# =============================================================================
#
# Main application router.
#
# Dynamically renders the selected page according to the current
# navigation state.
#
# Available views:
#
# - Teams
# - Team Detail
# - Team Rosters
# - Venues
# - Fixtures
# - Results
#
# =============================================================================


# =============================================================================
# TEAMS PAGE
# =============================================================================
#
# Display all qualified teams participating in the tournament.
#
# Includes:
#
# - Team cards
# - Rankings
# - Qualification information
# - Navigation to detailed team profiles
#
# =============================================================================

if st.session_state.page == "teams":

    render_teams(df_teams_dataset)

# =============================================================================
# TEAM DETAIL PAGE
# =============================================================================
#
# Display an in-depth profile of the selected national team.
#
# Includes:
#
# - Team overview
# - Squad information
# - Historical performance
# - Tournament metrics
#
# =============================================================================
elif st.session_state.page == "team_detail":
    
    team = st.session_state.selected_team

    team_data = df_teams_dataset[df_teams_dataset["Squad"] == team]
    render_team_detail(team_data)

# =============================================================================
# TEAM ROSTERS PAGE
# =============================================================================
#
# Display the player roster of a selected national team.
#
# Workflow:
#
# 1. User selects a team.
# 2. Player data is filtered.
# 3. Squad information is rendered.
#
# =============================================================================
elif st.session_state.page == "rosters":

    selected = st.selectbox( "Select Team",sorted(df_teams_dataset["Squad"].dropna().unique()))

    df_all_players = load_all_players_fotmob()
    players_team = df_all_players[df_all_players["team_name"] == selected]

    render_team_roster(players_team)

# =============================================================================
# VENUES PAGE
# =============================================================================
#
# Display all World Cup stadiums and host venues.
#
# Includes:
#
# - Stadium information
# - Capacity
# - Location
# - Venue visualizations
#
# =============================================================================
elif st.session_state.page == "venues":

    st.subheader("🏟️ World Cup Stadiums")
    df_venues= load_venues()
    
    render_venues(df_venues)

# =============================================================================
# FIXTURES PAGE
# =============================================================================
#
# Interactive tournament calendar.
#
# Includes:
#
# - Match schedule
# - Group stage fixtures
# - Knockout rounds
# - Standings integration
#
# =============================================================================
elif st.session_state.page == "match schedule":

    st.subheader("📅 World Cup Calendar")   

    
    df_matches_stages = load_fixtures()

    calendar_styles()
    render_fixtures(df_matches_stages)


# =============================================================================
# RESULTS PAGE
# =============================================================================
#
# Match results and advanced post-match analysis.
#
# Features:
#
# - Match filtering
# - Detailed event timeline
# - Tactical dashboards
# - Team analytics
# - Report generation
#
# Note:
# Current implementation uses a temporary dataset until the official
# World Cup 2026 competition data becomes available.
#
# =============================================================================
elif st.session_state.page == "match results":

    st.subheader("📊 Results")
    df_fixtures_copaam = load_fixtures_pruebas()

    df_fixtures_wc26 = load_fixtures()
    render_results(df_fixtures_wc26)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.html("""
<div style="text-align:center; margin-top:40px; font-size:14px; color:#aaa;">

⚽ <b>World Cup 2026 Analytics Platform</b>
<br><br>

📬 Contact: cesc.blanco@gmail.com |
🔗 <a href="https://github.com/CescBlanco" target="_blank">GitHub</a> |
💼 <a href="https://www.linkedin.com/in/cescblanco" target="_blank">LinkedIn</a> 
<br><br>

📊 Data sources:
<a href="https://www.fotmob.com" target="_blank">FotMob</a> |
<a href="https://www.whoscored.com" target="_blank">WhoScored</a>

</div>
""")