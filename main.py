import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import logging
from io import StringIO
from datetime import datetime
import os
from dotenv import load_dotenv


class FbrefScraperPipeline:
    """
    A pipeline for scraping Premier League statistics from FBref and exporting the data
    into a Google Sheets workbook.

    Attributes:
        sheet_id (str): The ID of the target Google Sheets workbook.
        creds_file (str): Path to the service account credentials JSON file.
        sheet (gspread.Spreadsheet): The authenticated spreadsheet instance.
        column_rename_map (dict): Mapping of visible column headers to aria-label values.
    """

    def __init__(self, sheet_id, creds_file):
        """
        Initializes the FbrefScraperPipeline with Google Sheets details.

        Args:
            sheet_id (str): The ID of the Google Sheets document.
            creds_file (str): Path to the JSON credentials file for Google Sheets API.
        """
        self.sheet_id = sheet_id
        self.creds_file = creds_file
        self.sheet = None
        self.column_rename_map = {}
        self._configure_logging()

    def _configure_logging(self):
        """
        Configures the logging settings for the pipeline.

        Returns:
            None
        """
        logging.basicConfig(filename='history.log', level=logging.INFO,
                            format='%(asctime)s: %(levelname)s: %(message)s')

    def run(self, url):
        """
        Executes the scraping and export process.

        Args:
            url (str): The FBref page URL to scrape data from.

        Returns:
            None
        """
        self._setup_google_sheets()
        tables = self._scrape_page(url)
        for table in tables:
            self._process_and_export_table(table)
        self._final_output()

    def _setup_google_sheets(self):
        """
        Sets up and authenticates the connection to Google Sheets. Clears the first worksheet
        and deletes all others.

        Returns:
            None
        """
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(self.creds_file, scopes=scopes)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(self.sheet_id)
            self.sheet.update_title("2024/2025 Premier League Statistics")

            worksheets = self.sheet.worksheets()
            for i, worksheet in enumerate(worksheets):
                if i != 0:
                    self.sheet.del_worksheet(worksheet)
            self.sheet.get_worksheet(0).clear()

        except Exception as e:
            logging.error(f"Failed to set up Google Sheets: {e}")
            raise

    def _scrape_page(self, url):
        """
        Scrapes HTML tables and column metadata from FBref.

        Args:
            url (str): URL of the stats page to scrape.

        Returns:
            list: List of <table> elements parsed by BeautifulSoup.
        """
        try:
            page = urlopen(url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "lxml")
            tables = soup.find_all("table")
            columns = soup.find_all("th", {"scope": "col", "aria-label": True})

            for col in columns:
                text = col.text.strip()
                aria_label = col["aria-label"].strip()
                self.column_rename_map[text] = aria_label

            return tables
        except Exception as e:
            logging.error(f"Failed to scrape or parse page: {e}")
            raise

    def _flatten_columns(self, df):
        """
        Flattens multi-index columns and removes unnamed levels.

        Args:
            df (pd.DataFrame): DataFrame potentially containing multi-index columns.

        Returns:
            pd.DataFrame: DataFrame with single-level flattened columns.
        """
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                ' '.join([lvl if not str(lvl).startswith('Unnamed') else '' for lvl in col]).strip()
                for col in df.columns.values
            ]
        return df

    def _remove_duplicate_words(self, name):
        """
        Removes duplicate words from a string while maintaining order.

        Args:
            name (str): A string representing a column name.

        Returns:
            str: Cleaned string with duplicates removed.
        """
        seen = set()
        words = []
        for word in name.split():
            if word in seen:
                continue
            seen.add(word)
            words.append(word)
        return ' '.join(words)

    def _clean_columns(self, df):
        """
        Cleans and standardizes column names: applies aria-label renaming,
        flattens multi-index columns, drops expected metrics, and removes duplicates.

        Args:
            df (pd.DataFrame): DataFrame to clean.

        Returns:
            pd.DataFrame: Cleaned DataFrame ready for export.
        """
        df.rename(columns=self.column_rename_map, inplace=True)
        df = self._flatten_columns(df)

        cols_to_drop = df.columns[df.columns.str.contains('xG|xA|Expectation|Expected')]
        df.drop(cols_to_drop, axis=1, inplace=True)

        df.columns = [self._remove_duplicate_words(col) for col in df.columns]
        return df

    def _process_and_export_table(self, table):
        """
        Converts an HTML table to DataFrame, cleans it, and uploads it to Google Sheets.

        Args:
            table (bs4.element.Tag): A <table> HTML element from FBref.

        Returns:
            None
        """
        try:
            caption = table.find("caption")
            tag = table.get("id", "NoID")
            table_id = (caption.get_text(strip=True) if caption else "") + "_" + tag
            sheet_title = table_id[:100] if table_id else "Unnamed_Table"

            df = pd.read_html(StringIO(str(table)))[0]
            df = self._clean_columns(df)

            try:
                worksheet = self.sheet.worksheet(sheet_title)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(title=sheet_title, rows="100", cols="20")
            else:
                worksheet.clear()

            df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            set_with_dataframe(worksheet, df)
            logging.info(f"Table '{sheet_title}' successfully written to Google Sheets.")

        except Exception as e:
            logging.error(f"Failed to process table: {e}")

    def _final_output(self):
        """
        Prints and logs the URL of the exported Google Sheets document.

        Returns:
            None
        """
        sheet_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
        print(f"✅ Premier League Data successfully written to Google Sheets ⚽\n📄 {sheet_url}")

# ---------------------- Command to Run the Pipeline ----------------------
if __name__ == "__main__":
    load_dotenv()
    creds_path = "GOOGLE_SHEETS_CREDS.json"  # Replace with your actual credentials file
    sheet_id = os.getenv("SHEET_ID")  # Or hardcode the ID here
    target_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    pipeline = FbrefScraperPipeline(sheet_id=sheet_id, creds_file=creds_path)
    pipeline.run(target_url)
