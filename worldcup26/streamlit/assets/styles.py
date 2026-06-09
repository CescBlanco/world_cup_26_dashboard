import streamlit as st

def apply_styles():

    st.markdown("""
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
    """, unsafe_allow_html=True)

def calendar_styles():
    # ---------------------------
    # CSS (mejor separado)
    # ---------------------------
    CALENDAR_CSS = """
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

    st.markdown(CALENDAR_CSS, unsafe_allow_html=True)