import streamlit as st
import pandas as pd

def render_teams(df: pd.DataFrame) -> None:
    """
    Render the participating teams grid.

    This function displays all participating teams in a responsive
    four-column layout. Each team card includes the team image,
    team name, and a button that navigates to the team detail page.

    Args:
        df (pd.DataFrame): Dataset containing participating teams.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        KeyError: If required columns are missing.
        RuntimeError: If the teams grid cannot be rendered.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_columns = ["team","Squad","team_photo"]

    # 🔹 Validate required columns
    missing_columns = [ col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    try:
        # 🔹 Render section title
        st.subheader("🌍 Participating Teams")

        # 🔹 Create responsive grid layout
        cols = st.columns(4)

        # 🔹 Render one card per team
        for i, row in enumerate(df.to_dict("records")):

            with cols[i % 4]:

                st.markdown(
                    f"""
                    <div style="
                        border-radius: 12px;
                        padding: 13px;
                        background: #2e2e2e;
                        text-align: center;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
                        margin-bottom: 10px;
                    ">
                        <img src="{row['team_photo']}"
                             style="width:85px; border-radius:8px;"><br>
                        <h4 style="margin:8px 0 0 0; color:white;">
                            {row['Squad']}
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 🔹 Navigate to the selected team page
                if st.button( "View Team →", key=f"team_{row['team']}_{i}"):
                    st.session_state.selected_team = row["team"]
                    st.session_state.page = "team_detail"
                    st.rerun()

    except Exception as e:
        raise RuntimeError( f"Failed to render teams grid: {e}")