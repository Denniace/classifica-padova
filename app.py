import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
import time
from geopy.geocoders import Nominatim

# Configurazione della Pagina Streamlit
st.set_page_config(page_title="Il Re di Padova", page_icon="🍕", layout="wide")

# --- FUNZIONE RICERCA AUTOMATICA INDIRIZZO ---
def trova_indirizzo_auto(nome_locale):
    geolocator = Nominatim(user_agent="padova_app_classifica_final_v4")
    try:
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia")
        if location:
            parti = location.address.split(",")
            # Prende via e numero civico se disponibili
            return f"{parti[0].strip()}, {parti[1].strip()}"
        return "📍 Indirizzo non trovato (Da aggiungere a mano)"
    except:
        return "📍 Mappa non raggiungibile"

# --- FUNZIONI DI GESTIONE DEI DATI ---
def carica_dati():
    if os.path.exists("Locali_padova.json"):
        try:
            with open("Locali_padova.json", "r", encoding="utf-8") as f:
                dati = json.load(f)
                
                # AUTO-RIPARAZIONE: Se il JSON è nel vecchio formato, lo converte al volo
                for k, v in list(dati.items()):
                    if isinstance(v, int) or isinstance(v, float): 
                        dati[k] = {"voti": int(v), "indirizzo": "📍 Sconosciuto (Vecchio dato)"}
                return dati
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
    if "osteria" in n or "bacaro" in n or "anfora" in n or "capo" in n or "tadi" in n: return "🍷 Osterie & Storici"
    if "gelateria" in n or "gelato" in n or "grom" in n or "romana" in n: return "🍦 Gelaterie"
    return "✨ Altro"

# --- INIZIALIZZAZIONE COOKIE MANAGER (ANTI-CHEAT) ---
cookie_manager = stx.CookieManager()

# Pausa tecnica per dare tempo al browser di caricare i cookie in modo sicuro
if 'init' not in st.session_state:
    time.sleep(0.6)
    st.session_state['init'] = True
    st.rerun()

if 'locali' not in st.session_state:
    st.session_state.
