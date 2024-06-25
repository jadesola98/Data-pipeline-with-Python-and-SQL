## Import required dependencies
import os
import logging 
import requests 
import psycopg2
import pandas as pd 
from dotenv import load_dotenv
from requests.exceptions import RequestException

## Load environmental variables
load_dotenv()

API_KEY         =   os.getenv("API_KEY")
API_HOST        =   os.getenv("API_HOST")
LEAGUE_ID       =	os.getenv("LEAGUE_ID")
SEASON			=	os.getenv("SEASON")

##Define API endpoints, headers and query parameters
url = "https://api-football-v1.p.rapidapi.com/v3/standings"
querystring = {"season":SEASON, "league":LEAGUE_ID}
headers = {
	"x-rapidapi-key": API_KEY,
	"x-rapidapi-host": API_HOST
}


api_response = requests.get(url, headers=headers, params=querystring)
#print(api_response.json())

standings_data = api_response.json()['response']
#print(standings_data)
#print(standings_data[0]['league']['standings'][0])


lst = []
for info in standings_data[0]['league']['standings'][0]:
    lst.append(info)
print(len(lst))
