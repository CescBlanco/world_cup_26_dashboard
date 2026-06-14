import pandas as pd
import streamlit as st

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

def team_header(players_team: pd.DataFrame) -> None:
    """
    Render the team header section.

    Displays the team name, logo, and head coach information.

    Args:
        players_team (pd.DataFrame): Team squad dataset.

    Returns:
        None

    Raises:
        TypeError: If players_team is not a DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If the header cannot be rendered.
    """

    # 🔹 Validate input type
    if not isinstance(players_team, pd.DataFrame):
        raise TypeError("players_team must be a pandas DataFrame")

    required_columns = [ "team_name", "team_logo", "role.fallback", "member_photo", "name", "cname"]

    missing_columns = [ col for col in required_columns if col not in players_team.columns]

    if missing_columns:
        raise KeyError( f"Missing required columns: {missing_columns}")

    try:
        # 🔹 Extract team information
        team_name = players_team["team_name"].iloc[0]
        team_logo = players_team["team_logo"].iloc[0]

        coach_df = players_team[players_team["role.fallback"] == "Coach"]
        if coach_df.empty:
            return

        coach = coach_df.iloc[0]

        # 🔹 Create header layout
        col1, col2, col3 = st.columns([1.2, 4, 4])

        with col1:
            st.image(coach["member_photo"], width=130)

        with col2:
            st.markdown(f"## {team_name}")
            st.markdown(f"**Coach:** {coach['name']}")

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

def team_summary(players_team: pd.DataFrame) -> pd.DataFrame:
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
