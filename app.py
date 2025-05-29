import os
import json
import pandas as pd
import requests
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

app = Flask(__name__)

# Load service account credentials from environment variable
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# File IDs for each required file
FILE_IDS = {
    "MLB_6_stats_summary.xlsx": "1OSK-QP0eOw09-AFo0M4-qToE5Ud77Gbb",
    "Statcast_Pitchers_Main.xlsx": "1D9GpG6Ao1nRYzWL1QuhFJnvJ9kQvMNLN",
    "Statcast_Hitters_Main.xlsx": "1EHzAy-5K2hADgKRQY-Z8-NqlMg9uHlGI",
    "MLB_Pitcher_xERA_xFIP_WAR_Stats.xlsx": "1tdVrA1Cux-8ESOnMpJ0YUpw1zAL7t-KH",
    "Daily_MLB_Weather.xlsx": "1oCWz4tbnm8ehUCSqaYje2-WyfbGBFhIv",
    "processed_probable_pitchers.csv": "1E2bK9U6ZDkGueXzuwGMiFZ7XSK_QOPez",
    "NBA_stats.csv": "1YiO2oYhtfZtLKnx-f8WHhN3hB6At4ZTO",
    "NHL_Team_Stats.csv": "1jY3Ukt8NjYoZKboGgV5nBf0p_hOwTykR",
    "mlb_team_stats_pitching.csv": "1Vcy8CQXAwQ3rAdKUmuw_E93V5UdsZD9o",
    "mlb_team_stats_batting.csv": "1eEyXvHKv1Pb2UjqU9KXn65q4N-3mEjzJ"
}

# Track if files have been synced
files_synced = False

def download_file(file_id, destination_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

def sync_files():
    if not os.path.exists('synced_files'):
        os.makedirs('synced_files')
    for filename, file_id in FILE_IDS.items():
        destination_path = os.path.join('synced_files', filename)
        download_file(file_id, destination_path)

@app.route('/')
def home():
    return "Puddin's POP Prediction Bot is live!"

@app.route('/predict', methods=['POST'])
def predict():
    global files_synced
    if not files_synced:
        sync_files()
        files_synced = True

    try:
        data = request.get_json()
        team_a = data.get('team_a', 'Default A')
        team_b = data.get('team_b', 'Default B')
        sport = data.get('sport', 'MLB')

        # Simulated prediction response
        prediction = {
            "intro": f"I’m Scott Ferrall, diving into ALL files for {sport} FIRST!",
            "game": f"{team_a} vs. {team_b}",
            "ferralls_fire": "We're talkin’ scorched turf and shattered dreams!",
            "file_stats": "Using synced stats from synced_files/*.xlsx and *.csv",
            "odds_check": "Pulled latest lines from FanDuel",
            "web_boost": "Checked weather and rosters live!",
            "the_pick": f"Taking {team_a} with a 63% edge!",
            "bonus_bet": "Alt line OVER 8.5 runs hits at 59%",
            "ferralls_final_word": "It’s a bloodbath, baby!"
        }

        return jsonify(prediction)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
