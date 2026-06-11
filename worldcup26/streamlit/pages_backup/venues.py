from functions.venues import *

def render_venues(df: pd.DataFrame) -> None:
    """
    Render the complete venues (stadiums) page.

    This function orchestrates the full venues dashboard, including:
    - Coordinate parsing (DMS → latitude/longitude)
    - Interactive filters
    - Key statistics metrics
    - Interactive map visualization
    - Stadiums list view

    Args:
        df (pd.DataFrame): Dataset containing stadium/venue information,
            including coordinate strings and metadata.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If any rendering step fails.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_columns = ["coords"]

    # 🔹 Validate required columns
    missing_columns = [ col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    try:

        # =========================
        # COORDINATE PARSING
        # =========================
        df[["lat", "lon"]] = df["coords"].apply(lambda x: pd.Series(parse_dms(x)) )

        # =========================
        # FILTERS
        # =========================
        df_venues_filtered = filters_venues(df)

        # =========================
        # METRICS
        # =========================
        metrics_venues(df_venues_filtered)

        # =========================
        # MAP VISUALIZATION
        # =========================
        map_venues(df_venues_filtered)

        # =========================
        # STADIUM LIST
        # =========================
        stadiums_list(df_venues_filtered)

    except Exception as e:
        raise RuntimeError(f"Failed to render venues page: {e}")