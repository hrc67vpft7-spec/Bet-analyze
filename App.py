import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

st.set_page_config(page_title="AI Bet Analyzer", page_icon="🎯", layout="centered")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Model, který po nás Google chce přímo v chybové hlášce
model = genai.GenerativeModel("gemini-3.6-flash")

st.title("🎯 AI Bet Analyzer & Kalkulacka")

uploaded_file = st.file_uploader("Nahraj screenshot kurzu", type=["png", "jpg", "jpeg"])

st.markdown("### 💰 Kalkulacka progrese")
je_progrese = st.checkbox("Chci dohnat predchozi prohrany tiket")
v_castka = 0.0
if je_progrese:
    v_castka = st.number_input("Zadej ocekavanou vyhru z minuleho tiketu ($):", min_value=0.1, step=1.0, format="%.2f")

system_prompt = """
Jsi profesionalni analytik pro sportovni sazeni.
1. FILTR VIRTUALU: Vyrad AI simulace a arkadove rezimy.
2. REALNE ZAPASY: Zamer se na zapas s nejjasnejsim favoritem.
3. VYBER: Vyber POUZE JEDEN tym.

**Analyza:** [Tvuj rozbor]
**Nejvetsi favorit:** [Jmeno tymu]

[KURZ_ZACATEK]
1.55
[KURZ_KONEC]
"""

if uploaded_file and st.button("Spustit hloubkovou analyzu"):
    with st.spinner("AI analyzuje zapasy a kurzy..."):
        try:
            image = Image.open(uploaded_file)
            response = model.generate_content([system_prompt, image])
            text_odpovedi = response.text
            
            cisty_text = re.sub(r'\[KURZ_ZACATEK\].*?\[KURZ_KONEC\]', '', text_odpovedi, flags=re.DOTALL)
            st.markdown(cisty_text)
            
            kurz_match = re.search(r'\[KURZ_ZACATEK\]\s*([0-9.]+)\s*\[KURZ_KONEC\]', text_odpovedi)
            
            if kurz_match:
                kurz_k = float(kurz_match.group(1))
                st.success(f"🔍 Nacteny kurz pro vypocet: **{kurz_k}**")
                if je_progrese and v_castka > 0:
                    if kurz_k > 1.0:
                        vklad_s = v_castka / (kurz_k - 1)
                        st.info(f"### 💸 Nutny vklad (S): **{vklad_s:.2f} $**")
                    else:
                        st.error("Kurz musi byt vyssi nez 1.0!")
            else:
                st.warning("Nenalezen zadny vhodny kurz.")
        except Exception as e:
            st.error(f"Doslo k chybe: {e}")
