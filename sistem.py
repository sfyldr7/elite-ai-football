import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re

# ======================================
# SAYFA
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
    background:#050816;
    color:white;
}

.main-title{
    font-size:58px;
    font-weight:900;
    margin-bottom:20px;
}

.card{
    background:#111827;
    padding:22px;
    border-radius:20px;
    margin-top:20px;
    border:1px solid #1f2937;
}

.green{
    color:#22c55e;
    font-size:28px;
    font-weight:bold;
}

.yellow{
    color:#facc15;
    font-size:28px;
    font-weight:bold;
}

.red{
    color:#ef4444;
    font-size:28px;
    font-weight:bold;
}

.blue{
    color:#38bdf8;
    font-size:26px;
    font-weight:bold;
}

.info{
    font-size:22px;
}

</style>
""", unsafe_allow_html=True)

# ======================================
# BAŞLIK
# ======================================

st.markdown("""
<div class="main-title">
⚽ ELITE AI GÖRSEL MAÇ ANALİZİ
</div>
""", unsafe_allow_html=True)

# ======================================
# ÇOKLU FOTO
# ======================================

uploaded = st.file_uploader(
    "Maç ekran görüntüsü yükle",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

# ======================================
# TEMİZLE
# ======================================

def temizle(text):

    text = text.replace("\n", " ")
    text = text.replace("%", " ")

    return text

# ======================================
# DAKİKA BUL
# ======================================

def dakika_bul(text):

    match = re.search(r"(\\d{1,2})'", text)

    if match:
        return int(match.group(1))

    return 0

# ======================================
# SKOR BUL
# ======================================

def skor_bul(text):

    match = re.search(r"(\\d+)\\s*-\\s*(\\d+)", text)

    if match:
        return int(match.group(1)), int(match.group(2))

    return 0,0

# ======================================
# SAYILARI BUL
# ======================================

def sayilar(text):

    nums = re.findall(r'\\d+', text)

    temiz = []

    for n in nums:

        try:
            temiz.append(int(n))
        except:
            pass

    return temiz

# ======================================
# ANALİZ MOTORU
# ======================================

def analiz(
    dk,
    home_goal,
    away_goal,
    attacks,
    dangerous,
    corners
):

    toplam = home_goal + away_goal

    sonuc = {}

    # GOL
    if dangerous >= 20:

        sonuc["gol"] = (
            "🔥 GOL BASKISI ÇOK YÜKSEK",
            "green",
            87
        )

    elif dangerous >= 10:

        sonuc["gol"] = (
            "⚠️ GOL OLABİLİR",
            "yellow",
            66
        )

    else:

        sonuc["gol"] = (
            "❄️ DÜŞÜK TEMPO",
            "red",
            35
        )

    # KG
    if attacks >= 30 and toplam >= 1:

        sonuc["kg"] = (
            "✅ KG VAR YAKIN",
            "green",
            74
        )

    else:

        sonuc["kg"] = (
            "❌ KG YOK YAKIN",
            "red",
            46
        )

    # İLK YARI
    if dk <= 35 and dangerous >= 15:

        sonuc["iy"] = (
            "🚀 İY 0.5 ÜST GÜÇLÜ",
            "green",
            81
        )

    else:

        sonuc["iy"] = (
            "⚠️ İY ALT YAKIN",
            "yellow",
            58
        )

    # KORNER
    if corners >= 6:

        sonuc["korner"] = (
            "📐 KORNER BASKISI VAR",
            "green",
            79
        )

    else:

        sonuc["korner"] = (
            "📐 NORMAL KORNER",
            "yellow",
            50
        )

    return sonuc

# ======================================
# FOTOĞRAFLAR
# ======================================

if uploaded:

    for file in uploaded:

        st.markdown("---")

        image = Image.open(file)

        st.image(
            image,
            use_container_width=True
        )

        img_np = np.array(image)

        gray = cv2.cvtColor(
            img_np,
            cv2.COLOR_BGR2GRAY
        )

        text = pytesseract.image_to_string(gray)

        text = temizle(text)

        # ==================================
        # OCR
        # ==================================

        dk = dakika_bul(text)

        home_goal, away_goal = skor_bul(text)

        nums = sayilar(text)

        attacks = max(nums) if len(nums) > 0 else 0

        dangerous = nums[-2] if len(nums) >= 2 else 0

        corners = nums[-3] if len(nums) >= 3 else 0

        # ==================================
        # ANALİZ
        # ==================================

        sonuc = analiz(
            dk,
            home_goal,
            away_goal,
            attacks,
            dangerous,
            corners
        )

        # ==================================
        # OCR VERİ
        # ==================================

        st.markdown("""
        <div class="card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="blue">
        📊 OCR OKUNAN VERİLER
        </div>
        """, unsafe_allow_html=True)

        st.write(f"Dakika: {dk}")
        st.write(f"Skor: {home_goal}-{away_goal}")
        st.write(f"Atak Gücü: {attacks}")
        st.write(f"Tehlikeli Atak: {dangerous}")
        st.write(f"Korner Baskısı: {corners}")

        st.markdown("</div>", unsafe_allow_html=True)

        # ==================================
        # GOL
        # ==================================

        gol_text, gol_css, gol_prob = sonuc["gol"]

        st.markdown(f"""
        <div class="card">
            <div class="{gol_css}">
                {gol_text}
            </div>

            <br>

            <div class="info">
                Gol ihtimali: %{gol_prob}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==================================
        # KG
        # ==================================

        kg_text, kg_css, kg_prob = sonuc["kg"]

        st.markdown(f"""
        <div class="card">
            <div class="{kg_css}">
                {kg_text}
            </div>

            <br>

            <div class="info">
                KG ihtimali: %{kg_prob}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==================================
        # İY
        # ==================================

        iy_text, iy_css, iy_prob = sonuc["iy"]

        st.markdown(f"""
        <div class="card">
            <div class="{iy_css}">
                {iy_text}
            </div>

            <br>

            <div class="info">
                İlk yarı ihtimali: %{iy_prob}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==================================
        # KORNER
        # ==================================

        kor_text, kor_css, kor_prob = sonuc["korner"]

        st.markdown(f"""
        <div class="card">
            <div class="{kor_css}">
                {kor_text}
            </div>

            <br>

            <div class="info">
                Korner ihtimali: %{kor_prob}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==================================
        # OTOMATİK KUPON
        # ==================================

        st.markdown("""
        <div class="card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="blue">
        🎯 OTOMATİK KUPON
        </div>
        """, unsafe_allow_html=True)

        if gol_prob >= 80:
            st.success("CANLI GOL")

        if kg_prob >= 70:
            st.success("KG VAR")

        if iy_prob >= 75:
            st.success("İY 0.5 ÜST")

        if kor_prob >= 75:
            st.success("KORNER ÜST")

        st.markdown("</div>", unsafe_allow_html=True)

        # ==================================
        # OCR HAM VERİ
        # ==================================

        with st.expander("OCR HAM VERİ"):

            st.write(text)
