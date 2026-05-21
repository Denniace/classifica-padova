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
    geolocator = Nominatim(user_agent="padova_app_classifica_final")
    try:
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia")
        if location:
            parti = location.address.split(",")
            return f"{parti[0].strip()}, {parti[1].strip()}"
        return "📍 Indirizzo non trovato (Cerca su Google)"
    except:
        return "📍 Errore mappe"

# --- FUNZIONI DI GESTIONE DEI DATI ---
def carica_dati():
    if os.path.exists("Locali_padova.json"):
        try:
            with open("Locali_padova.json", "r", encoding="utf-8") as f:
                dati = json.load(f)
                # Ripara vecchi formati se presenti nel JSON
                for k, v in dati.items():
                    if isinstance(v, int): 
                        dati[k] = {"voti": v, "indirizzo": "📍 Via da aggiungere"}
                return dati
        except:
            return {}
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

# --- INIZIALIZZAZIONE COOKIE MANAGER (ANTI-REFRESH) ---
cookie_manager = stx.CookieManager()

# Piccola pausa strategica per permettere al browser di caricare i cookie in modo asincrono
if 'init' not in st.session_state:
    time.sleep(0.6)
    st.session_state['init'] = True
    st.rerun()

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

# Recupera lo stato del voto dal browser
ha_votato = cookie_manager.get("voto_padova_v3")

# --- PREPARAZIONE DATI PER LA TABELLA ---
lista_classifica = []
for locale, info in st.session_state.locali.items():
    if isinstance(info, dict):
        voti = info.get("voti", 1)
        indirizzo = info.get("indirizzo", "📍 Sconosciuto")
    else:
        voti = info
        indirizzo = "📍 Sconosciuto"
        
    lista_classifica.append({
        "Locale": locale,
        "Voti": voti,
        "Indirizzo": indirizzo,
        "Categoria": assegna_categoria(locale)
    })

if not lista_classifica:
    df = pd.DataFrame(columns=["Locale", "Voti", "Indirizzo", "Categoria"])
else:
    df = pd.DataFrame(lista_classifica).sort_values(by="Voti", ascending=False).reset_index(drop=True)

# --- INTERFACCIA GRAFICA ---
st.title("🍔 Il Re di Padova - Classifica Ufficiale")

# --- PODIO ESTETICO ORIGINALE ---
st.subheader("🏆 Il Podio attuale")
col1, col2, col3 = st.columns(3)
if len(df) >= 1: 
    col1.metric("🥇 1° Posto", df.iloc[0]["Locale"], f"{df.iloc[0]['Voti']} voti")
if len(df) >= 2: 
    col2.metric("🥈 2° Posto", df.iloc[1]["Locale"], f"{df.iloc[1]['Voti']} voti")
if len(df) >= 3: 
    col3.metric("🥉 3° Posto", df.iloc[2]["Locale"], f"{df.iloc[2]['Voti']} voti")

st.markdown("---")

# --- TABELLA DELLA CLASSIFICA COMPLETA ---
st.subheader("📊 Classifica Completa")
st.dataframe(df, use_container_width=True)

# --- SEZIONE AGGIUNGI LOCALE (MANUALE + AUTOMATICO) ---
st.write("---")
st.subheader("➕ Non vedi il tuo posto preferito?")
with st.form("nuovo_locale", clear_on_submit=True):
    nome_nuovo = st.text_input("Nome del locale (es. Pizzeria da Pino):")
    indirizzo_manuale = st.text_input("Indirizzo (Opzionale - lascialo vuoto per la ricerca automatica):")
    invio = st.form_submit_button("Aggiungi Locale ➕")
    
    if invio and nome_nuovo.strip():
        if nome_nuovo not in st.session_state.locali:
            # Se l'utente inserisce la via a mano, usa quella direttamente
            if indirizzo_manuale.strip():
                via = indirizzo_manuale.strip()
                st.session_state.locali[nome_nuovo] = {"voti": 1, "indirizzo": via}
                salva_dati(st.session_state.locali)
                st.success(f"Aggiunto con il tuo indirizzo: {via}")
                time.sleep(1)
                st.rerun()
            # Altrimenti prova ad interpellare le mappe in automatico
            else:
                with st.spinner("Bussando ai server delle mappe... 🗺️"):
                    via = trova_indirizzo_auto(nome_nuovo)
                    st.session_state.locali[nome_nuovo] = {"voti": 1, "indirizzo": via}
                    sal
