import pandas as pd
import numpy as np
import re

import streamlit as st
from pydeck.data_utils.viewport_helpers import compute_view
import pydeck as pdk

def clean_coord(text):
    text = str(text)

    # normalizar espacios raros
    text = text.replace("\u00a0", " ")

    # normalizar símbolos
    text = text.replace("′", "'").replace("″", '"')

    # quitar comas
    text = text.replace(",", " ")

    return text


def dms_to_decimal(d, m, s, direction):
    decimal = float(d) + float(m)/60 + float(s)/3600
    if direction in ["S", "W"]:
        decimal *= -1
    return decimal


def parse_dms(coord):

    if pd.isna(coord):
        return np.nan, np.nan

    coord = clean_coord(coord)

    # 🔥 regex ultra flexible (incluye decimales en segundos)
    pattern = r"(\d+)\D+(\d+)?\D+([\d\.]+)?\D*([NSEW])"

    matches = re.findall(pattern, coord)

    # necesitamos 2 matches (lat + lon)
    if len(matches) >= 2:

        def convert(m):
            d = m[0]
            mnt = m[1] if m[1] != "" else 0
            s = m[2] if m[2] != "" else 0
            dir = m[3]

            return dms_to_decimal(d, mnt, s, dir)

        lat = convert(matches[0])
        lon = convert(matches[1])

        return lat, lon

    return np.nan, np.nan

def filters_venues(df):

    # --------------------
    # FILTERS
    # --------------------
    countries = st.multiselect("🌍 Filter by country",sorted(df["country"].unique()), default=df["country"].unique())

    df_venues_filtered = df[df["country"].isin(countries)]

    return df_venues_filtered

def metrics_venues(df):
    with st.container(border=True):
        # --------------------
        # METRICS
        # --------------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🏟️ Stadiums", len(df))
        col2.metric("🌍 Countries", df["country"].nunique())
        col3.metric("👥 Avg capacity", int(df["capacity"].mean()))
        col4.metric("🏆 Max capacity", int(df["capacity"].max()))

def map_venues(df):
    # --------------------
    # MAP
    # --------------------
    view_state = compute_view(df[["lon", "lat"]], view_proportion=0.8)

    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position='[lon, lat]',
        get_radius="radius",
        radius_units="meters",
        radius_min_pixels=3,
        radius_max_pixels=20,
        get_fill_color='[30, 144, 255, 180]', 
        get_line_color='[255, 255, 255, 120]',
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True
    )

    tooltip = {
        "html": """
        <div style="font-size:13px; line-height:1.4;">

            <div style="font-size:16px; font-weight:bold;">
                🏟️ {name}
            </div>

            <div style="opacity:0.85; margin-bottom:6px;">
                {city}, {country}
            </div>

            <hr style="margin:6px 0;" />

            👥 <b>Capacity:</b> {capacity} spectators<br/>
            📍 <b>Region:</b> {region}<br/>
            📅 <b>Year of Foundation:</b> {year_fundation}<br/>
            📐 <b>Dimensions:</b> {dimensions}<br/>

            <hr style="margin:6px 0;" />

            🌎 <b>FIFA name:</b><br/>
            <span style="opacity:0.9;">{fifa_name}</span>

        </div>
        """,
        "style": {
            "backgroundColor": "rgba(0,0,0,0.85)",
            "color": "white",
            "padding": "10px",
            "borderRadius": "8px",
            "maxWidth": "300px"
        }
    }

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    ))

def stadiums_list(df):

    st.subheader(f"📍 Stadium list ({len(df)})")
    cols = st.columns(3)

    for i, (_, row) in enumerate(df.iterrows()):

        with cols[i % 3]:

            with st.expander(f"🏟️ {row['name']}"):
                col1, col2 = st.columns([3,3])
                
                with col1:
                    st.write(f"**City**: {row['city']}")
                    st.write(f"**Country**: {row['country']}")
                    st.write(f"**Region**: {row['region']}")
                    st.write(f"**Capacity**: {row['capacity']}")
                    
                with col2:
                    st.image(row["photo_stadium"], width=300)

