"""
Streamlit app that displays the Premier League standings loaded by main_script.py.

Run with:  streamlit run app.py
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine


## Page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Premier League Standings 2020/21",
    page_icon="⚽",
    layout="wide",
)


## Load environment variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

VIEW_NAME = "premier_league_standings_vw"


@st.cache_data(ttl=600)
def load_standings():
    """Read the ranked view from PostgreSQL. Cached for 10 minutes so the
    database isn't queried again every time someone clicks in the app."""
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    return pd.read_sql(f"SELECT * FROM public.{VIEW_NAME} ORDER BY position", engine)


try:
    standings = load_standings()
except Exception as e:
    st.error(f"Could not load standings from the database. Has main_script.py been run? ({e})")
    st.stop()


st.title("🏆 Premier League Standings 2020/21")
st.write("Final league table for the 2020/21 season, loaded from PostgreSQL by the pipeline in main_script.py.")

st.dataframe(standings, hide_index=True, use_container_width=True)

show_chart = st.sidebar.radio("Show points as a chart?", ("No", "Yes"))

if show_chart == "Yes":
    fig = px.bar(
        standings,
        x="team",
        y="points",
        title="Points by team, 2020/21",
        labels={"points": "Points", "team": "Team", "wins": "Wins", "losses": "Losses"},
        hover_data=["wins", "draws", "losses", "goal_difference"],
        height=600,
    )
    st.plotly_chart(fig)
