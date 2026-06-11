import streamlit as st

def apply_styles() -> None:
    """
    Apply custom global styles to the Streamlit application.

    This function injects CSS into the application to customize
    the overall appearance, including background colors, text
    styling, card layouts, and button behavior.

    Returns:
        None

    Raises:
        RuntimeError: If the custom styles cannot be rendered.
    """

    try:
        # 🔹 Apply global application styles
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"]{
                background-color: #0E1117;
            }

            h1, h2, h3, p {
                color: white;
            }

            .card {
                background: #161B22;
                padding: 12px;
                border-radius: 12px;
            }

            .stButton > button {
                width: 100%;
                background: #00E5FF;
                color: black;
                font-weight: 700;
                border-radius: 10px;
            }

            .stButton > button:hover {
                background: #00bcd4;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True )

    except Exception as e:
        raise RuntimeError(f"Failed to apply application styles: {e}")

def calendar_styles() -> None:
    """
    Apply custom styles to the calendar component.

    This function injects CSS rules that modify the appearance
    of calendar events, including font sizes, spacing, border
    radius, and event time formatting.

    Returns:
        None

    Raises:
        RuntimeError: If the calendar styles cannot be rendered.
    """

    # 🔹 Define custom calendar styles
    calendar_css = """
    <style>
    .fc-event {
        font-size: 7px !important;
        padding: 1px 3px !important;
        line-height: 1.1 !important;
        border-radius: 4px !important;
    }

    .fc-event-title {
        font-size: 7px !important;
        font-weight: 400 !important;
    }

    .fc-daygrid-event {
        font-size: 7px !important;
    }

    .fc-event-time {
        font-size: 7px !important;
        opacity: 0.8;
    }
    </style>
    """

    try:
        # 🔹 Inject calendar-specific CSS
        st.markdown( calendar_css, unsafe_allow_html=True)

    except Exception as e:
        raise RuntimeError(f"Failed to apply calendar styles: {e}")