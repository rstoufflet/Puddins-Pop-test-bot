from flask import Flask, send_file
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import json

# Flask app setup
app = Flask(__name__)

# Google Drive API setup using credentials from environment variable
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Files to sync: mapping filename to Google Drive file ID
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

# Folder to store synced files
DOWNLOAD_DIR = 'synced_files'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download a single file
def download_file(file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print(f'Downloaded: {filename}')

# Sync all files from Drive
@app.before_first_request
def sync_files():
    for filename, file_id in FILES.items():
        download_file(file_id, filename)

# Serve files via Flask
@app.route('/files/<path:filename>')
def serve_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path)
    return 'File not found', 404

# Run the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
