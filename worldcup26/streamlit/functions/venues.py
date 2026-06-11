import pandas as pd
import numpy as np
import re

import streamlit as st
from pydeck.data_utils.viewport_helpers import compute_view
import pydeck as pdk

def clean_coord(text: str) -> str:
    """
    Normalize coordinate text for parsing.

    This function cleans raw coordinate strings by:
    - Normalizing non-breaking spaces
    - Standardizing prime symbols (′, ″)
    - Removing commas

    Args:
        text (str): Raw coordinate string.

    Returns:
        str: Cleaned coordinate string.
    """

    # 🔹 Ensure string type
    text = str(text)

    # 🔹 Normalize non-breaking spaces
    text = text.replace("\u00a0", " ")

    # 🔹 Normalize prime symbols
    text = text.replace("′", "'").replace("″", '"')

    # 🔹 Remove commas for safer parsing
    text = text.replace(",", " ")

    return text


def dms_to_decimal(d: float | str,m: float | str,s: float | str,direction: str) -> float:
    """
    Convert DMS (Degrees, Minutes, Seconds) to decimal degrees.

    Args:
        d (float | str): Degrees.
        m (float | str): Minutes.
        s (float | str): Seconds.
        direction (str): Direction indicator (N, S, E, W).

    Returns:
        float: Coordinate in decimal degrees.
    """

    # 🔹 Convert to decimal degrees
    decimal = float(d) + float(m) / 60 + float(s) / 3600

    # 🔹 Apply sign for southern and western hemispheres
    if direction in ["S", "W"]:
        decimal *= -1

    return decimal

def parse_dms(coord: str | None) -> tuple[float, float]:
    """
    Parse a DMS coordinate string into decimal latitude and longitude.

    This function extracts latitude and longitude from a raw DMS
    string and converts them into decimal degrees.

    Args:
        coord (str | None): Raw coordinate string.

    Returns:
        tuple[float, float]:
            (latitude, longitude) in decimal format.
            Returns (np.nan, np.nan) if parsing fails.
    """

    # 🔹 Handle missing values
    if pd.isna(coord):
        return np.nan, np.nan

    # 🔹 Clean coordinate string
    coord = clean_coord(coord)

    # 🔹 Flexible regex for DMS format
    pattern = r"(\d+)\D+(\d+)?\D+([\d\.]+)?\D*([NSEW])"
    matches = re.findall(pattern, coord)

    # 🔹 Expect at least lat + lon
    if len(matches) >= 2:

        def convert(m):
            d = m[0]
            mnt = m[1] if m[1] != "" else 0
            s = m[2] if m[2] != "" else 0
            direction = m[3]

            return dms_to_decimal(d, mnt, s, direction)

        lat = convert(matches[0])
        lon = convert(matches[1])

        return lat, lon

    return np.nan, np.nan

def filters_venues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply interactive filters to the venues dataset.

    This function allows filtering stadiums by country using a
    Streamlit multiselect widget.

    Args:
        df (pd.DataFrame): Venues dataset.

    Returns:
        pd.DataFrame: Filtered venues dataset.
    """

    # 🔹 Country filter UI
    countries = st.multiselect("🌍 Filter by country", sorted(df["country"].unique()), default=df["country"].unique())

    # 🔹 Apply filter
    df_venues_filtered = df[df["country"].isin(countries)]

    return df_venues_filtered

def metrics_venues(df: pd.DataFrame) -> None:
    """
    Display key statistics for the venues dataset.

    Shows:
    - Number of stadiums
    - Number of countries
    - Average capacity
    - Maximum capacity

    Args:
        df (pd.DataFrame): Venues dataset.

    Returns:
        None
    """

    with st.container(border=True):

        # 🔹 Layout metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🏟️ Stadiums", len(df))
        col2.metric("🌍 Countries", df["country"].nunique())
        col3.metric("👥 Avg capacity", int(df["capacity"].mean()))
        col4.metric("🏆 Max capacity", int(df["capacity"].max()))

def map_venues(df: pd.DataFrame) -> None:
    """
    Render an interactive map of stadium locations using PyDeck.

    This function visualizes stadiums on a map using latitude and
    longitude coordinates, with tooltips showing detailed metadata.

    Args:
        df (pd.DataFrame): Venues dataset containing coordinates.

    Returns:
        None
    """

    # 🔹 Compute optimal map view
    view_state = compute_view( df[["lon", "lat"]],view_proportion=0.8)

    # 🔹 Map layer configuration
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

    # 🔹 Tooltip configuration
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

    # 🔹 Render map
    st.pydeck_chart( pdk.Deck( layers=[layer], initial_view_state=view_state, tooltip=tooltip ))

def stadiums_list(df: pd.DataFrame) -> None:
    """
    Render a list of stadiums using expandable cards.

    Each stadium displays:
    - City, country, and region
    - Capacity
    - Stadium image

    Args:
        df (pd.DataFrame): Venues dataset.

    Returns:
        None
    """

    # 🔹 Section title
    st.subheader(f"📍 Stadium list ({len(df)})")

    # 🔹 Create grid layout
    cols = st.columns(3)

    # 🔹 Render each stadium card
    for i, (_, row) in enumerate(df.iterrows()):

        with cols[i % 3]:

            with st.expander(f"🏟️ {row['name']}"):

                col1, col2 = st.columns([3, 3])

                with col1:
                    st.write(f"**City**: {row['city']}")
                    st.write(f"**Country**: {row['country']}")
                    st.write(f"**Region**: {row['region']}")
                    st.write(f"**Capacity**: {row['capacity']}")

                with col2:
                    st.image(row["photo_stadium"], width=300)

