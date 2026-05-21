import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
import time
from geopy.geocoders import Nominatim

# Configurazione Pagina
st.set_page_config(page_title="Il Re di Padova", page_icon="🍕", layout="wide")

# --- FUNZIONE RICERCA INDIRIZZO ---
def trova_indirizzo_auto(nome_locale):
    geolocator = Nominatim(user_agent="padova_app_classifica_final")
    try:
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia")
        if location:
            parti = location.address.split(",")
            return f"{parti[0].strip()}, {parti[1].strip()}"
        return "📍 Indirizzo non trovato (Cerca su Google)"
    except:
        return "📍 Errore mappe"

# --- GESTIONE DATI ---
def carica_dati():
    if os.path.exists("Locali_padova.json"):
        with open("Locali_padova.json", "r", encoding="utf-8") as f:
            dati = json.load(f)
            # Converte vecchi formati se necessario
            for k, v in dati.items():
                if isinstance(v, int): dati[k] = {"voti": v, "indirizzo": "📍 Via da aggiungere"}
            return dati
    return {}

def salva_dati(dati):
    with open("Locali_padova.json", "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

def assegna_categoria(nome):
    n = nome.lower()
    if "panini" in n or "zita" in n: return "🥪 Panini"
    if "pizza" in n or "pizzeria" in n or "kebab" in n: return "🍕 Pizza & Kebab"
    if "osteria" in n or "bacaro" in n or "anfora" in n or "capo" in n or "tadi" in n: return "🍷 Osterie"
    if "gelateria" in n or "gelato" in n: return "🍦 Gelaterie"
    return "✨ Altro"

# --- INIZIALIZZAZIONE ---
cookie_manager = stx.CookieManager()

# Attesa per i cookie (Anti-Refresh)
if 'init' not in st.session_state:
    time.sleep(0.5)
    st.session_state['init'] = True
    st.rerun()

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

ha_votato = cookie_manager.get("voto_padova_v3")

# Preparazione Classifica
lista = []
for locale, info in st.session_state.locali.items():
    lista.append({
        "Locale": locale,
        "Voti": info.get("voti", 0),
        "Indirizzo": info.get("indirizzo", "📍 Sconosciuto"),
        "Categoria": assegna_categoria(locale)
    })

df = pd.DataFrame(lista).sort_values(by="Voti", ascending=False).reset_index(drop=True)

# --- INTERFACCIA ---
st.title("🍔 Il Re di Padova - Classifica Ufficiale")

# --- PODIO (ESTETICA ORIGINALE) ---
st.subheader("🏆 Il Podio attuale")
col1, col2, col3 = st.columns(3)
if len(df) >= 1: col1.metric("🥇 1° Posto", df.iloc[0]["Locale"], f"{df.iloc[0]['Voti']} voti")
if len(df) >= 2: col2.metric("🥈 2° Posto", df.iloc[1]["Locale"], f"{df.iloc[1]['Voti']} voti")
if len(df) >= 3: col3.metric("🥉 3° Posto", df.iloc[2]["Locale"], f"{df.iloc[2]['Voti']} voti")

st.markdown("---")

# --- TABELLA ---
st.subheader("📊 Classifica Completa")
st.dataframe(df, use_container_width=True)

# --- AGGIUNGI LOCALE (CON RICERCA AUTOMATICA) ---
st.write("---")
st.subheader("➕ Non vedi il tuo posto preferito?")
with st.form("nuovo_locale", clear_on_submit=True):
    nome_nuovo = st.text_input("Nome del locale (es. Pizzeria da Pino):")
    invio = st.form_submit_button("Trova indirizzo e Aggiungi 🔍")
    
    if invio and nome_nuovo.strip():
        if nome_nuovo not in st.session_state.locali:
            with st.spinner("Bussando ai server delle mappe... 🗺️"):
                via = trova_indirizzo_auto(nome_nuovo)
                st.session_state.locali[nome_nuovo] = {"voti": 1, "indirizzo": via}
                salva_dati(st.session_state.locali)
                st.success(f"Aggiunto! Indirizzo trovato: {via}")
                time.sleep(1)
                st.rerun()
        else:
            st.warning("Locale già in lista!")

# --- VOTAZIONE ---
st.write("---")
st.subheader("🗳️ Dai il tuo voto")

if ha_votato == "true":
    st.info("🚫 Hai già votato oggi. Torna domani!")
else:
    scelta = st.selectbox("Scegli chi supportare:", df["Locale"].tolist())
    if st.button("Regala un voto! 🗳️"):
        st.session_state.locali[scelta]["voti"] += 1
        salva_dati(st.session_state.locali)
        cookie_manager.set("voto_padova_v3", "true", max_age=86400)
        st.success(f"Voto per {scelta} registrato!")
        time.sleep(1)
        st.rerun()
