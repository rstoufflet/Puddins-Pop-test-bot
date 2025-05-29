from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BACKEND_URL = "https://puddins-drive-sync.onrender.com/files/"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    sport = data.get("sport")
    teams = data.get("teams")

    return jsonify({
        "intro": f"I’m Scott Ferrall, diving into ALL files for {sport} FIRST!",
        "game": f"Game: {teams}",
        "fire": "Ferrall’s Fire: We’re bringing the heat today, folks!",
        "file_stats": "wOBA: .341, xFIP: 3.78, Barrel %: 10.5 - (from MLB_6_stats_summary.xlsx)",
        "odds_check": "FanDuel has it -115 for the home team.",
        "web_boost": "Weather looks clear, no lineup issues reported.",
        "pick": "The Pick: Home team wins with 62% confidence.",
        "bonus_bet": "Bonus Bet: Over 8.5 runs (+110), 58% chance.",
        "final_word": "Ferrall’s Final Word: Smash the over and ride the home heat!"
    })

@app.route("/")
def home():
    return "Puddin's POP Chatbot Test is running. POST to /predict with JSON data."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
