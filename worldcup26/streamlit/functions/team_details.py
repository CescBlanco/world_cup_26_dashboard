import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

def clean_signed_value( value: str | int | float | None) -> float:
    """
    Clean and convert a signed numeric value.

    This function normalizes Unicode minus signs and converts
    the input value into a numeric representation. Invalid
    values are converted to NaN.

    Args:
        value (str | int | float | None):
            Input value to be converted.

    Returns:
        float:
            Numeric value or NaN if conversion fails.
    """

    # 🔹 Handle missing values
    if pd.isna(value):
        return np.nan

    # 🔹 Convert to string and remove surrounding spaces
    value = str(value).strip()

    # 🔹 Normalize Unicode minus signs
    value = value.replace("−", "-")

    # 🔹 Convert to numeric value
    return pd.to_numeric(value, errors="coerce" )

def classify_change( value: float | int | None) -> str:
    """
    Classify a numeric change as positive, negative, or neutral.

    Args:
        value (float | int | None):
            Numeric value representing a change.

    Returns:
        str:
            One of:
            - "positive"
            - "negative"
            - "neutral"
    """

    # 🔹 Handle missing values
    if pd.isna(value):
        return "neutral"

    # 🔹 Positive variation
    if value > 0:
        return "positive"

    # 🔹 Negative variation
    if value < 0:
        return "negative"

    # 🔹 No variation
    return "neutral"

def clean_change_ranking_prev( value: str | int | None) -> int | float:
    """
    Clean and convert a ranking change value.

    This function removes surrounding whitespace,
    normalizes Unicode minus signs, and converts the
    value to an integer representation.

    Args:
        value (str | int | None):
            Ranking change value.

    Returns:
        int | float:
            Integer value or NaN if the input is missing.

    Raises:
        ValueError: If the value cannot be converted to an integer.
    """

    # 🔹 Handle missing values
    if pd.isna(value):
        return np.nan

    # 🔹 Convert to string and remove surrounding spaces
    value = str(value).strip()

    # 🔹 Normalize Unicode minus signs
    value = value.replace("−", "-")

    # 🔹 Convert to integer
    return int(value)

def format_market_value(value: float | int | None) -> str | None:
    """
    Format a market value into a human-readable currency string.

    Values greater than or equal to one million are displayed in
    millions (M), while smaller values are displayed in thousands (K).

    Args:
        value (float | int | None): Market value amount.

    Returns:
        str | None:
            Formatted market value string, or None if the value is missing.

    Raises:
        TypeError: If value is not numeric.
    """

    # 🔹 Handle missing values
    if pd.isna(value):
        return None

    # 🔹 Validate input type
    if not isinstance(value, (int, float)):
        raise TypeError("value must be numeric")

    value = float(value)

    # 🔹 Format large values in millions
    if value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}M"

    # 🔹 Format smaller values in thousands
    return f"€{value / 1000:.0f}K"

def rating_color(rating: float | int | None) -> str:
    """
    Determine the display color associated with a player rating.

    Args:
        rating (float | int | None): Player rating value.

    Returns:
        str: Hexadecimal color code.

    Raises:
        TypeError: If rating is not numeric.
    """

    # 🔹 Handle missing ratings
    if pd.isna(rating):
        return "#808080"

    # 🔹 Validate input type
    if not isinstance(rating, (int, float)):
        raise TypeError("rating must be numeric")

    # 🔹 Rating color scale
    if rating < 5:
        return "#ff4d4d"

    if rating < 7:
        return "#ffa500"

    if rating < 8:
        return "#32cd32"

    return "#1e90ff"
    
def team_details_bloc1(df: pd.DataFrame) -> None:
    """
    Render the first section of the team details page.

    This block displays:
    - Team header (logo and name)
    - Recent form visualization (W/D/L)
    - ELO and ranking yearly changes
    - FIFA ranking variation

    Args:
        df (pd.DataFrame): Team dataset containing performance metrics.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If UI rendering fails.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    try:
        # =========================
        # TEAM HEADER
        # =========================
        subcol1, subcol2 = st.columns(2)

        with subcol1:
            st.image(df["team_photo"].iloc[0], width=150)

        with subcol2:
            st.markdown(f"## {df['Squad'].iloc[0]}")

        # =========================
        # RECENT FORM
        # =========================
        with st.container(border=True):

            import ast

            form = ast.literal_eval(df["latest_results"].iloc[0])

            st.subheader("📈 Recent Form")

            cols = st.columns(len(form))

            for i, r in enumerate(form):

                # 🔹 Color mapping for match results
                color = {
                    "W": "#00C853",
                    "D": "#FFB300",
                    "L": "#D50000"
                }.get(r, "#777")

                with cols[i]:

                    st.markdown(
                        f"""
                        <div style="
                            width:50px;
                            height:50px;
                            border-radius:50%;
                            background:{color};
                            color:white;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-weight:bold;
                            margin:auto;
                        ">
                            {r}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.write(" ")

        # =========================
        # ELO & RANKING TRENDS
        # =========================
        with st.container(border=True):

            st.subheader("Comparative ELO change (1 year)")

            # 🔹 Clean numeric values
            df["one_year_change_elo_clean"] = df["one_year_change_elo"].apply(clean_signed_value)
            df["one_year_change_ranking_clean"] = df["one_year_change_ranking"].apply(clean_signed_value)

            # 🔹 Classify trends
            df["elo_trend"] = df["one_year_change_elo_clean"].apply(classify_change)
            df["ranking_trend"] = df["one_year_change_ranking_clean"].apply(classify_change)

            elo_change = df["one_year_change_elo_clean"].iloc[0]

            if pd.notna(elo_change):

                if elo_change > 0:
                    st.success(f"📈 +{int(elo_change)} ELO points change")

                elif elo_change < 0:
                    st.error(f"📉 {int(elo_change)} ELO points change")

                else:
                    st.info("➖ No ELO points change")

            ranking_change = df["one_year_change_ranking_clean"].iloc[0]

            if pd.notna(ranking_change):

                if ranking_change > 0:
                    st.success(f"📈 +{int(ranking_change)} ranking change")

                elif ranking_change < 0:
                    st.error(f"📉 {int(ranking_change)} ranking change")

                else:
                    st.info("➖ No ranking change")

        # =========================
        # FIFA RANK CHANGE
        # =========================
        with st.container(border=True):

            ranking_change = clean_change_ranking_prev(df["prev_rank"].iloc[0])

            if ranking_change > 0:
                st.success(f"📈 FIFA Ranking improved by {ranking_change} positions.")

            elif ranking_change < 0:
                st.error(f"📉 FIFA Ranking dropped by {abs(ranking_change)} positions.")

            else:
                st.info("➖ No change in FIFA Ranking.")

    except Exception as e:
        raise RuntimeError(f"Failed to render team details block 1: {e}")

def team_details_bloc2(df: pd.DataFrame) -> None:
    """
    Render the second section of the team details page.

    This block includes:
    - FIFA and Elo rankings overview
    - Historical performance metrics
    - Goals statistics
    - Result distribution visualizations

    Args:
        df (pd.DataFrame): Team dataset with historical statistics.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If visualization rendering fails.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    try:

        # =========================
        # RANKINGS OVERVIEW
        # =========================
        with st.container(border=True):

            st.subheader("🌍 Rankings & Ratings")

            r1, r2, r3, r4, r5 = st.columns(5)

            with r1:
                st.metric("🌍 FIFA Rank", f"#{df['rank'].iloc[0]}")

            with r2:
                st.metric("⚡ Elo Rank", f"#{df['actual_ranking'].iloc[0]}")

            with r3:
                st.metric("⭐ FIFA Points", f"{df['points'].iloc[0]}")

            with r4:
                st.metric("ELO Points", f"{df['actual_elo'].iloc[0]}")

            with r5:
                st.metric("📈 ELO Points Change", df["one_year_change_elo"].iloc[0])

        # =========================
        # HISTORICAL RECORD
        # =========================
        with st.container(border=True):

            st.subheader("📊 Historical Record")

            wins = df["matches_wins"].iloc[0]
            draws = df["matches_draws"].iloc[0]
            losses = df["matches_losses"].iloc[0]

            home = df["matches_home"].iloc[0]
            away = df["matches_away"].iloc[0]
            neutral = df["matches_neutral"].iloc[0]

            total = df["matches_total"].iloc[0]

            gf = df["goals_for"].iloc[0]
            ga = df["goals_against"].iloc[0]

            win_rate = wins / total * 100
            goal_ratio = gf / ga

            s1, s2, s3, s4, s5 = st.columns(5)

            with s1:
                st.metric("Total matches played", f"{total}")

            with s2:
                st.metric("🏆 Win Rate", f"{win_rate:.1f}%")

            with s3:
                st.metric("⚽ Goals Scored", f"{gf}")

            with s4:
                st.metric("⚽ Goals Against", f"{ga}")

            with s5:
                st.metric("📈 Goals Ratio", f"{goal_ratio:.2f}")

        # =========================
        # RESULT DISTRIBUTIONS
        # =========================
        with st.container(border=True):

            pie_1, pie_2 = st.columns(2)

            # 🔹 Home / Away / Neutral distribution
            with pie_1:

                st.markdown("<h5 style='text-align:center;color:#9ca3af'>Results Distribution (Home/Away/Neutral)</h5>", unsafe_allow_html=True)

                pie_df = pd.DataFrame({ "Result": ["Home", "Away", "Neutral"],
                    "Count": [home, away, neutral]
                    })

                fig = px.pie(
                    pie_df,
                    values="Count",
                    names="Result",
                    color="Result",
                    color_discrete_map={
                        "Home": "#00C853",
                        "Away": "#FFB300",
                        "Neutral": "#D50000"
                    }
                )

                fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))

                st.plotly_chart(fig, use_container_width=True)

            # 🔹 Wins / Draws / Losses distribution
            with pie_2:

                st.markdown(
                    "<h5 style='text-align:center;color:#9ca3af'>Results Distribution (Wins/Draws/Losses)</h5>",
                    unsafe_allow_html=True
                )

                pie_df = pd.DataFrame({
                    "Result": ["Wins", "Draws", "Losses"],
                    "Count": [wins, draws, losses]
                })

                fig = px.pie(
                    pie_df,
                    values="Count",
                    names="Result",
                    color="Result",
                    color_discrete_map={
                        "Wins": "#00C853",
                        "Draws": "#FFB300",
                        "Losses": "#D50000"
                    }
                )

                fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        raise RuntimeError(f"Failed to render team details block 2: {e}")

def team_header(players_team: pd.DataFrame) -> None:
    """
    Render the team header section.

    This function displays the team name, team logo, and coach
    information. It separates coach data from player data and
    renders a structured header layout using Streamlit columns.

    Args:
        players_team (pd.DataFrame): Team dataset containing player
            and coach information.

    Returns:
        None

    Raises:
        TypeError: If players_team is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If the header rendering fails.
    """

    # 🔹 Validate input type
    if not isinstance(players_team, pd.DataFrame):
        raise TypeError("players_team must be a pandas DataFrame")

    required_columns = ["team_name", "team_logo", "role.fallback"]

    # 🔹 Validate required columns
    missing_columns = [ col for col in required_columns if col not in players_team.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    try:
        # 🔹 Extract team metadata
        team_name = players_team["team_name"].iloc[0]
        team_logo = players_team["team_logo"].iloc[0]

        # 🔹 Split coach vs players
        coach_df = players_team[ players_team["role.fallback"] == "Coach"]

        if coach_df.empty:
            return

        coach = coach_df.iloc[0]

        # =========================
        # HEADER LAYOUT
        # =========================
        col1, col2, col3 = st.columns([1.2, 4, 4])

        with col1:
            st.image(coach["member_photo"], width=130)

        with col2:
            st.markdown(f"## {team_name}")
            st.markdown(f"**Coach:** {coach['name']}")

            # 🔹 Optional coach country info
            if pd.notna(coach["cname"]):
                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:8px;
                        color:#9e9e9e;
                        font-size:0.85rem;
                        margin-top:4px;
                    ">
                        <img src="{team_logo}" width="18">
                        <span>{coach['cname']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        raise RuntimeError(f"Failed to render team header: {e}")

def team_sumary(players_team: pd.DataFrame) -> pd.DataFrame:
    """
    Compute and render team summary statistics.

    This function filters out non-player roles (e.g., coach),
    calculates key squad metrics (players count, average age,
    and total market value), displays them in Streamlit metrics,
    and returns the filtered players dataset.

    Args:
        players_team (pd.DataFrame): Team dataset including players
            and staff information.

    Returns:
        pd.DataFrame:
            Filtered dataset containing only players.

    Raises:
        TypeError: If players_team is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If summary computation fails.
    """

    # 🔹 Validate input type
    if not isinstance(players_team, pd.DataFrame):
        raise TypeError("players_team must be a pandas DataFrame")

    required_columns = ["role.fallback", "age", "transferValue"]

    # 🔹 Validate required columns
    missing_columns = [ col for col in required_columns if col not in players_team.columns]

    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    try:
        # =========================
        # FILTER PLAYERS ONLY
        # =========================
        players_only = players_team[players_team["role.fallback"].isin(["Keeper", "Defender", "Midfielder", "Attacker"])]

        # =========================
        # METRICS CALCULATION
        # =========================
        total_players = len(players_only)
        avg_age = round(players_only["age"].mean(), 1)
        total_value = players_only["transferValue"].fillna(0).sum()

        # =========================
        # STREAMLIT METRICS
        # =========================
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Players", total_players)

        with c2:
            st.metric("Average Age", avg_age)

        with c3:
            st.metric("Market Value", format_market_value(total_value))

        st.divider()

        return players_only

    except Exception as e:
        raise RuntimeError(f"Failed to compute team summary: {e}")

def star_players_market_value(players_only: pd.DataFrame) -> None:
    """
    Render the top players by market value.

    Displays the five most valuable players in the squad.

    Args:
        players_only (pd.DataFrame): Players dataset.

    Returns:
        None

    Raises:
        TypeError: If players_only is not a DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If the section cannot be rendered.
    """

    # =========================
    # STAR PLAYERS
    # =========================
    st.subheader("⭐ Top Market Value")

    # 🔹 Select top five players by market value
    top_players = players_only.sort_values("transferValue", ascending=False).head(5)

    cols = st.columns(5)

    for i, (_, player) in enumerate(top_players.iterrows()):

        with cols[i]:
        

            if pd.notna(player["member_photo"]):
                st.image(player["member_photo"], width=120)

            st.caption(player["name"])

            value = format_market_value( player["transferValue"])

            st.write(value)

    st.divider()


def squad_by_position( players_only: pd.DataFrame) -> None:
    """
    Render squad information grouped by playing position.

    Players are organized into goalkeepers, defenders,
    midfielders, and attackers. Each player card displays
    personal information, market value, rating, and injury status.

    Args:
        players_only (pd.DataFrame): Players dataset.

    Returns:
        None

    Raises:
        TypeError: If players_only is not a DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If player cards cannot be rendered.
    """

    # 🔹 Define position sections
    POSITION_SECTIONS = {
        "Keeper": "🧤 Goalkeepers",
        "Defender": "🛡️ Defenders",
        "Midfielder": "⚙️ Midfielders",
        "Attacker": "⚽ Attackers"
    }

    # 🔹 Iterate through each squad role
    for role, title in POSITION_SECTIONS.items():

        players = players_only[players_only["role.fallback"] == role]
        # 🔹 Skip empty position groups
        if players.empty:
            continue
        
        # 🔹 Create player card layout
        st.subheader(title)

        cols = st.columns(4)

        for i, (_, player) in enumerate(players.iterrows()):

            with cols[i % 4]:

                with st.container(border=True):

                    if pd.notna(player["member_photo"]):

                        img_col1, img_col2 = st.columns([3,1])

                        with img_col1:
                            st.image(player["member_photo"], width=120)

                        with img_col2:
                            if pd.notna(player.get("team_logo")):
                                st.image(player["team_logo"], width=90)

                    st.markdown( f"**{player['name']}**")

                    shirt = (int(player["shirtNumber"]) if pd.notna(player["shirtNumber"]) else "-")

                    position = ( player["positionIdsDesc"] if pd.notna(player["positionIdsDesc"]) else "")

                    st.caption( f"#{shirt} • {position}")

                    if pd.notna(player["cname"]):
                        st.write(player["cname"])

                    if pd.notna(player["age"]) and pd.notna(player["dateOfBirth"]):
                        dob = pd.to_datetime(player["dateOfBirth"]).strftime("%d-%m-%Y")
                        st.caption(f" Date of Birth: {dob}, Age: {int(player['age'])} years")

                    if pd.notna(player["height"]):
                        st.caption(f" Height: {int(player['height'])} cm")

                    value = format_market_value(player["transferValue"])
                    rating = player.get("rating")

                    metric_col1, metric_col2, metric3 = st.columns([3,1,2])

                    with metric_col1:
                        if value:
                            st.metric("Market Value", value)

                    with metric3:                         

                        if pd.notna(rating):

                            color = rating_color(rating)

                            st.markdown(
                                f"""
                                <div style="
                                    background:{color};
                                    color:black;
                                    border-radius:8px;
                                    padding:6px 10px;
                                    text-align:center;
                                    font-weight:bold;
                                ">
                                    {float(rating):.1f}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        else:
                            st.caption("Not Rated")

                    if ( pd.notna(player["injured"]) and player["injured"]):
                        expected = (player["injury.expectedReturn"] 
                                    if pd.notna( player["injury.expectedReturn"])  else "Unknown")

                        st.error(  f"🚑 Injured\n\nReturn: {expected}")
