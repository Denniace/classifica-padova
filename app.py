import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
import time
from geopy.geocoders import Nominatim

# Configurazione della Pagina
st.set_page_config(page_title="Il Re di Padova", page_icon="🍕", layout="wide")

# --- FUNZIONE RICERCA AUTOMATICA INDIRIZZO ---
def trova_indirizzo_auto(nome_locale):
    geolocator = Nominatim(user_agent="padova_app_classifica")
    try:
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia")
        if location:
            parti = location.address.split(",")
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
                
                # AUTO-RIPARAZIONE JSON VECCHIO
                for k, v in list(dati.items()):
                    if isinstance(v, (int, float)): 
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

# --- INIZIALIZZAZIONE COOKIE MANAGER E SESSION STATE ---
cookie_manager = stx.CookieManager()

if 'init' not in st.session_state:
    time.sleep(0.5)
    st.session_state['init'] = True
    st.rerun()

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

ha_votato = cookie_manager.get("voto_padova_dispositivo_v5")

# --- PREPARAZIONE DATI PER LA TABELLA ---
lista_classifica = []
for locale, info in st.session_state.locali.items():
    # Prevenzione errori nel caso info sia ancora un numero (vecchio formato)
    if isinstance(info, (int, float)):
        voti = int(info)
        indirizzo = "📍 Sconosciuto (Vecchio dato)"
    else:
        voti = info.get("voti", 1)
        indirizzo = info.get("indirizzo", "📍 Sconosciuto")
        
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

# --- IL PODIO VISIVO ---
st.subheader("🏆 Il Podio attuale")
col1, col2, col3 = st.columns(3)
if len(df) >= 1: col1.metric("🥇 1° Posto", df.iloc[0]["Locale"], f"{df.iloc[0]['Voti']} voti")
if len(df) >= 2: col2.metric("🥈 2° Posto", df.iloc[1]["Locale"], f"{df.iloc[1]['Voti']} voti")
if len(df) >= 3: col3.metric("🥉 3° Posto", df.iloc[2]["Locale"], f"{df.iloc[2]['Voti']} voti")

st.markdown("---")

# --- TABELLA DELLA CLASSIFICA COMPLETA ---
st.subheader("📊 Classifica e Posizioni")
st.dataframe(df, use_container_width=True)

# --- SEZIONE AGGIUNGI LOCALE ---
st.write("---")
st.subheader("➕ Non vedi il tuo posto preferito?")
with st.form("nuovo_locale", clear_on_submit=True):
    nome_nuovo = st.text_input("Nome esatto del locale (es. Ristorante Antonio Ferrari):")
    indirizzo_manuale = st.text_input("Indirizzo (Opzionale - lascialo vuoto per cercarlo in automatico):")
    invio = st.form_submit_button("Aggiungi Locale ➕")
    
    if invio and nome_nuovo.strip():
        if nome_nuovo not in st.session_state.locali:
            # Se l'utente scrive l'indirizzo a mano
            if indirizzo_manuale.strip():
                via = indirizzo_manuale.strip()
            # Altrimenti cerca in automatico
            else:
                with st.spinner("Cerco l'indirizzo sulle mappe di Padova... 🗺️"):
                    via = trova_indirizzo_auto(nome_nuovo)
                    
            st.session_state.locali[nome_nuovo] = {"voti": 1, "indirizzo": via}
            salva_dati(st.session_state.locali)
            st.success(f"Aggiunto con successo! Indirizzo: {via}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Questo locale è già presente nella lista!")

# --- SEZIONE VOTAZIONE CON BLOCCO DISPOSITIVO ---
st.write("---")
st.subheader("🗳️ Dai il tuo voto")

if ha_votato == "true":
    st.error("🚫 Hai già votato da questo dispositivo! Non puoi esprimere altri voti per oggi.")
else:
    if not df.empty:
        scelta = st.selectbox("Seleziona il locale che vuoi supportare:", df["Locale"].tolist())
        if st.button("Regala un voto! 🗳️"):
            # Incrementa il voto
            st.session_state.locali[scelta]["voti"] += 1
            salva_dati(st.session_state.locali)
            
            # Salva il cookie sul browser dell'utente (scade dopo 24 ore)
            cookie_manager.set("voto_padova_dispositivo_v5", "true", max_age=86400)
            
            st.success(f"🎉 Fantastico! Il tuo voto per '{scelta}' è stato registrato.")
            time.sleep(1)
            st.rerun()
    else:
        st.write("La lista è vuota. Aggiungi un ristorante qui sopra per abilitare le votazioni!")
