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

# --- FUNZIONE RICERCA INDIRIZZO ---
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
            else:
                parti = location.address.split(",")
                if len(parti) > 2:
                    return f"{parti[1].strip()}, {parti[2].strip()}"
                return location.address.split(",")[0].strip()
        return "📍 Indirizzo non trovato (Da aggiungere a mano)"
    except:
        return "📍 Mappa non raggiungibile"

# --- GESTIONE DATI (Nessun dato andrà perso) ---
def carica_dati():
    if os.path.exists("Locali_padova.json"):
        try:
            with open("Locali_padova.json", "r", encoding="utf-8") as f:
                dati = json.load(f)
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

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

# --- SISTEMA DI BLOCCO VOTI DOPPIO ---
# 1. Controllo di sessione (immediato)
if 'ha_votato_sessione' not in st.session_state:
    st.session_state.ha_votato_sessione = False

# 2. Controllo Cookie (a lungo termine per bloccare il refresh)
cookie_voto = cookie_manager.get("blocco_voti_v7")

# --- PREPARAZIONE TABELLA ---
lista_classifica = []
for locale, info in st.session_state.locali.items():
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

df = pd.DataFrame(lista_classifica) if lista_classifica else pd.DataFrame(columns=["Locale", "Voti", "Indirizzo", "Categoria"])
if not df.empty:
    df = df.sort_values(by="Voti", ascending=False).reset_index(drop=True)

# --- INTERFACCIA GRAFICA ---
st.title("🍔 Il Re di Padova - Classifica Ufficiale")

st.subheader("🏆 Il Podio attuale")
col1, col2, col3 = st.columns(3)
if len(df) >= 1: col1.metric("🥇 1° Posto", df.iloc[0]["Locale"], f"{df.iloc[0]['Voti']} voti")
if len(df) >= 2: col2.metric("🥈 2° Posto", df.iloc[1]["Locale"], f"{df.iloc[1]['Voti']} voti")
if len(df) >= 3: col3.metric("🥉 3° Posto", df.iloc[2]["Locale"], f"{df.iloc[2]['Voti']} voti")

st.markdown("---")

st.subheader("📊 Classifica e Posizioni")
st.dataframe(df, use_container_width=True)

# --- AGGIUNTA LOCALE ---
st.write("---")
st.subheader("➕ Non vedi il tuo posto preferito?")
with st.form("nuovo_locale", clear_on_submit=True):
    nome_nuovo = st.text_input("Nome esatto del locale:")
    indirizzo_manuale = st.text_input("Indirizzo (Opzionale - lascialo vuoto per cercarlo in automatico):")
    invio = st.form_submit_button("Aggiungi Locale ➕")
    
    if invio and nome_nuovo.strip():
        if nome_nuovo not in st.session_state.locali:
            if indirizzo_manuale.strip():
                via = indirizzo_manuale.strip()
            else:
                with st.spinner("Cerco l'indirizzo esatto sulle mappe... 🗺️"):
                    via = trova_indirizzo_auto(nome_nuovo)
                    
            st.session_state.locali[nome_nuovo] = {"voti": 1, "indirizzo": via}
            salva_dati(st.session_state.locali)
            st.success(f"Aggiunto con successo! Indirizzo assegnato: {via}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Questo locale è già presente nella lista!")

# --- SEZIONE VOTAZIONE PROTETTA ---
st.write("---")
st.subheader("🗳️ Dai il tuo voto")

# Il blocco scatta se il cookie è presente OPPURE se hai votato in questa sessione aperta
if cookie_voto == "vero" or st.session_state.ha_votato_sessione:
    st.error("🚫 Hai già votato! Non puoi esprimere altri voti per oggi dal tuo dispositivo.")
else:
    if not df.empty:
        scelta = st.selectbox("Seleziona il locale che vuoi supportare:", df["Locale"].tolist())
        if st.button("Regala un voto! 🗳️"):
            # 1. Attiva subito il blocco visivo per questa sessione
            st.session_state.ha_votato_sessione = True
            
            # 2. Aggiorna i dati nel database JSON
            st.session_state.locali[scelta]["voti"] += 1
            salva_dati(st.session_state.locali)
            
            # 3. Manda l'ordine al browser di salvare il cookie per 24h
            cookie_manager.set("blocco_voti_v7", "vero", max_age=86400)
            
            st.success(f"🎉 Fantastico! Il tuo voto per '{scelta}' è stato registrato.")
            
            # 4. TRUCCO CHIAVE: Aspettiamo 1.5 secondi prima di ricaricare la pagina 
            # affinché il browser faccia in tempo a salvare fisicamente il cookie.
            time.sleep(1.5)
            st.rerun()
    else:
        st.write("La lista è vuota. Aggiungi un ristorante qui sopra per abilitare le votazioni!")
