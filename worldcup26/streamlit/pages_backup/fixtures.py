import pandas as pd
from functions.fixtures import *
import streamlit.components.v1 as components

def render_fixtures(df: pd.DataFrame) -> None:
    """
    Render the full fixtures page with calendar and standings.

    This function orchestrates the fixtures view, including:
    - Datetime normalization
    - Event building for calendar visualization
    - Interactive calendar rendering
    - Match click details panel
    - Tournament group standings section

    Args:
        df (pd.DataFrame): Fixtures dataset containing match information,
            including teams, scores, and datetime.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If rendering pipeline fails.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_columns = ["match_datetime"]

    # 🔹 Validate required columns
    missing_columns = [ col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    try:

        # =========================
        # DATETIME NORMALIZATION
        # =========================
        df = df.copy()
        df["match_datetime"] = pd.to_datetime(df["match_datetime"])
        df["homeScore"] = pd.to_numeric(df["homeScore"], errors="coerce")
        df["awayScore"] = pd.to_numeric(df["awayScore"], errors="coerce")

        # =========================
        # BUILD CALENDAR EVENTS
        # =========================
        events = df.apply(build_event, axis=1).tolist()

        # =========================
        # CALENDAR RENDERING
        # =========================
        state = calendar_function(events)

        # =========================
        # EVENT CLICK HANDLING
        # =========================
        click_event_and_info(state)

        # =========================
        # STANDINGS SECTION
        # =========================
        option = st.segmented_control('\n\n', 
                           ['🥇 Table groups', '⚔️ Final Stages','⭐ Team of the round'], default= '⚔️ Final Stages')
   
        if option == "🥇 Table groups":
            st.badge("✅ Group stage completed", color="green")
            table_groups()

        elif option == "⚔️ Final Stages":

            df_final_playoffs = prepare_playoffs_wc26()  
        
            fig = create_plot_playoffs(df_final_playoffs)
            #st.info("Knockout stage pairings are provisional and will be finalized once all group standings are confirmed.")

            st.pyplot(fig, use_container_width=True)
        
        elif option == "⭐ Team of the round":
            df_team_of_the_round = create_team_of_the_week_wc26()  
            # Available rounds
            rounds_available = sorted( df_team_of_the_round["round_name"].dropna().unique())

            selected_round = st.selectbox("Select round", rounds_available)

            # Filter selected round
            df_round = df_team_of_the_round[df_team_of_the_round["round_name"] == selected_round].copy()


            
            titulo_team_of_week(selected_round)
            st.write(' ')
            st.write(' ')
            html = team_of_the_week_plot(df_round)
            
            components.html(  html,  height=520,scrolling=False)

    except Exception as e:
        raise RuntimeError(f"Failed to render fixtures page: {e}")