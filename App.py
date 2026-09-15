import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# Nastavení vzhledu aplikace
st.set_page_config(page_title="AI Bet Analyzer", page_icon="🎯", layout="centered")

# Bezpečné načtení API klíče
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Inicializace AI modelu (vybíráme Flash pro rychlost a schopnost číst obrázky)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🎯 AI Bet Analyzer & Kalkulačka")

# 1. Nahrání obrázku
uploaded_file = st.file_uploader("Nahraj screenshot kurzů", type=["png", "jpg", "jpeg"])

# 2. Nastavení progresivní sázky
st.markdown("### 💰 Kalkulačka progrese")
je_progrese = st.checkbox("Chci dohnat předchozí prohraný tiket")

v_castka = 0.0
if je_progrese:
    v_castka = st.number_input("Zadej očekávanou výhru z minulého tiketu ($):", min_value=0.1, step=1.0, format="%.2f")

# 3. Super-Prompt pro AI
system_prompt = """
Jsi profesionální analytik pro sportovní sázení a e-sporty s mnohaletou praxí. Tvým úkolem je analyzovat screenshot sázkové nabídky.
Zahrň analýzu pro všechny sporty (fotbal, tenis, hokej, basketbal, MMA atd.) i e-gaming (CS2, Dota 2, LoL, Valorant).

PRAVIDLA ANALÝZY:
1. FILTR VIRTUALŮ: Okamžitě identifikuj a vyřaď všechny AI simulace (např. eBasketball CPU vs CPU, CS2 Decoy Major, FIFA simulace) a arkádové rychlé režimy (H2H 2x2, zkrácené mapy). Varuj uživatele, že jde o loterii.
2. REÁLNÉ ZÁPASY: Pokud najdeš reálné zápasy profi týmů/hráčů, zaměř se na ten s nejjasnějším favoritem.
3. HLOUBKOVÝ ROZBOR: Stručně zhodnoť formu, Tier týmu (zda jde o top světovou úroveň nebo slabší regionální ligu), historickou dominanci, možnou únavu (pokud hrají více zápasů denně) a statistický předpoklad výhry.
4. VÝBĚR: Vyber POUZE JEDEN tým (největší jistotu z celé obrazovky).

TVŮJ VÝSTUP MUSÍ VYPADAT PŘESNĚ TAKTO (dodrž strukturu):
**Analýza:** [Tvůj detailní textový rozbor týmů na obrazovce]
**Největší favorit:** [Jméno týmu]

[KURZ_ZACATEK]
1.55
[KURZ_KONEC]
(Poznámka: Číslo mezi značkami musí být čistě desetinné číslo kurzu s tečkou, na který se má vsadit).
"""

if uploaded_file and st.button("Spustit hloubkovou analýzu"):
    with st.spinner("AI analyzuje zápasy a kurzy..."):
        try:
            # Přečtení obrázku
            image = Image.open(uploaded_file)
            
            # Odeslání do Gemini
            response = model.generate_content([system_prompt, image])
            text_odpovedi = response.text
            
            # Extrakce textu pro uživatele (odstranění značek s kurzem pro hezčí vzhled)
            cisty_text = re.sub(r'\[KURZ_ZACATEK\].*?\[KURZ_KONEC\]', '', text_odpovedi, flags=re.DOTALL)
            st.markdown(cisty_text)
            
            # Extrakce kurzu pro kalkulačku
            kurz_match = re.search(r'\[KURZ_ZACATEK\]\s*([0-9.]+)\s*\[KURZ_KONEC\]', text_odpovedi)
            
            if kurz_match:
                kurz_k = float(kurz_match.group(1))
                st.success(f"🔍 Načtený kurz pro výpočet: **{kurz_k}**")
                
                # Výpočet progrese
                if je_progrese and v_castka > 0:
                    if kurz_k > 1.0:
                        vklad_s = v_castka / (kurz_k - 1)
                        st.info(f"### 💸 Nutný vklad (S): **{vklad_s:.2f} $**")
                        st.write(f"Vzorec: S = {v_castka} / ({kurz_k} - 1)")
                    else:
                        st.error("Kurz musí být vyšší než 1.0!")
            else:
                st.warning("Na obrázku nebyl nalezen žádný vhodný kurz pro reálný zápas.")
                
        except Exception as e:
            st.error(f"Došlo k chybě: {e}")
