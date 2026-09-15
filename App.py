import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

st.set_page_config(page_title="AI Bet Analyzer", page_icon="🎯", layout="centered")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Čistý název modelu bez neviditelných znaků
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🎯 AI Bet Analyzer & Kalkulačka")

uploaded_file = st.file_uploader("Nahraj screenshot kurzů", type=["png", "jpg", "jpeg"])

st.markdown("### 💰 Kalkulačka progrese")
je_progrese = st.checkbox("Chci dohnat předchozí prohraný tiket")

v_castka = 0.0
if je_progrese:
    v_castka = st.number_input("Zadej očekávanou výhru z minulého tiketu ($):", min_value=0.1, step=1.0, format="%.2f")

system_prompt = """
Jsi profesionální analytik pro sportovní sázení a e-sporty.
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
                st.success(f"🔍 Načtený kurz pro výpočet: **{kurz_k}**")
                if je_progrese and v_castka > 0:
                    if kurz_k > 1.0:
                        vklad_s = v_castka / (kurz_k - 1)
                        st.info(f"### 💸 Nutný vklad (S): **{vklad_s:.2f} $**")
                    else:
                        st.error("Kurz musí být vyšší než 1.0!")
            else:
                st.warning("Nenalezen žádný vhodný kurz.")
        except Exception as e:
            st.error(f"Došlo k chybě: {e}")
