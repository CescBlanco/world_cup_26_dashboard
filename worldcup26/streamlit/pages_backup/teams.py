import streamlit as st

def render_teams(df):

    st.subheader("Participating Teams")

    cols = st.columns(4)

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
                    <img src="{row['team_photo']}" style="width:85px; border-radius:8px;"><br>
                    <h4 style="margin:8px 0 0 0; color:white;">
                        {row['Squad']}
                    </h4>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "View Team →",
                key=f"team_{row['team']}_{i}"
            ):
                st.session_state.selected_team = row["team"]
                st.session_state.page = "team_detail"
                st.rerun()