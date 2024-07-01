## Import required dependencies

import os
import psycopg2
import pandas as pd 
from PIL import Image
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, String


# load environment variables
load_dotenv()

API_KEY         =   os.getenv("API_KEY")
API_HOST        =   os.getenv("API_HOST")
DB_NAME         =   os.getenv("DB_NAME")
DB_USER         =   os.getenv("DB_USER")
DB_PASS         =   os.getenv("DB_PASS")
DB_HOST         =   os.getenv("DB_HOST")
DB_PORT         =   int(os.getenv("DB_PORT"))


# Create the database connection string
connection_string = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create the sqlalchemy engine
engine = create_engine(connection_string)

# Query to view the newly created table
query = f'SELECT * FROM public.premier_league_standings_vw'
# Execute the query and store the result in a DataFrame for easy viewing
premier_league_standings = pd.read_sql(query, engine)

# Set the page configuration of the app
st.set_page_config(
    page_title   =  "Premier League Standings 2023/24",
    page_icon    =  "⚽",
    layout       =  "wide"
)

# Read image into app
prem_league_logo_filepath  =  "premier_league_logo.png"
prem_league_logo_image     =  Image.open(prem_league_logo_filepath)


# Create columns for the layout and display the image through the 2nd one
col1, col2 = st.columns([4, 1])
col2.image(prem_league_logo_image)


st.title("🏆Premier League Table Standings 2020/21🏆")
st.write("The app showcases the current Premier League standings for the 2020/21 season in the table below.")

# Display instructions
show_visualization = st.sidebar.radio('Would you like to view the standings as a visualization too?', ('No', 'Yes'))
fig_specification  = px.bar(premier_league_standings, 
                        x           =   'team', 
                        y           =   'points', 
                        title       =   'Premier League Standings 2020/21', 
                        labels      =   {'points':'Points', 'team':'Team', 'wins': 'Wins', 'losses': 'Losses'},
                        color       =   'team',
                        height      =   600,
                        hover_data  =   ['wins', 'losses']
)

if show_visualization == 'Yes':
    st.table(premier_league_standings)
    st.write("")
    fig = fig_specification 
    st.plotly_chart(fig, use_container_width=True)
else:
    st.table(premier_league_standings)