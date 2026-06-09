from functions.venues import *

def render_venues(df):
    df[["lat", "lon"]] = df["coords"].apply(lambda x: pd.Series(parse_dms(x)))

    df_venues_filtered= filters_venues(df)

    metrics_venues(df_venues_filtered)

    map_venues(df_venues_filtered)

    stadiums_list(df_venues_filtered)