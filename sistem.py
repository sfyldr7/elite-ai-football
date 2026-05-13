import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# API
# =========================================================

API_KEY = "2549da2ef45ba49efcd4b5ec65be1d7e"

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# =========================================================
# SAYFA
# =========================================================

st.set_page_config(
    page_title="ELITE AI LIVE TERMINAL",
    page_icon="⚽",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #050816;
    color: white;
}

.block-container {
    padding-top: 1rem;
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #00ffae;
    text-shadow: 0px 0px 20px #00ffae;
}

.signal-card {
    background: linear-gradient(145deg,#0f172a,#111827);
    border: 1px solid #1f2937;
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0px 0px 15px rgba(0,255,174,0.15);
}

.signal-title {
    font-size: 26px;
    font-weight: bold;
    color: #00ffae;
}

.signal-red {
    color: #ff4d6d;
    font-weight: bold;
    font-size: 22px;
}

.signal-green {
    color: #00ffae;
    font-weight: bold;
    font-size: 22px;
}

.metric-box {
    background: #0b1220;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #1f2937;
}

.metric-value {
    font-size: 30px;
    color: #00ffae;
    font-weight: bold;
}

.metric-title {
    font-size: 14px;
    color: #94a3b8;
}

.small-text {
    color: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# BAŞLIK
# =========================================================

st.markdown("""
<div class="main-title">
⚽ ELITE AI CANLI FUTBOL TRADER TERMINALİ
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# VALUE LİGLER
# =========================================================

VALUE_LEAGUES = [
    "Australia",
    "Japan",
    "Korea",
    "Norway",
    "Sweden",
    "Finland",
    "Reserve",
    "Youth",
    "U23",
    "Women"
]

# =========================================================
# API
# =========================================================

def get_live_matches():

    url = f"{BASE_URL}/fixtures?live=all"

    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return []

    return r.json()["response"]

def get_stats(fixture_id):

    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"

    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return []

    return r.json()["response"]

# =========================================================
# STAT
# =========================================================

def stat(stats, key):

    for item in stats:

        if item["type"] == key:

            val = item["value"]

            if val is None:
                return 0

            if isinstance(val, str):
                val = val.replace("%","")

            try:
                return float(val)

            except:
                return 0

    return 0

# =========================================================
# MOMENTUM
# =========================================================

def momentum(stats):

    dangerous = stat(stats,"Dangerous Attacks")
    sog = stat(stats,"Shots on Goal")
    corners = stat(stats,"Corner Kicks")
    possession = stat(stats,"Ball Possession")

    score = (
        dangerous * 0.45 +
        sog * 14 +
        corners * 4 +
        possession * 0.25
    )

    return round(score,2)

# =========================================================
# MAÇ KALİTE
# =========================================================

def quality_score(
    hm,
    am,
    hs,
    aw,
    danger_total
):

    q = (
        (hm+am)*0.25 +
        (hs+aw)*10 +
        danger_total*0.45
    )

    return round(min(q,100),2)

# =========================================================
# AI GOL İHTİMALİ
# =========================================================

def goal_probability(
    momentum,
    sog,
    dangerous,
    corners
):

    p = (
        momentum*0.35 +
        sog*12 +
        dangerous*0.25 +
        corners*5
    )

    return round(min(p,95),2)

# =========================================================
# SİNYAL MOTORU
# =========================================================

def signal_engine(
    minute,
    hm,
    am,
    hs,
    aw,
    hd,
    ad
):

    diff = abs(hm-am)

    # CHAOS
    if (
        minute >= 70 and
        (hs+aw) >= 8 and
        (hd+ad) >= 70
    ):

        return "🔥 KAOS MODU", 9.5

    # EXTREME HOME
    if (
        hm > am and
        hs >= 4 and
        hd >= 30 and
        diff >= 20
    ):

        return "🟢 EV BASKISI", 8.8

    # EXTREME AWAY
    if (
        am > hm and
        aw >= 4 and
        ad >= 30 and
        diff >= 20
    ):

        return "🔴 DEPLASMAN BASKISI", 8.8

    # DEAD
    if (
        minute >= 35 and
        (hs+aw) <= 1
    ):

        return "❄️ ÖLÜ MAÇ", 7.0

    return None, 0

# =========================================================
# CANLI MAÇLAR
# =========================================================

matches = get_live_matches()

signals = []

# =========================================================
# ANALİZ
# =========================================================

for match in matches:

    try:

        fixture_id = match["fixture"]["id"]

        minute = match["fixture"]["status"]["elapsed"]

        if minute is None:
            continue

        league = match["league"]["name"]

        league_lower = league.lower()

        value_found = False

        for val in VALUE_LEAGUES:

            if val.lower() in league_lower:
                value_found = True
                break

        if not value_found:
            continue

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        hg = match["goals"]["home"] or 0
        ag = match["goals"]["away"] or 0

        stats = get_stats(fixture_id)

        if len(stats) < 2:
            continue

        home_stats = stats[0]["statistics"]
        away_stats = stats[1]["statistics"]

        hm = momentum(home_stats)
        am = momentum(away_stats)

        hs = stat(home_stats,"Shots on Goal")
        aw = stat(away_stats,"Shots on Goal")

        hd = stat(home_stats,"Dangerous Attacks")
        ad = stat(away_stats,"Dangerous Attacks")

        hc = stat(home_stats,"Corner Kicks")
        ac = stat(away_stats,"Corner Kicks")

        signal, confidence = signal_engine(
            minute,
            hm,
            am,
            hs,
            aw,
            hd,
            ad
        )

        if signal is None:
            continue

        quality = quality_score(
            hm,
            am,
            hs,
            aw,
            hd+ad
        )

        probability = goal_probability(
            max(hm,am),
            max(hs,aw),
            max(hd,ad),
            max(hc,ac)
        )

        signals.append({
            "league": league,
            "home": home,
            "away": away,
            "minute": minute,
            "score": f"{hg}-{ag}",
            "signal": signal,
            "confidence": confidence,
            "quality": quality,
            "probability": probability,
            "hm": hm,
            "am": am
        })

    except:
        pass

# =========================================================
# SIRALAMA
# =========================================================

signals = sorted(
    signals,
    key=lambda x: x["probability"],
    reverse=True
)

# =========================================================
# SİNYAL YOK
# =========================================================

if len(signals) == 0:

    st.warning("Şu anda güçlü sinyal bulunamadı.")

# =========================================================
# SİNYAL KARTLARI
# =========================================================

for s in signals:

    st.markdown(f"""
    <div class="signal-card">

    <div class="signal-title">
    {s['home']} vs {s['away']}
    </div>

    <div class="small-text">
    🏆 {s['league']}
    </div>

    <br>

    <div class="signal-green">
    {s['signal']}
    </div>

    <br>

    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Dakika</div>
        <div class="metric-value">{s['minute']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Skor</div>
        <div class="metric-value">{s['score']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">AI Güven</div>
        <div class="metric-value">{s['confidence']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Gol İhtimali</div>
        <div class="metric-value">%{s['probability']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Kalite</div>
        <div class="metric-value">{s['quality']}</div>
        </div>
        """, unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=["Ev Sahibi","Deplasman"],
        y=[s["hm"],s["am"]],
        mode="lines+markers",
        line=dict(width=5),
    ))

    fig.update_layout(
        height=250,
        template="plotly_dark",
        title="Canlı Momentum Akışı",
        margin=dict(l=20,r=20,t=40,b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}"
)