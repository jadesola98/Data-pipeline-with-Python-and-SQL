## Import required packages
import os
import logging 
import requests 
import psycopg2
import pandas as pd 
from dotenv import load_dotenv
from requests.exceptions import RequestException
from sqlalchemy import create_engine, Integer, String

## Load environment variables
load_dotenv()

API_KEY         =   os.getenv("API_KEY")
API_HOST        =   os.getenv("API_HOST")
DB_NAME         =   os.getenv("DB_NAME")
DB_USER         =   os.getenv("DB_USER")
DB_PASS         =   os.getenv("DB_PASS")
DB_HOST         =   os.getenv("DB_HOST")
DB_PORT         =   int(os.getenv("DB_PORT"))


## Set up logger
logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

## Set up file and console handlers
file_handler = logging.FileHandler('standings.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


##Define API endpoints, headers and query parameters
url = "https://api-football-v1.p.rapidapi.com/v3/standings"
querystring = {"season":2020, "league":39}
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

## Send the API request with exception handling
try:
    api_response = requests.get(url, headers=headers, params=querystring, timeout=20)
    api_response.raise_for_status() 


except HTTPError as http_err:
    logger.error(f'HTTP error occurred: {http_err}')


except Timeout:
    logger.error('Request timed out after 20 seconds')


except RequestException as request_err:
    logger.error(f'Request error occurred: {request_err}')


## Parse the API response
standings = api_response.json()['response']

## Extract the data from the JSON response
standings_data = standings[0]['league']['standings'][0]


## Flatten the data
data = []

for team_details in standings_data:
    rank            =   team_details['rank']
    name            =   team_details['team']['name']
    played          =   team_details['all']['played']
    win             =   team_details['all']['win']
    draw            =   team_details['all']['draw']
    lose            =   team_details['all']['lose']
    goals_for       =   team_details['all']['goals']['for']
    goals_against   =   team_details['all']['goals']['against']
    goals_diff      =   team_details['goalsDiff']
    points          =   team_details['points']
    
    data.append([rank,name,played,win,draw,lose,goals_for,goals_against,goals_diff,points])

## Convert data into a dataframe
df = pd.DataFrame(data, columns=['rank','team','games_played','wins','draws','losses','goals_for','goals_against','goal_difference','points'])
print(df)


# Create the database connection string
connection_string = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create the sqlalchemy engine
engine = create_engine(connection_string)

# Name of the table to write to
table_name = 'premier_league_standings'

# Define data type of table columns
dtype = {
    'rank': Integer,
    'team': String,
    'games_played': Integer,
    'wins': Integer,
    'draws': Integer,
    'losses': Integer,
    'goals_for': Integer,
    'goals_against': Integer,
    'goal_difference': Integer,
    'points': Integer
}

# Write DataFrame to PostgreSQL table
try:
    df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype)
    logger.info(f'DataFrame written to {table_name} table in {DB_NAME} database')

except Exception as e:
    logger.error(f'Error writing DataFrame to {table_name} table in {DB_NAME} database: {e}')



# view newly created table
table_query = f'SELECT * FROM {table_name}'
table_df = pd.read_sql(table_query, engine)
print(table_df)


# SQL command to create a view
ranked_standings_view_query = """
CREATE OR REPLACE VIEW premier_league_standings_vw AS 
SELECT 
    RANK() OVER (ORDER BY wins DESC, draws DESC, losses ASC) AS position,
    team,
    games_played,
    wins,
    draws,
    losses,
    points
FROM 
    premier_league_standings;

"""


try:
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text(ranked_standings_view_query))
    logger.info(f'view successfully created')

except Exception as e:
    logger.error(f'Error creating view: {e}')


# view newly created view
view_query = f'SELECT * FROM premier_league_standings_vw'
view_df = pd.read_sql(view_query, engine)
print(view_df)


