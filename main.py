import pandas as pd
from bs4 import BeautifulSoup
import requests
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

# Set up Google Sheets credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("GOOGLE_SHEETS_CREDS.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1cLKSFOBpPct27Ttgk0hbb6Rt5uLRJ1r1v5FC_CD3WPM"  # Replace with your Google Sheet ID

# Open your sheet
sheet = client.open_by_key(sheet_id)
worksheet = sheet.worksheet("Sheet1")

