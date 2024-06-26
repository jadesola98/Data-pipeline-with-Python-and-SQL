## Import required dependencies
import os
import logging 
import requests 
import psycopg2
import pandas as pd 
from dotenv import load_dotenv
from requests.exceptions import RequestException

## Load environment variables
load_dotenv()

API_KEY         =   os.getenv("API_KEY")
API_HOST        =   os.getenv("API_HOST")


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


try:
    api_response = api_response = requests.get(url, headers=headers, params=querystring, timeout=20)
    api_response.raise_for_status() 


except HTTPError as http_err:
    logger.error(f'HTTP error occurred: {http_err}')


except Timeout:
    logger.error('Request timed out after 20 seconds')


except RequestException as request_err:
    logger.error(f'Request error occurred: {request_err}')

#api_response = requests.get(url, headers=headers, params=querystring)
#print(api_response.json())

standings_data = api_response.json()['response']
#print(standings_data)
#print(standings_data[0]['league']['standings'][0])


'''
lst = []
for info in standings_data[0]['league']['standings'][0]:
    lst.append(info)
print(len(lst))
'''