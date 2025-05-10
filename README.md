# 🏆 Premier League Stats Scraper to Google Sheets

This Python project scrapes comprehensive Premier League statistics from [FBref](https://fbref.com/en/comps/9/Premier-League-Stats) and exports them directly into a Google Sheets spreadsheet. The script is fully automated and designed for easy re-use and modification.

---

## 📄 Overview

* **Language**: Python
* **Libraries**: `pandas`, `BeautifulSoup`, `gspread`, `gspread_dataframe`, `google-auth`, `dotenv`, `logging`
* **Source**: [fbref.com](https://fbref.com/en/comps/9/Premier-League-Stats)
* **Output**: Google Sheets spreadsheet titled `"2024/2025 Premier League Statistics"`
* **Each worksheet**: Named after the `<caption>` tag of each HTML table on the page

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
```

### 3. Set Up Google Sheets API

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a new project and enable the **Google Sheets API**
* Create a **Service Account**
* Generate a JSON key file and name it `GOOGLE_SHEETS_CREDS.json`
* Share the spreadsheet with the **Service Account email**

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: `requirements.txt` should include:
>
> ```text
> pandas
> beautifulsoup4
> gspread
> gspread_dataframe
> google-auth
> python-dotenv
> ```

### 5. Run the Script

```bash
python main.py
```

---

## 🔧 How It Works

1. **Scraping**: Downloads all `<table>` elements from FBref’s Premier League stats page.
2. **Parsing**: Uses `pandas.read_html` and `BeautifulSoup` to convert tables to DataFrames.
3. **Cleanup**: Automatically collapses multi-index headers and adds a `Last Updated` timestamp.
4. **Google Sheets Integration**:

   * Renames the workbook to `"2024/2025 Premier League Statistics"`
   * Clears all previous worksheets except the first
   * Each table is written into a separate worksheet named from its `<caption>` tag

---

## ⚠️ Known Limitations

* **Ambiguous column names**: Some tables have unclear or duplicate column headers due to the HTML structure. The collapsed multi-index columns may result in confusing names that are difficult to interpret.
* **High volume of variables**: The scraped data includes hundreds of columns across multiple tables, making it impractical to perform thorough column renaming or validation within the script.
* **Lack of preprocessing**: No preprocessing (e.g., data cleaning, formatting, filtering) is performed due to the wide variety and volume of data types across tables.
* **Sheet title length**: Google Sheets limits worksheet titles to 100 characters; long captions may cause errors.
* **HTML Structure Changes**: Any changes to FBref’s HTML layout may break the scraping logic.
* **No change tracking or historical backups**: The script overwrites the existing data without keeping previous versions.

---

## 📈 Future Improvements

* **Standardize column names**: Build a post-processing module that maps ambiguous or duplicate column headers to cleaner, consistent names using a dictionary or heuristic approach.
* **Add preprocessing logic**: Implement optional filters, type checks, or cleaning routines for numerical columns to support downstream analytics.
* **Handle large data gracefully**: Add pagination, table filtering, or batching to manage high-volume exports more efficiently.
* **Add version control**: Store historical snapshots of each table in new sheets or backup files to enable comparisons over time.
* **Improve sheet title handling**: Automatically shorten long sheet names while preserving context, to avoid Google Sheets errors.

---

## ✅ Output Example

```
✅ Premier League Data successfully written to Google Sheets ⚽
📄 https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE
```

---

## ✍ Author
**Chidimma Ijoma**
- [GitHub](https://github.com/chidi-ijoma)
- [Email](mailto:nevusijoma@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/chidimma-ijoma/)