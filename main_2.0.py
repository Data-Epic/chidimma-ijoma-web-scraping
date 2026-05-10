import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import logging
from datetime import datetime
from dotenv import load_dotenv
import soccerdata as sd
import requests
import time
import os

# ---------------------- Load Environment Variables ----------------------
load_dotenv()
sheet_id = os.getenv("SHEET_ID")
api_key = os.getenv("FOOTBALL_API_KEY")

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(filename='history_comprehensive.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# ---------------------- Soccerdata Setup ----------------------
fbref = sd.FBref(leagues="ENG-Premier League", seasons="2025-2026")

# ---------------------- Football Data API Setup ----------------------
api_headers = {"X-Auth-Token": api_key}
base_url = "https://api.football-data.org/v4"

# ---------------------- Google Sheets API Setup ----------------------
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("GOOGLE_SHEETS_CREDS.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    sheet.update_title("2025/2026 Premier League Comprehensive Statistics")
except Exception as e:
    logging.error(f"Failed to set up Google Sheets: {e}")
    raise Exception("Google Sheets setup failed. Check credentials and permissions.")

# ---------------------- Helper Functions ----------------------
def get_or_create_worksheet(sheet, title):
    try:
        worksheet = sheet.worksheet(title)
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=title, rows="100", cols="50")
    return worksheet

def clear_workbook(sheet):
    try:
        worksheets = sheet.worksheets()
        for i, worksheet in enumerate(worksheets):
            if i != 0:  # Keep the first worksheet only
                sheet.del_worksheet(worksheet)
        first_sheet = sheet.get_worksheet(0)
        first_sheet.clear()
        first_sheet.update_title("Standings") # Rename it ready for the loop
        logging.info("Workbook cleared successfully.")
    except Exception as e:
        logging.error(f"Failed to clear workbook: {e}")
        raise Exception("Failed to clear workbook. Check permissions.")

def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df

def reset_index_clean(df):
    df = df.reset_index()
    # Keep only 'team' from the index, drop league and season
    cols_to_drop = [c for c in df.columns if c in ['league', 'season']]
    df = df.drop(columns=cols_to_drop)
    return df

def write_to_sheet(sheet, title, df):
    df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet = get_or_create_worksheet(sheet, title)
    set_with_dataframe(worksheet, df)
    logging.info(f"'{title}' successfully written to Google Sheets.")
    print(f"✅ '{title}' written successfully.")

# ---------------------- Clear Workbook ----------------------
clear_workbook(sheet)

# ---------------------- Team Stat Types ----------------------
stat_types = {
    "Standard Stats": "standard",
    "Shooting": "shooting",
    "Keeper": "keeper",
    "Playing Time": "playing_time",
    "Misc Stats": "misc"
}

# ---------------------- Stat Types & Column Configs ----------------------
stat_configs = {
    "Standard Stats": {
        "stat_type": "standard",
        "rename": {
            "team": "Team", "players_used": "Players Used", "Age": "Average Age",
            "Poss": "Possession %", "Playing Time MP": "Matches Played",
            "Playing Time Starts": "Starts", "Playing Time Min": "Minutes Played",
            "Performance Gls": "Goals", "Performance Ast": "Assists",
            "Performance G-PK": "Non-Penalty Goals", "Performance PK": "Penalties Scored",
            "Performance PKatt": "Penalties Attempted", "Performance CrdY": "Yellow Cards",
            "Performance CrdR": "Red Cards", "Per 90 Minutes Gls": "Goals per 90",
            "Per 90 Minutes Ast": "Assists per 90", "Per 90 Minutes G-PK": "Non-Penalty Goals per 90",
            "Per 90 Minutes G+A-PK": "Non-Penalty Goals+Assists per 90"
        },
        "drop": [
            "Playing Time 90s", "Performance G+A", "Per 90 Minutes G+A", "Starts"
        ]
    },
    "Shooting": {
        "stat_type": "shooting",
        "rename": {
            "team": "Team", "players_used": "Players Used","90s": "90s Played",
            "Standard Gls": "Goals", "Standard Sh": "Shots", "Standard SoT": "Shots on Target",
            "Standard SoT%": "Shot Accuracy %", "Standard Sh/90": "Shots per 90",
            "Standard SoT/90": "Shots on Target per 90", "Standard G/Sh": "Goals per Shot",
            "Standard G/SoT": "Goals per Shot on Target", "Standard PK": "Penalties Scored",
            "Standard PKatt": "Penalties Attempted"
        },
        "drop": ["90s Played"]
    },
    "Goalkeeping": {
        "stat_type": "keeper",
        "rename": {
            "team": "Team", "players_used": "Goalkeepers Used",
            "Playing Time MP": "Matches Played", "Playing Time Starts": "Starts",
            "Playing Time Min": "Minutes Played", "Performance GA": "Goals Conceded",
            "Performance GA90": "Goals Conceded per 90", "Performance SoTA": "Shots on Target Faced",
            "Performance Saves": "Saves", "Performance Save%": "Save Percentage",
            "Performance W": "Wins", "Performance D": "Draws", "Performance L": "Losses",
            "Performance CS": "Clean Sheets", "Performance CS%": "Clean Sheet %",
            "Penalty Kicks PKatt": "Penalties Faced", "Penalty Kicks PKA": "Penalties Conceded",
            "Penalty Kicks PKsv": "Penalties Saved", "Penalty Kicks PKm": "Penalties Missed",
            "Penalty Kicks Save%": "Penalty Save %"
        },
        "drop": ["Playing Time 90s", "Wins", "Draws", "Losses", "Starts", "Minutes Played"]
    },
    "Playing Time": {
        "stat_type": "playing_time",
        "rename": {
            "team": "Team", "players_used": "Players Used", "Age": "Average Age",
            "Playing Time MP": "Matches Played", "Playing Time Min": "Minutes Played",
            "Playing Time Mn/MP": "Minutes per Match", "Playing Time Min%": "Minutes Share %",
            "Starts Starts": "Starts", "Starts Mn/Start": "Minutes per Start",
            "Starts Compl": "Full Games Played", "Subs Subs": "Substitute Appearances",
            "Subs Mn/Sub": "Minutes per Sub Appearance", "Subs unSub": "Times Substituted Off",
            "Team Success PPM": "Points per Match", "Team Success onG": "Goals Scored While On Pitch",
            "Team Success onGA": "Goals Conceded While On Pitch",
            "Team Success +/-": "Goal Difference While On Pitch",
            "Team Success +/-90": "Goal Difference per 90"
        },
        "drop": ["Playing Time 90s", "Minutes Share %", "Matches Played",
                 "Minutes Played", "Minutes per Match", "Starts"]
    },
    "Misc Stats": {
        "stat_type": "misc",
        "rename": {
            "team": "Team", "players_used": "Players Used", "90s": "90s Played",
            "Performance CrdY": "Yellow Cards", "Performance CrdR": "Red Cards",
            "Performance 2CrdY": "Second Yellow Cards", "Performance Fls": "Fouls Committed",
            "Performance Fld": "Fouls Won", "Performance Off": "Offsides",
            "Performance Crs": "Crosses", "Performance Int": "Interceptions",
            "Performance TklW": "Tackles Won", "Performance PKwon": "Penalties Won",
            "Performance PKcon": "Penalties Conceded", "Performance OG": "Own Goals"
        },
        "drop": ["90s Played", "Players Used"]
    }
}

# ---------------------- 1. Standings ----------------------
try:
    print("⏳ Fetching Standings...")
    response = requests.get(
        f"{base_url}/competitions/PL/standings",
        headers=api_headers,
        timeout=30
        )
    data = response.json()
    table = data["standings"][0]["table"]

    standings_rows = []
    for entry in table:
        standings_rows.append({
            "Position": entry["position"],
            "Team": entry["team"]["name"],
            "Played": entry["playedGames"],
            "Won": entry["won"],
            "Drawn": entry["draw"],
            "Lost": entry["lost"],
            "Points": entry["points"],
            "Goals For": entry["goalsFor"],
            "Goals Against": entry["goalsAgainst"],
            "Goal Difference": entry["goalDifference"]
        })

    standings_df = pd.DataFrame(standings_rows)
    write_to_sheet(sheet, "Standings", standings_df)

except Exception as e:
    logging.error(f"Failed to process Standings: {e}")
    print(f"❌ Standings failed: {e}")

# ---------------------- 2. Match Results ----------------------
try:
    print("⏳ Fetching Match Results...")
    response = requests.get(
        f"{base_url}/competitions/PL/matches",
        headers=api_headers,
        timeout=30
        )
    data = response.json()
    matches = data["matches"]

    match_rows = []
    for match in matches:
        match_rows.append({
            "Matchday": match["matchday"],
            "Date": match["utcDate"][:10],
            "Home Team": match["homeTeam"]["name"],
            "Away Team": match["awayTeam"]["name"],
            "Home Goals": match["score"]["fullTime"]["home"],
            "Away Goals": match["score"]["fullTime"]["away"],
            "Status": match["status"]
        })

    matches_df = pd.DataFrame(match_rows)
    write_to_sheet(sheet, "Match Results", matches_df)

except Exception as e:
    logging.error(f"Failed to process Match Results: {e}")
    print(f"❌ Match Results failed: {e}")


# ---------------------- 3. Team Stats ----------------------
for sheet_title, config in stat_configs.items():
    try:
        print(f"⏳ Fetching {sheet_title}...")
        df = fbref.read_team_season_stats(stat_type=config["stat_type"])
        df = flatten_columns(df)
        df = reset_index_clean(df)

        # Drop url column if present
        if 'url' in df.columns:
            df = df.drop(columns=['url'])

        # Drop duplicate team columns if present
        df = df.loc[:, ~df.columns.duplicated()]

        # Rename columns
        df = df.rename(columns=config["rename"])

        # Drop unwanted columns that exist in the dataframe
        cols_to_drop = [c for c in config["drop"] if c in df.columns]
        df = df.drop(columns=cols_to_drop)

        write_to_sheet(sheet, sheet_title, df)
        time.sleep(10)

    except Exception as e:
        logging.error(f"Failed to process '{sheet_title}': {e}")
        print(f"❌ '{sheet_title}' failed: {e}")
        time.sleep(10)
        continue

# ---------------------- 4. Team Leaders (Top Scorer & Assister Per Team) ----------------------
try:
    print("⏳ Fetching Team Leaders...")
    df_players = fbref.read_player_season_stats(stat_type="standard")
    df_players = df_players.reset_index()

    # Flatten multi-index columns first
    df_players.columns = [' '.join(col).strip() for col in df_players.columns.values]

    # Target the correct flattened column names
    team_col = 'team'
    player_col = 'player'
    goal_col = 'Performance Gls'
    assist_col = 'Performance Ast'

    # Convert to numeric
    df_players[goal_col] = pd.to_numeric(df_players[goal_col], errors='coerce').fillna(0)
    df_players[assist_col] = pd.to_numeric(df_players[assist_col], errors='coerce').fillna(0)

    # Top scorer per team
    top_scorers = df_players.loc[df_players.groupby(team_col)[goal_col].idxmax()][
        [team_col, player_col, goal_col]
    ]
    top_scorers.columns = ['Team', 'Top Scorer', 'Goals']

    # Top assister per team
    top_assisters = df_players.loc[df_players.groupby(team_col)[assist_col].idxmax()][
        [team_col, player_col, assist_col]
    ]
    top_assisters.columns = ['Team', 'Top Assister', 'Assists']

    # Merge into one clean table
    team_leaders = pd.merge(top_scorers, top_assisters, on='Team').reset_index(drop=True)

    write_to_sheet(sheet, "Team Leaders", team_leaders)

except Exception as e:
    logging.error(f"Failed to process Team Leaders: {e}")
    print(f"❌ Team Leaders failed: {e}")

# ---------------------- 5. Goals and Assists ----------------------
try:
    print("⏳ Fetching Goals and Assists...")
    df_league = fbref.read_player_season_stats(stat_type="standard")
    df_league = df_league.reset_index()

    # Flatten multi-index columns
    df_league.columns = [' '.join(col).strip() for col in df_league.columns.values]

    team_col = 'team'
    player_col = 'player'
    goal_col = 'Performance Gls'
    assist_col = 'Performance Ast'

    # Convert to numeric
    df_league[goal_col] = pd.to_numeric(df_league[goal_col], errors='coerce').fillna(0)
    df_league[assist_col] = pd.to_numeric(df_league[assist_col], errors='coerce').fillna(0)

    # Top 20 scorers in the league
    scorers = df_league[[team_col, player_col, goal_col]].sort_values(
        by=goal_col, ascending=False
    ).reset_index(drop=True)
    scorers.columns = ['Team', 'Player', 'Goals']
    scorers.index += 1  # Start ranking from 1

    # Top 20 assisters in the league
    assisters = df_league[[team_col, player_col, assist_col]].sort_values(
        by=assist_col, ascending=False
    ).reset_index(drop=True)
    assisters.columns = ['Team', 'Player', 'Assists']
    assisters.index += 1  # Start ranking from 1

    # Combine side by side into one clean sheet
    scorers = scorers.reset_index().rename(columns={'index': 'Rank'})
    assisters = assisters.reset_index().rename(columns={'index': 'Rank'})

    # Add a separator column then merge side by side
    scorers[''] = ''
    league_leaders = pd.concat([scorers, assisters], axis=1)

    write_to_sheet(sheet, "Goals and Assists", league_leaders)

except Exception as e:
    logging.error(f"Failed to process Goals and Assists: {e}")
    print(f"❌ Goals and Assists failed: {e}")


# ---------------------- Final Output ----------------------
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
print(f"✅ Premier League Data successfully written to Google Sheets ⚽\n📄 {sheet_url}")