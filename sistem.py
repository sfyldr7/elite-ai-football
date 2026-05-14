import streamlit as st
import requests

# ======================================
# SAYFA AYARI
# ======================================
st.set_page_config(
    page_title="ELITE AI",
    layout="wide"
)

# ======================================
# CSS
# ======================================
st.markdown("""
<style>

html, body, [class*="css"]{
    background-color:#050816;
    color:white;
}

.main-title{
    font-size:52px;
    font-weight:900;
    color:white;
    margin-bottom:30px;
}

.match-card{
    background:#111827;
    padding:20px;
    border-radius:20px;
    margin-bottom:15px;
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
    font-size:18px;
    font-weight:bold;
}

.signal-mid{
    color:#facc15;
    font-size:18px;
    font-weight:bold;
}

.signal-low{
    color:#ef4444;
    font-size:18px;
    font-weight:bold;
}

.prob{
    color:#38bdf8;
    font-size:18px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ======================================
# BAŞLIK
# ======================================
st.markdown("""
<div class="main-title">
⚽ ELITE AI CANLI FUTBOL TERMINALI
</div>
""", unsafe_allow_html=True)

# ======================================
# API KEY
# ======================================
API_KEY = "0a278e2125fc4eec7c0ac24ac276dabf"

# ======================================
# CACHE (5 DAKİKA)
# ======================================
@st.cache_data(ttl=300)
def canli_maclar():

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise Exception(f"API Hatası: {response.status_code}")

    return response.json()

# ======================================
# ANALİZ
# ======================================
def analiz_yap(home_goal, away_goal, minute):

    total = home_goal + away_goal

    mesaj = "NORMAL"
    css = "signal-low"
    ihtimal = 50

    if minute >= 70 and total <= 1:
        mesaj = "GOL YÜKSEK"
        css = "signal-high"
        ihtimal = 84

    elif minute >= 55 and total <= 2:
        mesaj = "GOL OLABİLİR"
        css = "signal-mid"
        ihtimal = 72

    elif minute <= 20 and total == 0:
        mesaj = "TEMKİNLİ"
        css = "signal-low"
        ihtimal = 58

    return mesaj, css, ihtimal

# ======================================
# VERİ ÇEK
# ======================================
try:

    data = canli_maclar()

    matches = data["response"]

    if len(matches) == 0:
        st.warning("Şu anda canlı maç yok.")

    for match in matches:

        league = match["league"]["name"]

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_goal = match["goals"]["home"] or 0
        away_goal = match["goals"]["away"] or 0

        minute = match["fixture"]["status"]["elapsed"] or 0

        mesaj, css, ihtimal = analiz_yap(
            home_goal,
            away_goal,
            minute
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
