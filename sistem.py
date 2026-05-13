import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =====================================
# API
# =====================================
API_KEY = "2549da2ef45ba49efcd4b5ec65be1d7e"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# =====================================
# SAYFA AYARLARI
# =====================================
st.set_page_config(
    page_title="ELITE AI LIVE TERMINAL",
    layout="wide"
)

# =====================================
# CSS
# =====================================
st.markdown("""
<style>

html, body, [class*="css"]  {
    background-color: #0f172a;
    color: white;
}

.main-title {
    font-size: 38px;
    font-weight: bold;
    color: #00ff99;
    margin-bottom: 25px;
}

.match-card {
    background: #111827;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 12px;
    border: 1px solid #1f2937;
}

.league {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 8px;
}

.teams {
    font-size: 22px;
    font-weight: bold;
}

.minute {
    color: orange;
    font-size: 17px;
    font-weight: bold;
}

.signal-green {
    background: #064e3b;
    color: #6ee7b7;
    padding: 6px 12px;
    border-radius: 10px;
    font-weight: bold;
    display: inline-block;
}

.signal-red {
    background: #7f1d1d;
    color: #fca5a5;
    padding: 6px 12px;
    border-radius: 10px;
    font-weight: bold;
    display: inline-block;
}

.signal-yellow {
    background: #78350f;
    color: #fde68a;
    padding: 6px 12px;
    border-radius: 10px;
    font-weight: bold;
    display: inline-block;
}

.signal-gray {
    background: #374151;
    color: #d1d5db;
    padding: 6px 12px;
    border-radius: 10px;
    font-weight: bold;
    display: inline-block;
}

.probability {
    font-size: 18px;
    font-weight: bold;
    color: #00ff99;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# BAŞLIK
# =====================================
st.markdown("""
<div class="main-title">
⚽ ELITE AI CANLI FUTBOL TERMİNALİ
</div>
""", unsafe_allow_html=True)

# =====================================
# API FUNCTIONS
# =====================================
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

# =====================================
# PARSE
# =====================================
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

# =====================================
# MOMENTUM
# =====================================
def calculate_momentum(stats):

    dangerous = parse_stat(stats, "Dangerous Attacks")
    shots = parse_stat(stats, "Shots on Goal")
    corners = parse_stat(stats, "Corner Kicks")
    possession = parse_stat(stats, "Ball Possession")

    momentum = (
        dangerous * 0.4 +
        shots * 12 +
        corners * 4 +
        possession * 0.3
    )

    return round(momentum, 2)

# =====================================
# AI SIGNAL
# =====================================
def generate_signal(
    minute,
    home_momentum,
    away_momentum,
    home_sog,
    away_sog,
    home_dangerous,
    away_dangerous
):

    total_sog = home_sog + away_sog

    # KAOS
    if minute >= 75 and total_sog >= 8:
        return "💣 KAOS MAÇI", "signal-red", 87

    # EV GOL
    if (
        home_momentum > away_momentum and
        home_sog >= 3 and
        home_dangerous >= 20
    ):
        return "🔥 EV GOLÜ YÜKSEK", "signal-green", 78

    # DEPLASMAN GOL
    if (
        away_momentum > home_momentum and
        away_sog >= 3 and
        away_dangerous >= 20
    ):
        return "🚨 DEPLASMAN GOLÜ", "signal-yellow", 75

    # ÖLÜ
    if minute >= 35 and total_sog <= 1:
        return "💀 ÖLÜ MAÇ", "signal-gray", 22

    return "⚪ NORMAL", "signal-gray", 50

# =====================================
# MAÇLARI ÇEK
# =====================================
matches = get_live_matches()

if len(matches) == 0:

    st.warning("Şu anda canlı maç bulunamadı.")

else:

    signal_matches = []

    for match in matches:

        try:

            fixture_id = match["fixture"]["id"]

            minute = match["fixture"]["status"]["elapsed"]

            if minute is None:
                continue

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            league = match["league"]["name"]

            home_goals = match["goals"]["home"] or 0
            away_goals = match["goals"]["away"] or 0

            stats = get_fixture_statistics(fixture_id)

            if len(stats) < 2:
                continue

            home_stats = stats[0]["statistics"]
            away_stats = stats[1]["statistics"]

            home_momentum = calculate_momentum(home_stats)
            away_momentum = calculate_momentum(away_stats)

            home_sog = parse_stat(home_stats, "Shots on Goal")
            away_sog = parse_stat(away_stats, "Shots on Goal")

            home_dangerous = parse_stat(
                home_stats,
                "Dangerous Attacks"
            )

            away_dangerous = parse_stat(
                away_stats,
                "Dangerous Attacks"
            )

            signal, signal_class, probability = generate_signal(
                minute,
                home_momentum,
                away_momentum,
                home_sog,
                away_sog,
                home_dangerous,
                away_dangerous
            )

            signal_matches.append({
                "league": league,
                "minute": minute,
                "home": home,
                "away": away,
                "score": f"{home_goals}-{away_goals}",
                "signal": signal,
                "signal_class": signal_class,
                "probability": probability
            })

        except:
            pass

    # =====================================
    # EN İYİLERİ ÜSTE
    # =====================================
    signal_matches = sorted(
        signal_matches,
        key=lambda x: x["probability"],
        reverse=True
    )

    # =====================================
    # GÖSTER
    # =====================================
    for m in signal_matches:

        st.markdown(f"""
        <div class="match-card">

            <div class="league">
                {m["league"]}
            </div>

            <div class="teams">
                {m["home"]} {m["score"]} {m["away"]}
            </div>

            <br>

            <span class="minute">
                {m["minute"]}'
            </span>

            &nbsp;&nbsp;

            <span class="{m["signal_class"]}">
                {m["signal"]}
            </span>

            &nbsp;&nbsp;

            <span class="probability">
                %{m["probability"]}
            </span>

        </div>
        """, unsafe_allow_html=True)

# =====================================
# FOOTER
# =====================================
st.markdown("---")

st.caption(
    f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}"
)
