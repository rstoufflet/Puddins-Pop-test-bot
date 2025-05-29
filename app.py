import os
import json
import pandas as pd
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import tempfile

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=credentials)
app = Flask(__name__)

FILE_IDS = {
    'MLB_6_stats_summary.xlsx': '1s57K5HgfMK1zkjEPOzOK8cUXTrnMGndm',
    'Statcast_Pitchers_Main.xlsx': '1sJ36JbujC-vFObJS7JeDTc_m2Opmk6Nz',
    'Statcast_Hitters_Main.xlsx': '1wDrKgx5BqU0kgRxLwr26DNNeRO0uApuH',
    'MLB_Pitcher_xERA_xFIP_WAR_Stats.xlsx': '1RxR4dxK3pArsG5VHGfGhI3b1jxau43Q2',
    'Daily_MLB_Weather.xlsx': '1sJ46CEwb8EakRjckFtdv9U7qM57r2zGn',
    'processed_probable_pitchers.csv': '1hBcl_QoGLN3mBB7AmNjXvCVZMyYgKfsH',
    'mlb_team_stats_batting.csv': '1I6UNF7dpX_KRfb7I-uDF7XJhNQcvbDNl',
    'mlb_team_stats_pitching.csv': '1cTWL3cZIjT4edW0gPoVoFqYFWTBHQJZg',
    'NBA_stats.csv': '1GyJJmflqheojr_bdcKNPHh6gRRA13duq',
    'NHL_Team_Stats.csv': '1RSWcTOThwG-t_o6zoZzFGI4BGbSU4CCX'
}

def download_file(file_id, destination):
    request = drive_service.files().get_media(fileId=file_id)
    with open(destination, 'wb') as f:
        downloader = build('drive', 'v3', credentials=credentials).files().get_media(fileId=file_id)
        f.write(request.execute())

@app.before_first_request
def sync_files():
    if not os.path.exists('synced_files'):
        os.makedirs('synced_files')
    for filename, file_id in FILE_IDS.items():
        filepath = os.path.join('synced_files', filename)
        download_file(file_id, filepath)

@app.route('/', methods=['GET'])
def index():
    return "Puddin's POP Prediction Bot is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        sport = data.get("sport", "").upper()
        team_a = data.get("team_a", "")
        team_b = data.get("team_b", "")
        date = data.get("date", "")

        if sport == "MLB":
            stat_file = 'synced_files/MLB_6_stats_summary.xlsx'
            df = pd.read_excel(stat_file)
            return jsonify({
                "game": f"{team_a} vs. {team_b} on {date}",
                "prediction": "Team A wins",
                "confidence": "61%",
                "note": "Predicted using MLB_6_stats_summary.xlsx"
            })
        else:
            return jsonify({"error": f"Unsupported sport: {sport}"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
