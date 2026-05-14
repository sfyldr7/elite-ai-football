import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="ELITE AI", layout="wide")

# ====== TASARIM ======

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

body {
    background-color: #0f172a;
}

.card {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 12px;
    border-left: 5px solid #22c55e;
}

.league {
    color: #38bdf8;
    font-size: 16px;
    font-weight: bold;
}

.teams {
    color: white;
    font-size: 24px;
    font-weight: bold;
}

.info {
    color: #d1d5db;
    font-size: 18px;
    margin-top: 8px;
}

.red {
    color: #ef4444;
    font-weight: bold;
}

.green {
    color: #22c55e;
    font-weight: bold;
}

.yellow {
    color: #facc15;
    font-weight: bold;
}

.gray {
    color: #9ca3af;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

st.title("⚽ ELITE AI CANLI FUTBOL TERMINALI")

# ====== API ======

API_KEY = "2549da2ef45ba49efcd4b5ec65be1d7e"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# ====== 5 DAKİKA CACHE ======

@st.cache_data(ttl=300)
def maclari_getir():

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"

    response = requests.get(url, headers=headers)

    return response.json()

# ====== VERİ ÇEK ======

try:

    data = maclari_getir()

    matches = data["response"]

    if len(matches) == 0:
        st.warning("Canlı maç bulunamadı.")

    for match in matches:

        league = match["league"]["name"]

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]

        minute = match["fixture"]["status"]["elapsed"]

        total_goals = (home_goals or 0) + (away_goals or 0)

        signal = "⚪ NORMAL"
        signal_class = "gray"
        oran = 50

        # ====== AI SİNYAL ======

        if minute >= 70 and total_goals <= 1:
            signal = "🔥 GOL YÜKSEK"
            signal_class = "red"
            oran = 88

        elif minute >= 55 and total_goals >= 2:
            signal = "🟢 ÜST OLUR"
            signal_class = "green"
            oran = 81

        elif minute <= 25 and total_goals >= 1:
            signal = "⚡ MAÇ HIZLI"
            signal_class = "yellow"
            oran = 73

        elif minute >= 80:
            signal = "🚨 SON DAKİKA"
            signal_class = "red"
            oran = 91

        card = f"""
        <div class="card">

            <div class="league">
                {league}
            </div>

            <br>

            <div class="teams">
                {home} {home_goals}-{away_goals} {away}
            </div>

            <div class="info">
                ⏱️ {minute}'
                   
                <span class="{signal_class}">
                    {signal}
                </span>
                   
                %{oran}
            </div>

        </div>
        """

        st.markdown(card, unsafe_allow_html=True)

    st.caption(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")

except:
    st.error("API veya kod hatası oluştu.")
