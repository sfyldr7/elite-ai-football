import requests
import time
import sqlite3
import threading
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List

# =========================
# API SETTINGS
# =========================
API_KEY = "2549da2ef45ba49efcd4b5ec65be1d7e"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# =========================
# CONFIG
# =========================
REFRESH_SECONDS = 30

# =========================
# DATABASE
# =========================
def init_database():
    conn = sqlite3.connect("momentum_system.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fixture_id INTEGER,
        home TEXT,
        away TEXT,
        minute INTEGER,
        score TEXT,
        signal TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# =========================
# DATA MODEL
# =========================
@dataclass
class MatchSignal:
    fixture_id: int
    home: str
    away: str
    minute: int
    score: str
    signal: str
    confidence: float

# =========================
# API FUNCTIONS
# =========================
def get_live_matches():
    url = f"{BASE_URL}/fixtures?live=all"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return []

    data = response.json()

    return data.get("response", [])

def get_fixture_statistics(fixture_id):

    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return []

    data = response.json()

    return data.get("response", [])

# =========================
# PARSE STATS
# =========================
def parse_stat(stats, key):

    for item in stats:

        if item["type"] == key:

            value = item["value"]

            if value is None:
                return 0

            if isinstance(value, str):
                value = value.replace("%", "")

            try:
                return float(value)
            except:
                return 0

    return 0

# =========================
# MOMENTUM ENGINE
# =========================
def calculate_momentum(stats):

    dangerous = parse_stat(stats, "Dangerous Attacks")
    shots_on_goal = parse_stat(stats, "Shots on Goal")
    corners = parse_stat(stats, "Corner Kicks")
    possession = parse_stat(stats, "Ball Possession")

    momentum = (
        dangerous * 0.4 +
        shots_on_goal * 0.3 +
        corners * 0.2 +
        possession * 0.1
    )

    return round(momentum, 2)

# =========================
# MATCH QUALITY SCORE
# =========================
def calculate_match_quality(
    home_momentum,
    away_momentum,
    home_sog,
    away_sog,
    dangerous_total
):

    quality = (
        (home_momentum + away_momentum) * 0.3 +
        (home_sog + away_sog) * 12 +
        dangerous_total * 0.4
    )

    return round(min(quality, 100), 2)

# =========================
# HEATMAP
# =========================
def build_heatmap(momentum, dangerous):

    heat = (
        momentum * 0.6 +
        dangerous * 0.4
    )

    return round(heat, 2)

# =========================
# NEURAL NETWORK MODEL
# =========================
class NeuralPredictionModel:

    def __init__(self):

        self.weights = {
            "momentum": 0.35,
            "shots": 0.30,
            "dangerous": 0.20,
            "corners": 0.15
        }

    def predict_goal_probability(
        self,
        momentum,
        shots,
        dangerous,
        corners
    ):

        score = (
            momentum * self.weights["momentum"] +
            shots * self.weights["shots"] * 10 +
            dangerous * self.weights["dangerous"] +
            corners * self.weights["corners"] * 5
        )

        return round(min(score, 95), 2)

neural_model = NeuralPredictionModel()

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(
    minute,
    home_momentum,
    away_momentum,
    home_sog,
    away_sog,
    home_dangerous,
    away_dangerous
):

    diff = abs(home_momentum - away_momentum)

    # EXTREME HOME
    if (
        minute >= 18 and
        minute <= 70 and
        home_momentum > away_momentum and
        home_sog >= 3 and
        home_dangerous >= 20 and
        diff >= 15
    ):

        return "EXTREME HOME NEXT GOAL", 9.1

    # EXTREME AWAY
    if (
        minute >= 18 and
        minute <= 70 and
        away_momentum > home_momentum and
        away_sog >= 3 and
        away_dangerous >= 20 and
        diff >= 15
    ):

        return "EXTREME AWAY NEXT GOAL", 9.1

    # CHAOS MODE
    if (
        minute >= 75 and
        (home_sog + away_sog) >= 8
    ):

        return "CHAOS GOAL ALERT", 8.5

    # DEAD MATCH
    if (
        minute >= 35 and
        (home_sog + away_sog) <= 1
    ):

        return "DEAD MATCH", 7.0

    return "NO SIGNAL", 0

# =========================
# MODERN UI
# =========================
def modern_header():

    print("\n")
    print("#" * 70)
    print("#      ELITE AI MOMENTUM ANALYSIS SYSTEM             #")
    print("#" * 70)

# =========================
# LIVE GRAPH
# =========================
def print_live_graph(home_momentum, away_momentum):

    home_bar = int(home_momentum / 2)
    away_bar = int(away_momentum / 2)

    print("\nLIVE MOMENTUM GRAPH")

    print("HOME : " + "█" * home_bar)
    print("AWAY : " + "█" * away_bar)

# =========================
# SAVE SIGNAL
# =========================
def save_signal(signal):

    conn = sqlite3.connect("momentum_system.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO signals (
        fixture_id,
        home,
        away,
        minute,
        score,
        signal,
        confidence
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        signal.fixture_id,
        signal.home,
        signal.away,
        signal.minute,
        signal.score,
        signal.signal,
        signal.confidence
    ))

    conn.commit()
    conn.close()

# =========================
# AI DATASET EXPORT
# =========================
def export_dataset():

    conn = sqlite3.connect("momentum_system.db")

    query = "SELECT * FROM signals"

    df = pd.read_sql(query, conn)

    conn.close()

    df.to_csv("training_dataset.csv", index=False)

# =========================
# AUTO COUPON
# =========================
def generate_coupon(signals):

    print("\nAUTO COUPON")
    print("=" * 50)

    sorted_signals = sorted(
        signals,
        key=lambda x: x.confidence,
        reverse=True
    )

    top = sorted_signals[:3]

    for s in top:

        print(f"{s.home} vs {s.away}")
        print(f"BET: {s.signal}")
        print(f"CONFIDENCE: {s.confidence}")
        print("-" * 40)

# =========================
# ANALYZE MATCH
# =========================
def analyze_match(match, signal_storage):

    fixture_id = match["fixture"]["id"]

    minute = match["fixture"]["status"]["elapsed"]

    if minute is None:
        return

    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]

    home_goals = match["goals"]["home"] or 0
    away_goals = match["goals"]["away"] or 0

    stats = get_fixture_statistics(fixture_id)

    if len(stats) < 2:
        return

    home_stats = stats[0]["statistics"]
    away_stats = stats[1]["statistics"]

    home_momentum = calculate_momentum(home_stats)
    away_momentum = calculate_momentum(away_stats)

    home_sog = parse_stat(home_stats, "Shots on Goal")
    away_sog = parse_stat(away_stats, "Shots on Goal")

    home_dangerous = parse_stat(home_stats, "Dangerous Attacks")
    away_dangerous = parse_stat(away_stats, "Dangerous Attacks")

    signal, confidence = generate_signal(
        minute,
        home_momentum,
        away_momentum,
        home_sog,
        away_sog,
        home_dangerous,
        away_dangerous
    )

    if signal == "NO SIGNAL":
        return

    probability = neural_model.predict_goal_probability(
        max(home_momentum, away_momentum),
        max(home_sog, away_sog),
        max(home_dangerous, away_dangerous),
        parse_stat(home_stats, "Corner Kicks")
    )

    quality = calculate_match_quality(
        home_momentum,
        away_momentum,
        home_sog,
        away_sog,
        home_dangerous + away_dangerous
    )

    heat_home = build_heatmap(
        home_momentum,
        home_dangerous
    )

    heat_away = build_heatmap(
        away_momentum,
        away_dangerous
    )

    result = MatchSignal(
        fixture_id,
        home,
        away,
        minute,
        f"{home_goals}-{away_goals}",
        signal,
        confidence
    )

    signal_storage.append(result)

    save_signal(result)

    print("\n" + "=" * 60)
    print(f"MATCH: {home} vs {away}")
    print(f"MINUTE: {minute}")
    print(f"SCORE: {home_goals}-{away_goals}")
    print(f"SIGNAL: {signal}")
    print(f"CONFIDENCE: {confidence}/10")
    print(f"GOAL PROBABILITY: %{probability}")
    print(f"MATCH QUALITY: {quality}/100")
    print(f"HOME HEAT: {heat_home}")
    print(f"AWAY HEAT: {heat_away}")

    print_live_graph(
        home_momentum,
        away_momentum
    )

# =========================
# MAIN SYSTEM
# =========================
def run_system():

    init_database()

    modern_header()

    while True:

        try:

            live_matches = get_live_matches()

            signal_storage = []

            threads = []

            for match in live_matches:

                t = threading.Thread(
                    target=analyze_match,
                    args=(match, signal_storage)
                )

                threads.append(t)

                t.start()

            for t in threads:
                t.join()

            if len(signal_storage) > 0:
                generate_coupon(signal_storage)

            export_dataset()

        except Exception as e:

            print(f"SYSTEM ERROR: {e}")

        time.sleep(REFRESH_SECONDS)

# =========================
# START
# =========================
if __name__ == "__main__":
    run_system()
