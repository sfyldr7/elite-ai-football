import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re

st.set_page_config(
    page_title="ELITE AI",
    layout="wide"
)

st.markdown("""
<style>
body{
    background:#050816;
    color:white;
}

.big-title{
    font-size:60px;
    font-weight:bold;
    color:white;
}

.box{
    background:#0b1225;
    padding:20px;
    border-radius:20px;
    margin-top:20px;
}

.green{
    color:#00ff88;
}

.red{
    color:#ff4d4d;
}

.blue{
    color:#00bfff;
}

.yellow{
    color:#ffd633;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="big-title">
⚽ ELITE AI GÖRSEL MAÇ ANALİZİ
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Maç ekran görüntüsü yükle",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:

    all_text = ""

    for uploaded_file in uploaded_files:

        image = Image.open(uploaded_file)

        st.image(image, use_container_width=True)

        img_np = np.array(image)

        gray = cv2.cvtColor(
            img_np,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.threshold(
            gray,
            150,
            255,
            cv2.THRESH_BINARY
        )[1]

        custom_config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(
            gray,
            config=custom_config,
            lang='eng+tur'
        )

        all_text += text + "\n"

    st.markdown("""
    <div class="box">
    <h1 class="blue">📋 OCR ÇIKTISI</h1>
    """, unsafe_allow_html=True)

    st.code(all_text)

    st.markdown("</div>", unsafe_allow_html=True)

    dakika = "0"
    skor = "0-0"

    dakika_match = re.search(r'(\d{1,2})[\'`´:]?', all_text)
    skor_match = re.search(r'(\d+)\s*-\s*(\d+)', all_text)

    if dakika_match:
        dakika = dakika_match.group(1)

    if skor_match:
        skor = skor_match.group(0)

    atak = 0
    tehlikeli_atak = 0
    topa_sahip = 50
    korner = 0

    lines = all_text.splitlines()

    for line in lines:

        line_lower = line.lower()

        nums = re.findall(r'\d+', line)

        if (
            "atak" in line_lower
            and "tehlikeli" not in line_lower
            and len(nums) >= 2
        ):
            atak = max([int(x) for x in nums])

        if (
            "tehlikeli" in line_lower
            and len(nums) >= 2
        ):
            tehlikeli_atak = max([int(x) for x in nums])

        if "%" in line_lower and len(nums) >= 2:
            topa_sahip = max([int(x) for x in nums])

        if "korner" in line_lower and len(nums) >= 1:
            korner = max([int(x) for x in nums])

    st.markdown("""
    <div class="box">
    <h1 class="green">📊 OCR OKUNAN VERİLER</h1>
    """, unsafe_allow_html=True)

    st.write(f"### ⏱ Dakika: {dakika}")
    st.write(f"### ⚽ Skor: {skor}")
    st.write(f"### 🔥 Atak Gücü: {atak}")
    st.write(f"### 🚨 Tehlikeli Atak: {tehlikeli_atak}")
    st.write(f"### 🚩 Korner Baskısı: {korner}")
    st.write(f"### 📈 Topa Sahip Olma: %{topa_sahip}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="box">
    <h1 class="yellow">🤖 ELITE AI TAHMİN</h1>
    """, unsafe_allow_html=True)

    ev_gol = int(skor.split("-")[0])
    dep_gol = int(skor.split("-")[1])

    toplam_gol = ev_gol + dep_gol

    if tehlikeli_atak >= 10:
        st.success("🔥 Çok ciddi baskı var. Gol ihtimali yüksek.")

    elif tehlikeli_atak >= 5:
        st.warning("⚠️ Baskı yükseliyor. Gol gelebilir.")

    else:
        st.info("⏳ Maç düşük tempoda ilerliyor.")

    if korner >= 5:
        st.success("🚩 Korner üst için uygun tempo.")

    if topa_sahip >= 60:
        st.success("⚽ Bir takım oyunu domine ediyor.")

    st.markdown("## 🎯 BAHİS ÖNERİLERİ")

    if toplam_gol == 0 and int(dakika) < 25:
        st.write("✅ İlk Yarı Alt 1.5")

    if tehlikeli_atak >= 8:
        st.write("✅ KG VAR değerlendirilebilir")

    if toplam_gol <= 1 and int(dakika) < 35:
        st.write("✅ Maç Sonu Üst 1.5 düşünülebilir")

    if korner >= 4:
        st.write("✅ Korner Üst değerlendirilebilir")

    if topa_sahip >= 65 and tehlikeli_atak >= 8:
        st.write("✅ Baskılı takım gol bulabilir")

    if tehlikeli_atak <= 3 and int(dakika) > 30:
        st.write("✅ Alt seçenekleri mantıklı")

    st.markdown("</div>", unsafe_allow_html=True)
