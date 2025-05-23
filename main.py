import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import logging
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv
import os

# ---------------------- Initial Message ----------------------
"""
This script scrapes the Premier League statistics from fbref.com and exports them to Google Sheets.
The script uses the Google Sheets API to create a new spreadsheet and write the scraped data into it.
In order to run this script, you need to have the following:
1. A .env file where you will place your Google Sheets Workbook ID
2. A Google Cloud project with the Google Sheets API enabled
3. A service account with the necessary permissions to access the Google Sheets API
"""

# ---------------------- Load Environment Variables ----------------------
load_dotenv()
sheet_id = os.getenv("SHEET_ID")


# ---------------------- Logging Configuration ----------------------
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# ---------------------- Google Sheets Setup ------------------------
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("GOOGLE_SHEETS_CREDS.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    sheet.update_title("2024/2025 Premier League Statistics")
except Exception as e:
    logging.error(f"Failed to set up Google Sheets: {e}")
    raise Exception("Google Sheets setup failed. Check credentials and permissions.")

# Delete all worksheets from the spreadsheet
worksheets = sheet.worksheets()

for i, worksheet in enumerate(worksheets):
    if i != 0:  # Keep the first worksheet only
        sheet.del_worksheet(worksheet)

sheet.get_worksheet(0).clear() # Clear the first worksheet

# ---------------------- Web Scraping ------------------------
url = "https://fbref.com/en/comps/9/Premier-League-Stats"

try:
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
except Exception as e:
    logging.error(f"Failed to scrape or parse page: {e}")
    raise Exception("Scraping failed. Check if the URL is correct and accessible.")

# ---------------------- Export Each Table to Google Sheets ------------------------
for table in tables:
    try:
        caption = table.find("caption").get_text(strip=True)
        tag = table["id"]
        table_id = str(caption + "_" + tag)
        sheet_title = table_id if table_id else "Unnamed_Table"

        df = pd.read_html(StringIO(str(table)))[0]

        # Collapse multi-index columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]
        

        # Create or update worksheet
        try:
            worksheet = sheet.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=sheet_title, rows="100", cols="20")
        else:
            worksheet.clear()

        # Add timestamp
        df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Export DataFrame to sheet
        set_with_dataframe(worksheet, df)
        logging.info(f"Table '{sheet_title}' successfully written to Google Sheets.")

    except Exception as e:
        logging.error(f"Failed to process table '{sheet_title}': {e}")
        continue

# ---------------------- Final Output ------------------------
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
print(f"✅ Premier League Data successfully written to Google Sheets ⚽\n📄 {sheet_url}")