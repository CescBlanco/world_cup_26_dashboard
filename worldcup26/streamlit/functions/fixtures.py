import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
from concurrent.futures import ThreadPoolExecutor
import requests
from utils.mapping import NAME_MAPPING2


def match_status(row):
    return "played" if pd.notna(row["homeScore"]) and pd.notna(row["awayScore"]) else "scheduled"

def build_event(row):
        
        STATUS_COLORS = { "played": "#057C0B","scheduled": "#00E5FF"}

        status = match_status(row)
        color = STATUS_COLORS[status]

        home = row["homeTeamName"]
        away = row["awayTeamName"]

        dt = row["match_datetime"]

        # 🔥 TITLE limpio (SIN hora)
        if status == "scheduled":
            title = f"⚽ {home} vs {away}"
        else:
            title = f"⚽ {home} {int(row['homeScore'])}-{int(row['awayScore'])} {away}"

        return {
            "title": title,
            "start": dt.isoformat(),   
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "home": home,
                "away": away,
                "home_logo": row["homeTeamPhoto"],
                "away_logo": row["awayTeamPhoto"],
                "status": status,
                "score": (
                    f"{int(row['homeScore'])}-{int(row['awayScore'])}"
                    if status == "played" else None
                ),
                "time": dt.strftime("%H:%M"),
                "stage": row["stageName"],
                "round": row["matchround"]
            }
        }

def calendar_function(df):
    # ---------------------------
    # CALENDAR
    # ---------------------------
    state = calendar(
        events=df,
        options={
            "initialView": "dayGridMonth",
            "height": 750,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "eventTimeFormat": {
                "hour": "2-digit",
                "minute": "2-digit",
                "hour12": False
            },
            "displayEventTime": True
        },
        key="wc_calendar"
    )
    return state

def click_event_and_info(state):
    # ---------------------------
    # CLICK EVENT (UI PRO)
    # ---------------------------
    if state.get("eventClick"):
        st.subheader("🏟️ MATCH OVERVIEW")
        with st.container(border=True):
            event = state["eventClick"]["event"]
            props = event.get("extendedProps", {})

            st.caption(event["title"])

            st.write(" ")

            col1, col2, col3 = st.columns([1, 4,1])

            with col1:
                st.image(props.get("home_logo"), width=90)
                st.write(props.get("home"))
            
            with col2:

                st.write(f"🏆 Stage: {props.get('stage')}")
                st.write(f"🔁 Round: {props.get('round')}")

                if props.get("status") == "played":
                    st.success(f"Final score: {props.get('score')}")
                else:
                    st.info(f"Kick-off: {props.get('time')}")

            with col3:
                st.image(props.get("away_logo"), width=90)
                st.write(props.get("away"))

        st.divider()

def parse_table_standings(data, group_idx=0):

    df_tables= pd.DataFrame(data[0]['data']['tables'])[['leagueId', 'leagueName', 'legend', 'table']]

    group=pd.DataFrame(df_tables.iloc[group_idx]).T

    legend = group['legend'].iloc[0]
    color_map = {item["color"]: {"title": item["title"], "tKey": item["tKey"]} for item in legend}

    teams= pd.DataFrame(group['table'].iloc[0]['all'])
    teams["name"] = teams["name"].replace(NAME_MAPPING2)
    teams[["goals_for", "goals_against"]] = teams["scoresStr"].str.split("-", expand=True)
    teams["competition"] = teams["qualColor"].map(lambda x: color_map.get(x, {}).get("title"))
    teams["tKey"] = teams["qualColor"].map(lambda x: color_map.get(x, {}).get("tKey"))

    teams["team_logo"] = "https://images.fotmob.com/image_resources/logo/teamlogo/"  + teams["id"].astype(str) + ".png"
    teams = teams[['qualColor','idx','name','id','team_logo','played','wins','draws',
                'losses',"goals_for","goals_against",'goalConDiff','pts','competition']]

    return teams

def extract_standings_groups_fotmob(group_idx=0):
    
    response = requests.get("https://www.fotmob.com/api/data/tltable?leagueId=77&teams=%5B5796%5D")
    response.raise_for_status()
    data = response.json()
    return parse_table_standings(data, group_idx=group_idx)

def create_plot_standings(group_df):

    # headers
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([1, 4, 2, 2, 2, 2, 2, 2, 2, 2])
    with c1:
        st.write("")
    with c2:
        st.markdown("""
            **Team**  
            <small>(Qualification Status)</small>
            """, unsafe_allow_html=True)
    with c3:
        st.write("Played Games")
    with c4:
        st.write("Wins")
    with c5:
        st.write("Draws")
    with c6:
        st.write("Losses")
    with c7:
        st.write("Goals Scored")
    with c8:
        st.write("Goals Against")
    with c9:
        st.write("Goal Diff")
    with c10:
        st.write("Points")

    st.markdown("<hr style='margin:4px 0 6px 0;'>", unsafe_allow_html=True)

    #rows
    for _, row in group_df.iterrows():

        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
            [1, 5, 2, 2, 2, 2, 2, 2, 2, 2]
        )

        with c1:
            st.image(row["team_logo"], width=40)

        with c2:
            st.markdown(f"**{row['idx']}. {row['name']}**")
            if pd.notna(row["competition"]):
                st.caption(row["competition"])

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

def table_groups():

    st.markdown(f"### 🥇TABLE GROUPS ")
    
    with ThreadPoolExecutor(max_workers=13) as executor:
        groups = list(
            executor.map(
                extract_standings_groups_fotmob,
                range(13)
            )
        )

    block1, block2 = st.columns(2)

    with block1:

        with st.container(border=True):
            st.markdown("### GROUP A")
            create_plot_standings(groups[0])
        
        with st.container(border=True):
            st.markdown(f"### GROUP C ") 
            create_plot_standings(groups[2])
        
        with st.container(border=True):
            st.markdown(f"### GROUP E ") 
            create_plot_standings(groups[4])

        with st.container(border=True):
            st.markdown(f"### GROUP G ") 
            create_plot_standings(groups[6])
        
        with st.container(border=True):
            st.markdown(f"### GROUP I ") 
            create_plot_standings(groups[8])
        
        with st.container(border=True):
            st.markdown(f"### GROUP K ") 
            create_plot_standings(groups[10])


    with block2:
        with st.container(border=True):
            st.markdown("### GROUP B")
            create_plot_standings(groups[1])
        
        with st.container(border=True):
            st.markdown(f"### GROUP D ") 
            create_plot_standings(groups[3])

        with st.container(border=True):
            st.markdown(f"### GROUP F ") 
            create_plot_standings(groups[5])
        
        with st.container(border=True):
            st.markdown(f"### GROUP H ") 
            create_plot_standings(groups[7])

        with st.container(border=True):
            st.markdown(f"### GROUP J ") 
            create_plot_standings(groups[9])
        
        with st.container(border=True):
            st.markdown(f"### GROUP L ") 
            create_plot_standings(groups[11])
    st.divider()
    with st.container(border=True):
            st.markdown(f"### BEST 3RD PLACE TEAMS") 
            create_plot_standings(groups[12])

