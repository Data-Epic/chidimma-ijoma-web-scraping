import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import logging
from io import StringIO

# Set up logging configuration
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


# Set up Google Sheets credentials
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("GOOGLE_SHEETS_CREDS.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1cLKSFOBpPct27Ttgk0hbb6Rt5uLRJ1r1v5FC_CD3WPM"  # Replace with your Google Sheet ID

# Open your sheet
sheet = client.open_by_key(sheet_id)
worksheet = sheet.worksheet("Sheet1")

# Define the URL of the website to scrape
url = "https://fbref.com/en/comps/9/Premier-League-Stats"

# Send a GET request to the website
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "lxml")

league_table = soup.find("table", {"id": "results2024-202591_overall"})
if league_table is None:
    logging.error("League table not found on the page.")
    raise Exception("League table not found on the page.")

try:
    df = pd.read_html(StringIO(str(league_table)))[0]
except ValueError as e:
    logging.error(f"Error reading HTML table: {e}")
    raise Exception(f"Error reading HTML table: {e}")
print(df)