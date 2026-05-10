# 🏆 Premier League Stats Scraper to Google Sheets

This Python project scrapes comprehensive Premier League statistics from [FBref](https://fbref.com/en/comps/9/Premier-League-Stats) and [football-data.org](https://www.football-data.org/) and exports them directly into a Google Sheets spreadsheet. The script is fully automated and designed for easy re-use at the start of every new Premier League season.

---

## 📄 Overview

* **Language**: Python
* **Libraries**: `pandas`, `soccerdata`, `gspread`, `gspread_dataframe`, `google-auth`, `requests`, `python-dotenv`, `logging`
* **Data Sources**:
  * [fbref.com](https://fbref.com/en/comps/9/Premier-League-Stats) via `soccerdata` — comprehensive team statistics
  * [football-data.org](https://www.football-data.org/) — league standings and match results
* **Output**: Google Sheets spreadsheet titled `"2024/2025 Premier League Comprehensive Statistics"`
* **Worksheets**:
  * 📊 Standings
  * 📅 Match Results
  * 📈 Standard Stats
  * 🎯 Shooting
  * 🧤 Goalkeeping
  * ⏱️ Playing Time
  * 🃏 Misc Stats
  * 🏅 Team Leaders
  * ⚽ Goals and Assists

---

## 📜 Project History

This project started as an internship assignment to scrape Premier League data from FBref and export it to Google Sheets using `BeautifulSoup` and `urllib`. The original approach worked well at the time but became unreliable due to Cloudflare protection introduced on FBref, which blocked all automated requests.

After revisiting the project on a new machine, the original `main.py` script was found to be completely obsolete — FBref's Cloudflare setup blocked every approach attempted, including custom `User-Agent` headers, `cloudscraper`, and `playwright`. The project was therefore rebuilt from the ground up as `main_2.0.py` with a more robust and comprehensive approach:

* `soccerdata` replaced `BeautifulSoup` to handle FBref's Cloudflare protection internally
* `football-data.org` API was introduced for clean, reliable standings and match result data
* Column names were fully standardised and irrelevant columns dropped
* A workbook clearing function was added to ensure clean runs every time

The original `main.py` is preserved in the repository for historical reference only and is no longer functional.

---

## 🗂️ Scripts

| Script | Description |
|---|---|
| `main.py` | Original script from internship project. Used `BeautifulSoup` and `urllib` to scrape FBref directly. Now obsolete due to Cloudflare protection on FBref. Preserved for historical reference. |
| `main_2.0.py` | Current active script. Combines football-data.org API and soccerdata/FBref for comprehensive Premier League statistics. |

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Data-Epic/chidimma-ijoma-web-scraping.git
cd premier-league-scraper
```

### 2. Create a `.env` File

Create a `.env` file in the project root:

```env
SHEET_ID=your_google_sheet_id_here
FOOTBALL_API_KEY=your_football_data_api_key_here
```

### 3. Set Up Google Sheets API

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a new project and enable the **Google Sheets API**
* Create a **Service Account**
* Generate a JSON key file and name it `GOOGLE_SHEETS_CREDS.json`
* Share the spreadsheet with the **Service Account email**

### 4. Get a Football Data API Key

* Go to [football-data.org](https://www.football-data.org/)
* Click **"Get API Key"** and sign up for a free account
* Copy your API key into the `.env` file as shown above

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: `requirements.txt` includes:
>
> ```text
> pandas
> gspread
> google-auth
> gspread-dataframe
> requests
> soccerdata
> python-dotenv
> beautifulsoup4
> lxml
> cloudscraper
> playwright
> ```

### 6. Run the Script

```bash
python main_2.0.py
```

> **Note**: The script takes several minutes to complete due to intentional delays between FBref requests to avoid rate limiting.

---

## 🔧 How It Works

1. **Clears the workbook** — removes all existing worksheets except one, ready for a fresh run
2. **football-data.org API** — fetches Standings and Match Results first so they appear as the first tabs
3. **soccerdata/FBref** — pulls team statistics across 5 categories: Standard, Shooting, Goalkeeping, Playing Time and Misc
4. **Column cleanup** — renames all columns to human-readable names and drops redundant ones
5. **Team Leaders** — pulls player data and finds the top scorer and top assister per team
6. **Goals and Assists** — ranks all players in the league by goals and assists side by side
7. **Timestamps** — every worksheet gets a `Last Updated` column so you always know when the data was refreshed

---

## ⚠️ Known Limitations

* **Cloudflare protection**: FBref uses Cloudflare which blocks standard HTTP requests. `soccerdata` handles this internally using a headless browser but may break if FBref updates their protection in future.
* **Rate limiting**: FBref limits how frequently data can be fetched. The script includes 10-second delays between requests to stay within limits, making it slower to run.
* **football-data.org free tier**: The free API tier only provides standings and match results. Detailed player statistics require a paid plan.
* **No change tracking or historical backups**: The script overwrites existing data on every run without keeping previous versions.
* **API Quotas**: Heavy or frequent use may exceed Google Sheets API quota limits.
* **Season configuration**: The season and league are hardcoded in the script. These need to be manually updated at the start of each new season.

---

## 📈 Future Improvements

* **Automatic season detection**: Automatically detect and update the current Premier League season without manual changes to the script.
* **Historical snapshots**: Store previous runs as timestamped backup sheets to enable season-over-season comparisons.
* **Scheduling**: Set up automated runs using a task scheduler (e.g. Windows Task Scheduler or cron) so the sheet updates itself regularly without manual execution.
* **Dashboard**: Build a summary dashboard sheet with key metrics and charts pulled from the data tabs.
* **Expand stat categories**: Add passing, possession, defensive and goal creation stats if FBref access improves or an alternative data source is found.

---

## ✅ Output Example
✅ 'Standings' written successfully.
✅ 'Match Results' written successfully.
✅ 'Standard Stats' written successfully.
✅ 'Shooting' written successfully.
✅ 'Goalkeeping' written successfully.
✅ 'Playing Time' written successfully.
✅ 'Misc Stats' written successfully.
✅ 'Team Leaders' written successfully.
✅ 'Goals and Assists' written successfully.
✅ Premier League Data successfully written to Google Sheets ⚽
📄 https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE

---

## ✍ Author
**Chidimma Ijoma**
- [GitHub](https://github.com/chidi-ijoma)
- [Email](mailto:nevusijoma@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/chidimma-ijoma/)