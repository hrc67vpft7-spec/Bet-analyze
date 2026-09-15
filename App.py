import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

st.set_page_config(page_title="AI Bet Analyzer Pro", page_icon="🎯", layout="centered")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Stabilní flash model
model = genai.GenerativeModel("gemini-3.6-flash")

st.title("🎯 AI Bet Analyzer & Progrese")

# Volba režimu aplikace
rezim = st.radio("Vyber režim sázení:", ["pre-match (Předzápasová analýza)", "⚡ Live Turbo (Rychlé sázky)"])

kurz_k = 0.0

if rezim == "pre-match (Předzápasová analýza)":
    uploaded_file = st.file_uploader("Nahraj screenshot předzápasové nabídky", type=["png", "jpg", "jpeg"], key="pre")
    
    system_prompt = """
    Jsi profesionální analytik pro sportovní sázení.
    Zahrň analýzu pro všechny sporty i e-gaming.
    1. FILTR VIRTUALŮ: Vyřaď AI simulace a arkádové rychlé režimy.
    2. REÁLNÉ ZÁPASY: Zaměř se na ten s nejjasnějším favoritem.
    3. HLOUBKOVÝ ROZBOR: Zhodnoť formu, Tier týmu, únavu.
    4. VÝBĚR: Vyber POUZE JEDEN tým.

    **Analýza:** [Tvůj detailní textový rozbor]
    **Největší favorit:** [Jméno týmu]

    [KURZ_ZACATEK]
    1.55
    [KURZ_KONEC]
    """
    
    if uploaded_file and st.button("Spustit hloubkovou analýzu"):
        with st.spinner("AI analyzuje zápasy a kurzy..."):
            try:
                image = Image.open(uploaded_file)
                response = model.generate_content([system_prompt, image])
                text_odpovedi = response.text
                
                cisty_text = re.sub(r'\[KURZ_ZACATEK\].*?\[KURZ_KONEC\]', '', text_odpovedi, flags=re.DOTALL)
                st.markdown(cisty_text)
                
                kurz_match = re.search(r'\[KURZ_ZACATEK\]\s*([0-9.]+)\s*\[KURZ_KONEC\]', text_odpovedi)
                if kurz_match:
                    kurz_k = float(kurz_match.group(1))
                    st.success(f"🔍 Načtený kurz: **{kurz_k}**")
            except Exception as e:
                st.error(f"Chyba: {e}")

else:
    live_volba = st.radio("Live vstup:", ["📸 Screenshot live kurzu", "⌨️ Ruční zadání kurzu"])
    
    if live_volba == "📸 Screenshot live kurzu":
        uploaded_file_live = st.file_uploader("Nahraj live screenshot", type=["png", "jpg", "jpeg"], key="live")
        if uploaded_file_live and st.button("🔥 Pálit live analýzu"):
            with st.spinner("Blesková live analýza..."):
                try:
                    system_prompt_live = """
                    Jsi rychlý live sázkařský asistent. Zanalyzuj screenshot live zápasu.
                    1. Ignoruj virtuály.
                    2. Vyber jasného favorita.
                    Odpověz stručně:
                    **Doporučení:** [Tým / Sázka]
                    [KURZ_ZACATEK]
                    [Číselný kurz]
                    [KURZ_KONEC]
                    """
                    image = Image.open(uploaded_file_live)
                    response = model.generate_content([system_prompt_live, image])
                    text_odpovedi = response.text
                    
                    cisty_text = re.sub(r'\[KURZ_ZACATEK\].*?\[KURZ_KONEC\]', '', text_odpovedi, flags=re.DOTALL)
                    st.markdown(cisty_text)
                    
                    kurz_match = re.search(r'\[KURZ_ZACATEK\]\s*([0-9.]+)\s*\[KURZ_KONEC\]', text_odpovedi)
                    if kurz_match:
                        kurz_k = float(kurz_match.group(1))
                except Exception as e:
                    st.error(f"Chyba: {e}")
    else:
        kurz_k = st.number_input("Zadej live kurz ručně:", min_value=1.01, max_value=50.0, value=1.50, step=0.01)

st.markdown("---")
st.markdown("### 💰 Kalkulačka progrese")
je_progrese = st.checkbox("Chci dohnat předchozí prohraný tiket")

if je_progrese:
    v_castka = st.number_input("Zadej očekávanou výhru z minulého tiketu ($):", min_value=0.1, step=1.0, format="%.2f")
    if kurz_k > 1.0:
        vklad_s = v_castka / (kurz_k - 1)
        st.info(f"### 💸 Nutný vklad (S): **{vklad_s:.2f} $** při kurzu **{kurz_k}**")
    else:
        st.warning("Zatím není načtený nebo zadaný platný kurz pro výpočet progrese.")
