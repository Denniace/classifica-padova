import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
import time
from geopy.geocoders import Nominatim

# --- CONFIGURAZIONE DELLA PAGINA (Deve essere la prima istruzione) ---
st.set_page_config(page_title="Il Re di Padova", page_icon="🍕", layout="wide")

# --- INIEZIONE PWA ---
st.markdown("""
    <link rel="manifest" href="https://raw.githubusercontent.com/Denniace/classifica-padova/main/manifest.json">
    <meta name="theme-color" content="#0E1117">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE COOKIE MANAGER ---
cookie_manager = stx.CookieManager(key="gestore_cookie_padova")

# --- FUNZIONI ---
def trova_indirizzo_auto(nome_locale):
    geolocator = Nominatim(user_agent="padova_king_v7")
    try:
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia", addressdetails=True)
        if location:
            addr = location.raw.get('address', {})
            via = addr.get('road') or addr.get('pedestrian') or addr.get('path') or addr.get('square')
            civico = addr.get('house_number', '')
            if via:
                return f"{via}, {civico}".strip(", ") if civico else via
        return "📍 Indirizzo non trovato"
    except:
        return "📍 Mappa non raggiungibile"

def carica_dati():
    if os.path.exists("Locali_padova.json"):
        try:
            with open("Locali_padova.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salva_dati(dati):
    with open("Locali_padova.json", "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

def assegna_categoria(nome):
    n = nome.lower()
    if "panini" in n or "zita" in n: return "🥪 Panini & Snack"
    if "pizza" in n or "pizzeria" in n or "kebab" in n: return "🍕 Pizza & Kebab"
    if "osteria" in n or "bacaro" in n or "anfora" in n or "tadi" in n: return "🍷 Osterie & Storici"
    if "gelateria" in n or "gelato" in n: return "🍦 Gelaterie"
    return "✨ Altro"

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

# --- INTERFACCIA ---
st.title("🍔 Il Re di Padova - Classifica Ufficiale")

# Logica Voti
cookie_voto = cookie_manager.get("blocco_voti_v7")
if 'ha_votato_sessione' not in st.session_state:
    st.session_state.ha_votato_sessione = False

lista_classifica = []
for locale, info in st.session_state.locali.items():
    lista_classifica.append({
        "Locale": locale,
        "Voti": info.get("voti", 1),
        "Indirizzo": info.get("indirizzo", "📍 Sconosciuto"),
        "Categoria": assegna_categoria(locale)
    })

df = pd.DataFrame(lista_classifica) if lista_classifica else pd.DataFrame(columns=["Locale", "Voti", "Indirizzo", "Categoria"])
if not df.empty:
    df = df.sort_values(by="Voti", ascending=False).reset_index(drop=True)

st.subheader("📊 Classifica")
st.dataframe(df, use_container_width=True)

# Votazione
if cookie_voto == "vero" or st.session_state.ha_votato_sessione:
    st.error("🚫 Hai già votato!")
else:
    if not df.empty:
        scelta = st.selectbox("Vota il tuo preferito:", df["Locale"].tolist())
        if st.button("Regala un voto! 🗳️"):
            st.session_state.ha_votato_sessione = True
            st.session_state.locali[scelta]["voti"] += 1
            salva_dati(st.session_state.locali)
            cookie_manager.set("blocco_voti_v7", "vero", max_age=86400)
            st.rerun()
