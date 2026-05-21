import streamlit as st
import pandas as pd
import json
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Nome del file in cui salveremo i dati sul tuo computer
FILE_DATI = "locali_padova.json"

# Inizializziamo il gestore dei cookie
cookies = EncryptedCookieManager(password="unapasswordsegretaperpadova123")
if not cookies.ready():
    st.stop()

# FUNZIONE 1: Carica i dati dal file JSON
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "Dalla Zita (Panini)": 15,
            "Caffè Pedrocchi (Storico)": 12,
            "Pizzeria Pago Pago": 9,
            "Gelateria GROM": 5
        }

# FUNZIONE 2: Salva lo stato attuale dei locali
def salva_dati(dati):
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)


# --- INIZIO APPLICAZIONE STREAMLIT ---

st.title("🍔 Il Re di Padova - Classifica Locali")
st.write("Vota i tuoi posti preferiti e stravolgi la classifica in tempo reale!")

# Inizializziamo la sessione caricando i dati dal file
if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

# Trasformiamo i dati in una classifica ordinata
df = pd.DataFrame(list(st.session_state.locali.items()), columns=['Locale', 'Voti'])
df = df.sort_values(by='Voti', ascending=False).reset_index(drop=True)


# --- SEZIONE: IL PODIO VISIVO (TOP 3) ---
st.subheader("🏆 Il Podio di Padova")
num_locali = len(df)

if num_locali > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🥇 1° Posto", value=df.iloc[0]['Locale'], delta=f"{df.iloc[0]['Voti']} voti")
    if num_locali > 1:
        with col2:
            st.metric(label="🥈 2° Posto", value=df.iloc[1]['Locale'], delta=f"{df.iloc[1]['Voti']} voti")
    if num_locali > 2:
        with col3:
            st.metric(label="🥉 3° Posto", value=df.iloc[2]['Locale'], delta=f"{df.iloc[2]['Voti']} voti")

st.markdown("---")


# --- NUOVA TABELLA COLORATA ---
st.subheader("📊 Classifica Completa")

def evidenzia_podio(row):
    if row.name == 0:
        return ['background-color: #ffd700; color: black'] * len(row)
    elif row.name == 1:
        return ['background-color: #c0c0c0; color: black'] * len(row)
    elif row.name == 2:
        return ['background-color: #cd7f32; color: black'] * len(row)
    return [''] * len(row)

df_stilizzato = df.style.apply(evidenzia_podio, axis=1)
st.dataframe(df_stilizzato, use_container_width=True)


# --- SEZIONE: AGGIUNGI UN LOCALE ---
st.subheader("➕ Non vedi il tuo posto preferito? Aggiungilo!")

with st.form("nuovo_locale_form", clear_on_submit=True):
    nuovo_nome = st.text_input("Nome del locale:")
    categoria = st.text_input("Specialità o Tipo (es. Pizza, Panini):")
    bottone_aggiungi = st.form_submit_button("Inserisci nella classifica")

    if bottone_aggiungi:
        if nuovo_nome.strip() != "":
            nome_completo = f"{nuovo_nome.strip()} ({categoria.strip()})" if categoria.strip() else nuovo_nome.strip()
            if nome_completo not in st.session_state.locali:
                st.session_state.locali[nome_completo] = 1
                salva_dati(st.session_state.locali)
                st.success(f"🎉 {nome_completo} aggiunto alla classifica!")
                st.rerun()
            else:
                st.warning("Questo locale è già presente!")
        else:
            st.error("Inserisci un nome valido.")


# --- SEZIONE: CASSETTA DELLE VOTAZIONI ---
st.subheader("🗳️ Dai il tuo voto!")
opzione_scelta = st.selectbox("Quale locale vuoi supportare?", df['Locale'])

if st.button(f"Regala un voto a: {opzione_scelta}"):
    if cookies.get("ha_votato") == "si":
        st.error("🚫 Hai già dato il tuo voto per oggi!")
    else:
        st.session_state.locali[opzione_scelta] += 1
        salva_dati(st.session_state.locali)
        cookies["ha_votato"] = "si"
        cookies.save()
        st.success(f"Grazie! Il tuo voto per {opzione_scelta} è stato registrato!")
        st.rerun()