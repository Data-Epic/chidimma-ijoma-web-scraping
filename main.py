import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import logging
from io import StringIO
from datetime import datetime

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# ---------------------- Google Sheets Setup ------------------------
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("GOOGLE_SHEETS_CREDS.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = "1cLKSFOBpPct27Ttgk0hbb6Rt5uLRJ1r1v5FC_CD3WPM"
    sheet = client.open_by_key(sheet_id)
    sheet.update_title("2024/2025 Premier League Statistics")

    # Rename or create worksheet
    try:
        worksheet = sheet.worksheet("Overview")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Overview", rows="100", cols="20")
    else:
        worksheet.clear()
except Exception as e:
    logging.error(f"Failed to set up Google Sheets: {e}")
    raise Exception("Google Sheets setup failed. Check credentials and permissions.")

# ---------------------- Web Scraping ------------------------
url = "https://fbref.com/en/comps/9/Premier-League-Stats"

try:
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "lxml")
    league_table = soup.find("table", {"id": "results2024-202591_overall"})

    if league_table is None:
        raise ValueError("League table not found in the HTML.")

    df = pd.read_html(StringIO(str(league_table)))[0]
except Exception as e:
    logging.error(f"Failed to scrape or parse league table: {e}")
    raise Exception("Scraping failed. Check if the table ID or URL has changed.")

# ---------------------- Data Cleaning & Transformation ------------------------
rename_map = {
    "Rk": "Rank",
    "Squad": "Team",
    "W": "Wins",
    "D": "Draws",
    "L": "Losses",
    "GF": "Goals For",
    "GA": "Goals Against",
    "GD": "Goal Difference",
    "Pts": "Points",
    "Pts/MP": "Points Per Match",
    "xG": "Expected Goals",
    "xGA": "Expected Goals Against",
    "xGD": "Expected Goal Difference",
    "xGD/90": "Expected Goal Difference Per 90mins",
    "Last 5": "Last 5 Match Results",
}

df.rename(columns=rename_map, inplace=True)

# Split 'Top Team Scorer' into two columns
if "Top Team Scorer" in df.columns:
    split_cols = df["Top Team Scorer"].str.split(" - ", n=1, expand=True)
    df["Top Scorer"] = split_cols[0].str.strip()
    df["Top Scorer Goals"] = split_cols[1].str.strip() if split_cols.shape[1] > 1 else None

# Drop irrelevant columns
columns_to_drop = [col for col in ["Notes", "Top Team Scorer"] if col in df.columns]
if columns_to_drop:
    df.drop(columns=columns_to_drop, inplace=True)

# Add timestamp
df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------------- Export to Google Sheets ------------------------
try:
    set_with_dataframe(worksheet, df)
    logging.info("Data successfully written to Google Sheets.")
except Exception as e:
    logging.error(f"Failed to write data to Google Sheets: {e}")
    raise Exception("Data upload failed. Check worksheet access or format issues.")

# ---------------------- Final Output ------------------------
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
print(f"✅ Premier League Data successfully written to Google Sheets ⚽\n📄 {sheet_url}")