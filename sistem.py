import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="ELITE AI", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0f172a;
}

.main {
    background-color: #0f172a;
}

.card {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 12px;
    border-left: 5px solid #22c55e;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}

.league {
    color: #38bdf8;
    font-size: 18px;
    font-weight: bold;
}

.teams {
    color: white;
    font-size: 24px;
    font-weight: bold;
}

.minute {
    color: orange;
    font-size: 18px;
}

.signal-red {
    color: #ef4444;
    font-weight: bold;
    font-size: 20px;
}

.signal-green {
    color: #22c55e;
    font-weight: bold;
    font-size: 20px;
}

.signal-yellow {
    color: #facc15;
    font-weight: bold;
    font-size: 20px;
}

.signal-gray {
    color: #9ca3af;
    font-weight: bold;
    font-size: 20px;
}

.probability {
    color: #38bdf8;
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ ELITE AI CANLI FUTBOL TERMINALI")

API_URL = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"

headers = {
    "X-RapidAPI-Key": "2549da2ef45ba49efcd4b5ec65be1d7e",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

try:
    response = requests.get(API_URL, headers=headers)
    data = response.json()

    matches = data["response"]

    if len(matches) == 0:
        st.warning("Canlı maç bulunamadı.")

    else:
        for match in matches:

            league = match["league"]["name"]

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            minute = match["fixture"]["status"]["elapsed"]

            total_goals = (home_goals or 0) + (away_goals or 0)

            signal = "⚪ NORMAL"
            signal_class = "signal-gray"
            probability = 50

            # GOL BASKI SİSTEMİ

            if minute >= 70 and total_goals <= 1:
                signal = "🔥 GOL GELİYOR"
                signal_class = "signal-red"
                probability = 87

            elif minute >= 55 and total_goals >= 2:
                signal = "🟢 ÜST CANLI"
                signal_class = "signal-green"
                probability = 82

            elif minute <= 25 and total_goals >= 1:
                signal = "⚡ MAÇ HIZLI"
                signal_class = "signal-yellow"
                probability = 75

            elif minute >= 80 and abs((home_goals or 0) - (away_goals or 0)) == 1:
                signal = "🚨 SON DAKİKA GOLÜ"
                signal_class = "signal-red"
                probability = 91

            card = f"""
            <div class="card">

                <div class="league">
                    {league}
                </div>

                <br>

                <div class="teams">
                    {home} {home_goals}-{away_goals} {away}
                </div>

                <br>

                <span class="minute">
                    ⏱️ {minute}'
                </span>

                &nbsp;&nbsp;&nbsp;

                <span class="{signal_class}">
                    {signal}
                </span>

                &nbsp;&nbsp;&nbsp;

                <span class="probability">
                    %{probability}
                </span>

            </div>
            """

            st.markdown(card, unsafe_allow_html=True)

    st.caption(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error(f"Hata oluştu: {e}")
