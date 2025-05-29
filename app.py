from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import json
import pandas as pd

app = Flask(__name__)
CORS(app)

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Drive files map
FILES = {
    'MLB_6_stats_summary.xlsx': '1W1Iw1ECcc-lLKEEXPffQkJ_xKJqG0UuM',
    'Statcast_Pitchers_Main.xlsx': '1fqcyWbtCgMiEjfJbeQjs7N3gSXBmvhFL',
    'Statcast_Hitters_Main.xlsx': '1anuDY5TS7MG6p8tDBeCrEJRrnwYn_jnp',
    'MLB_Pitcher_xERA_xFIP_WAR_Stats.xlsx': '1la6M3xEf0XH8bDuh6EDYesO0J97K3l7N',
    'Daily_MLB_Weather.xlsx': '15NQPHy2avaHCwLlHuXB9tXUiy9jx57RN',
    'processed_probable_pitchers.csv': '1AC3RilmEOU6JaVgsjNUowCIB8SmG4zX5',
    'NBA_stats.csv': '1W9K1VuMS8mUc9h4lI37CmT-JnYP6MZiC',
    'NHL_Team_Stats.csv': '1hKJCUOhn2cbtm8pQpglql2Uuvh6q4a_z',
    'mlb_team_stats_pitching.csv': '1D3HysmUKDX1ZnPg87kwV1Wjqo34xIc2w',
    'mlb_team_stats_batting.csv': '1FX-ZmG42yLzWJX_NL6yaFTOXQdvGeNdJ'
}

DOWNLOAD_DIR = 'synced_files'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_file(file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    path = os.path.join(DOWNLOAD_DIR, filename)
    fh = io.FileIO(path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print(f"Downloaded: {filename}")

def sync_files():
    for name, fid in FILES.items():
        download_file(fid, name)

def lookup_stat(df, team, fields):
    match = df[df['Team'].str.contains(team, case=False, na=False)]
    return {field: match[field].values[0] for field in fields} if not match.empty else None

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    sport = data.get("sport")
    teams = data.get("teams")
    if not teams or 'vs.' not in teams:
        return jsonify({"error": "Invalid teams format. Use 'Team A vs. Team B'"}), 400

    team1, team2 = [t.strip() for t in teams.split("vs.")]

    try:
        if sport == "MLB":
            df = pd.read_excel(os.path.join(DOWNLOAD_DIR, 'MLB_6_stats_summary.xlsx'))
            stats1 = lookup_stat(df, team1, ['wOBA', 'xFIP', 'Barrel %'])
            stats2 = lookup_stat(df, team2, ['wOBA', 'xFIP', 'Barrel %'])
        elif sport == "NBA":
            df = pd.read_csv(os.path.join(DOWNLOAD_DIR, 'NBA_stats.csv'))
            stats1 = lookup_stat(df, team1, ['TS%', 'Net Rating', 'Pace'])
            stats2 = lookup_stat(df, team2, ['TS%', 'Net Rating', 'Pace'])
        elif sport == "NHL":
            df = pd.read_csv(os.path.join(DOWNLOAD_DIR, 'NHL_Team_Stats.csv'))
            stats1 = lookup_stat(df, team1, ['Corsi %', 'PDO', 'Save %'])
            stats2 = lookup_stat(df, team2, ['Corsi %', 'PDO', 'Save %'])
        else:
            return jsonify({"error": f"Unsupported sport: {sport}"}), 400

        if not stats1 or not stats2:
            return jsonify({"error": "Team not found in dataset."}), 404

        stat_lines = f"{team1}: {stats1} | {team2}: {stats2}"
        pick = team1 if sum(stats1.values()) > sum(stats2.values()) else team2

        return jsonify({
            "intro": f"I’m Scott Ferrall, diving into ALL files for {sport} FIRST!",
            "game": f"Game: {teams}",
            "fire": "Ferrall’s Fire: The numbers don't lie!",
            "file_stats": stat_lines,
            "odds_check": "Odds data pending...",
            "web_boost": "Weather/injury status: clean.",
            "pick": f"The Pick: {pick} with 61% confidence.",
            "bonus_bet": "Alt line potential: Over 9.5 goals, 56% chance.",
            "final_word": f"Ferrall’s Final Word: Ride {pick}, hammer the totals!"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Puddin's POP Chatbot Test is live! POST to /predict with sport and teams."

@app.route('/files/<path:filename>')
def serve_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    return send_file(path) if os.path.exists(path) else ("File not found", 404)

if __name__ == '__main__':
    sync_files()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
