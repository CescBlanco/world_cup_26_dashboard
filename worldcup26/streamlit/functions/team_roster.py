import pandas as pd
import streamlit as st

def format_market_value(value):

        if pd.isna(value):
            return None

        value = float(value)

        if value >= 1_000_000:
            return f"€{value/1_000_000:.1f}M"

        return f"€{value/1000:.0f}K"

def rating_color(rating):
    if pd.isna(rating):
        return "#808080"  # gris

    if rating < 5:
        return "#ff4d4d"  # rojo
    elif rating < 7:
        return "#ffa500"  # naranja
    elif rating < 8:
        return "#32cd32"  # verde
    else:
        return "#1e90ff"  # azul

def team_header(players_team):
    team_name = players_team["team_name"].iloc[0]
    team_logo = players_team["team_logo"].iloc[0]

    coach_df = players_team[players_team["role.fallback"] == "Coach" ]
    players_df = players_team[players_team["role.fallback"] != "Coach"]

    if not coach_df.empty:

        coach = coach_df.iloc[0]

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

def team_sumary(players_team):
        # =========================
        # TEAM SUMMARY
        # =========================

        players_only = players_team[players_team["role.fallback"].isin(["Keeper", "Defender", "Midfielder", "Attacker"])]

        total_players = len(players_only)
        avg_age = round(players_only["age"].mean(), 1)
        total_value = players_only["transferValue"].fillna(0).sum()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Players", total_players)

        with c2:
            st.metric("Average Age", avg_age)

        with c3:
            st.metric("Market Value",format_market_value(total_value))

        st.divider()

        return players_only

def star_players_mk_value(players_only):

        # =========================
        # STAR PLAYERS
        # =========================
        st.subheader("⭐ Top Market Value")

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

def squad_by_postion(players_only):

    # =========================
    # SQUAD BY POSITION
    # =========================
    POSITION_SECTIONS = {
        "Keeper": "🧤 Goalkeepers",
        "Defender": "🛡️ Defenders",
        "Midfielder": "⚙️ Midfielders",
        "Attacker": "⚽ Attackers"
    }

    for role, title in POSITION_SECTIONS.items():

        players = players_only[players_only["role.fallback"] == role]
        if players.empty:
            continue

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
                                    color:white;
                                    border-radius:8px;
                                    padding:6px 10px;
                                    text-align:right;
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
