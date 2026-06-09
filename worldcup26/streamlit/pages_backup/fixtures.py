import pandas as pd
from functions.fixtures import *

def render_fixtures(df):

    df["match_datetime"] = pd.to_datetime(df["match_datetime"])

    # ---------------------------
    # BUILD EVENTS 
    # ---------------------------
    events = [build_event(row) for row in df.to_dict("records")]

    state= calendar_function(events)

    click_event_and_info(state)

    table_groups()