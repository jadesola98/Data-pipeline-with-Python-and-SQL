"""
Premier League standings pipeline.

Extracts league standings from API-Football (via RapidAPI), flattens the JSON
response into a table with pandas, loads it into PostgreSQL, and creates a
ranked view on top of it.

Configuration is read from environment variables (see .env.example).
"""

import os
import logging

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout, RequestException
from sqlalchemy import create_engine, Integer, String, text


## Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "5432"))


## Pipeline settings
API_URL = "https://api-football-v1.p.rapidapi.com/v3/standings"
SEASON = 2020
LEAGUE_ID = 39  # Premier League
TABLE_NAME = "premier_league_standings"
VIEW_NAME = "premier_league_standings_vw"


## Set up logging: every message goes once to the console and once to standings.log
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.FileHandler("standings.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


## Column types for the PostgreSQL table
DTYPES = {
    "rank": Integer,
    "team": String,
    "games_played": Integer,
    "wins": Integer,
    "draws": Integer,
    "losses": Integer,
    "goals_for": Integer,
    "goals_against": Integer,
    "goal_difference": Integer,
    "points": Integer,
}


## Ranked view, using the Premier League's tie-breakers:
## points, then goal difference, then goals scored
RANKED_VIEW_SQL = f"""
CREATE OR REPLACE VIEW {VIEW_NAME} AS
SELECT
    RANK() OVER (ORDER BY points DESC, goal_difference DESC, goals_for DESC) AS position,
    team,
    games_played,
    wins,
    draws,
    losses,
    goals_for,
    goals_against,
    goal_difference,
    points
FROM {TABLE_NAME};
"""


def extract():
    """Call the API and return the list of team standings for one league season."""
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST,
    }
    params = {"season": SEASON, "league": LEAGUE_ID}

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()

    except HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise SystemExit(1)

    except Timeout:
        logger.error("Request timed out after 20 seconds")
        raise SystemExit(1)

    except RequestException as request_err:
        logger.error(f"Request error occurred: {request_err}")
        raise SystemExit(1)

    payload = response.json().get("response", [])
    if not payload:
        logger.error("API returned no standings data - check the season, league ID and API key")
        raise SystemExit(1)

    standings_data = payload[0]["league"]["standings"][0]
    logger.info(f"Extracted standings for {len(standings_data)} teams (season {SEASON})")
    return standings_data


def transform(standings_data):
    """Flatten the nested JSON for each team into one row of a DataFrame."""
    rows = []
    for team_details in standings_data:
        rows.append([
            team_details["rank"],
            team_details["team"]["name"],
            team_details["all"]["played"],
            team_details["all"]["win"],
            team_details["all"]["draw"],
            team_details["all"]["lose"],
            team_details["all"]["goals"]["for"],
            team_details["all"]["goals"]["against"],
            team_details["goalsDiff"],
            team_details["points"],
        ])

    df = pd.DataFrame(rows, columns=list(DTYPES.keys()))
    logger.info(f"Transformed {len(df)} rows")
    return df


def load(df, engine):
    """Write the DataFrame to PostgreSQL and rebuild the ranked view.

    Everything runs in one transaction, so if any step fails, nothing is
    half-written. The view is dropped first because PostgreSQL will not
    drop a table that a view depends on.
    """
    try:
        with engine.begin() as connection:
            connection.execute(text(f"DROP VIEW IF EXISTS {VIEW_NAME};"))
            df.to_sql(TABLE_NAME, connection, if_exists="replace", index=False, dtype=DTYPES)
            connection.execute(text(RANKED_VIEW_SQL))
        logger.info(f"Loaded {len(df)} rows into {TABLE_NAME} and rebuilt {VIEW_NAME} in {DB_NAME}")

    except Exception as e:
        logger.error(f"Error loading data into {DB_NAME}: {e}")
        raise SystemExit(1)


def main():
    standings_data = extract()
    df = transform(standings_data)

    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)

    load(df, engine)

    ## Show the final ranked table
    view_df = pd.read_sql(f"SELECT * FROM {VIEW_NAME} ORDER BY position", engine)
    print(view_df.to_string(index=False))


if __name__ == "__main__":
    main()
