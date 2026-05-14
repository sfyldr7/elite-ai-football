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
body {
    background-color:#050816;
    color:white;
}
.big-title{
    font-size:58px;
    font-weight:bold;
    color:white;
}
.box{
    background:#0b1225;
    padding:20px;
    border-radius:15px;
    margin-top:20px;
}
.green{
    color:#00ff88;
}
.red{
    color:#ff4d4d;
}
.yellow{
    color:#ffd633;
}
.blue{
    color:#00bfff;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">⚽ ELITE AI GÖRSEL MAÇ ANALİZİ</div>', unsafe_allow_html=True)

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
            lang='eng'
        )

        all_text += text + "\n"

    st.markdown("## 📋 OCR OKUNAN VERİLER")

    st.code(all_text)

    dakika = "0"
    skor = "0-0"

    dakika_match = re.search(r'(\d{1,2})[\'`´:]?', all_text)
    skor_match = re.search(r'(\d+)\s*-\s*(\d+)', all_text)

    if dakika_match:
        dakika = dakika_match.group(1)

    if skor_match:
        skor = skor_match.group(0)

    tehlikeli_atak = 0
    atak = 0
    korner = 0
    topa_sahip = 50

    sayilar = re.findall(r'\d+', all_text)

    if len(sayilar) >= 8:
        try:
            atak = int(sayilar[4])
            tehlikeli_atak = int(sayilar[5])
            topa_sahip = int(sayilar[6])
            korner = int(sayilar[7])
        except:
            pass

    st.markdown("""
    <div class="box">
    <h1 class="blue">📊 OCR OKUNAN VERİLER</h1>
    """, unsafe_allow_html=True)

    st.write(f"### Dakika: {dakika}")
    st.write(f"### Skor: {skor}")
    st.write(f"### Atak Gücü: {atak}")
    st.write(f"### Tehlikeli Atak: {tehlikeli_atak}")
    st.write(f"### Korner Baskısı: {korner}")
    st.write(f"### Topa Sahip Olma: %{topa_sahip}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="box">
    <h1 class="green">🤖 ELITE AI ANALİZ</h1>
    """, unsafe_allow_html=True)

    if tehlikeli_atak >= 10:
        st.success("🔥 Çok yüksek baskı var. Gol ihtimali yükseliyor.")

    elif tehlikeli_atak >= 5:
        st.warning("⚠️ Baskı artıyor. Gol gelebilir.")

    else:
        st.info("⏳ Maç düşük tempoda gidiyor.")

    if korner >= 5:
        st.success("🚩 Korner baskısı yüksek.")

    if topa_sahip >= 60:
        st.success("⚽ Bir takım oyunu domine ediyor.")

    ev_gol = int(skor.split("-")[0])
    dep_gol = int(skor.split("-")[1])

    toplam_gol = ev_gol + dep_gol

    st.markdown("## 🎯 YAPAY ZEKA TAHMİNLERİ")

    if toplam_gol == 0 and dakika < "25":
        st.write("✅ İlk Yarı Alt 1.5 Mantıklı")

    if tehlikeli_atak >= 8:
        st.write("✅ KG VAR ihtimali yükseliyor")

    if korner >= 4:
        st.write("✅ Korner Üst düşünülebilir")

    if topa_sahip >= 65 and tehlikeli_atak >= 8:
        st.write("✅ Baskılı takım gol bulabilir")

    st.markdown("</div>", unsafe_allow_html=True)
