import streamlit as st
import pandas as pd
from st_clickable_images import clickable_images

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
        st.subheader("🌍 Competing Teams")

        st.info("Select a team by tapping its badge.")

        # 🔹 Create responsive grid layout
        cols = st.columns(4)

        # 🔹 Render one card per team
        for i, row in enumerate(df.to_dict("records")):
            with cols[i % 4]:
                with st.container(border=True):
                    
                        
                    st.markdown(
                    """
                    <style>
                    .team-card {
                        text-align: center;
                        padding: 2px;
                    }
                    .team-name {
                        text-align: center;
                        font-weight: 600;
                        margin-top: 3px;
                        color: white;
                        font-size: 20px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            
                clicked = clickable_images(
                        [row["team_photo"]],
                        titles=[f"View {row['Squad']}"],
                        div_style={
                            "display": "flex",
                            "justify-content": "center",
                        },
                        img_style={
                            "width": "140px",
                            "border-radius": "12px",
                            "padding": "12px",
                            "background-color": "#2e2e2e",
                            "box-shadow": "0 2px 8px rgba(0,0,0,0.25)",
                            "transition": "all 0.2s ease-in-out",
                        },
                    )

                st.markdown(
                        f"""
                        <div class="team-card">
                            <div class="team-name">{row['Squad'].upper()}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if clicked > -1:
                st.session_state.selected_team = row["team"]
                st.session_state.page = "team_detail"
                st.rerun()

    except Exception as e:
        raise RuntimeError( f"Failed to render teams grid: {e}")