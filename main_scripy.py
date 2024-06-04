import os
import logging 
import requests 
import psycopg2
import pandas as pd 
from dotenv import load_dotenv
from requests.exceptions import RequestException


import requests

load_dotenv()

API_KEY         =   os.getenv("API_KEY")
API_HOST        =   os.getenv("API_HOST")

url = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring = {"season":"2020", "league":"39"}

headers = {
	"x-rapidapi-key": API_KEY,
	"x-rapidapi-host": API_HOST
}

api_response = requests.get(url, headers=headers, params=querystring)

#print(response.json())

standings_data = api_response.json()['response']
#print(standings_data[0]['league']['standings'][0])

lst = []
for info in standings_data[0]['league']['standings'][0]:
    lst.append(info)
print(len(lst))

