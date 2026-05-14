import streamlit as st
import requests
import time

# =========================
# SAYFA AYARLARI
# =========================
st.set_page_config(
    page_title="ELITE AI",
    layout="wide"
)

# =========================
# CSS TASARIM
# =========================
st.markdown("""
<style>
html, body, [class*="css"]{
    background-color:#050816;
    color:white;
}

.main-title{
    font-size:48px;
    font-weight:bold;
    color:white;
    margin-bottom:25px;
}

.match-card{
    background:#111827;
    padding:18px;
    border-radius:18px;
    margin-bottom:14px;
    border:1px solid #1f2937;
}

.league{
    color:#9ca3af;
    font-size:14px;
    margin-bottom:8px;
}

.teams{
    font-size:24px;
    font-weight:bold;
    color:white;
}

.minute{
    color:#22c55e;
    font-size:16px;
    font-weight:bold;
}

.signal-high{
    color:#22c55e;
    font-size:20px;
    font-weight:bold;
}

.signal-mid{
    color:#facc15;
    font-size:20px;
    font-weight:bold;
}

.signal-low{
    color:#ef4444;
    font-size:20px;
    font-weight:bold;
}

.prob{
    color:#38bdf8;
    font-size:18px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# BAŞLIK
# =========================
st.markdown("""
<div class="main-title">
⚽ ELITE AI CANLI FUTBOL TERMINALI
</div>
""", unsafe_allow_html=True)

# =========================
# API
# =========================
API_KEY = "2549da2ef45ba49efcd4b5ec65be1d7e"
API_HOST = "api-football-v1.p.rapidapi.com"

# =========================
# CACHE (5 DAKİKA)
# =========================
@st.cache_data(ttl=300)
def maclari_getir():

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise Exception(f"API Hatası: {response.status_code}")

    return response.json()

# =========================
# ANALİZ
# =========================
def analiz_yap(home, away, minute, goals):

    skor = goals["home"] + goals["away"]

    ihtimal = 50
    mesaj = "NORMAL"
    css = "signal-low"

    if minute >= 70 and skor <= 1:
        ihtimal = 82
        mesaj = "GOL YÜKSEK"
        css = "signal-high"

    elif minute >= 55 and skor <= 2:
        ihtimal = 72
        mesaj = "GOL OLABİLİR"
        css = "signal-mid"

    elif minute <= 20 and skor == 0:
        ihtimal = 58
        mesaj = "TEMKİNLİ"
        css = "signal-low"

    return mesaj, ihtimal, css

# =========================
# VERİ ÇEK
# =========================
try:

    data = maclari_getir()

    fixtures = data["response"]

    if len(fixtures) == 0:
        st.warning("Canlı maç bulunamadı.")

    for match in fixtures:

        league = match["league"]["name"]

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_goal = match["goals"]["home"] or 0
        away_goal = match["goals"]["away"] or 0

        minute = match["fixture"]["status"]["elapsed"] or 0

        mesaj, ihtimal, css = analiz_yap(
            home,
            away,
            minute,
            {
                "home": home_goal,
                "away": away_goal
            }
        )

        st.markdown(f"""
        <div class="match-card">

            <div class="league">
                {league}
            </div>

            <div class="teams">
                {home} {home_goal}-{away_goal} {away}
            </div>

            <br>

            <span class="minute">
                {minute}'
            </span>

               

            <span class="{css}">
                ● {mesaj}
            </span>

               

            <span class="prob">
                %{ihtimal}
            </span>

        </div>
        """, unsafe_allow_html=True)

except Exception as e:

    st.error(f"HATA: {e}")
