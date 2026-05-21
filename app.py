import streamlit as st
import pandas as pd
import json
import os
import extra_streamlit_components as stx
from geopy.geocoders import Nominatim

FILE_DATI = "locali_padova.json"

# --- FUNZIONE MAGICA: CERCA L'INDIRIZZO ONLINE ---
def trova_indirizzo(nome_locale):
    # Diciamo alle mappe chi siamo per non farsi bloccare
    geolocator = Nominatim(user_agent="padova_app_classifica_re")
    try:
        # Cerchiamo il locale aggiungendo "Padova" per aiutare il motore di ricerca
        location = geolocator.geocode(f"{nome_locale}, Padova, Italia")
        if location:
            # OpenStreetMap restituisce indirizzi lunghissimi. Prendiamo solo la via principale.
            parti_indirizzo = location.address.split(",")
            indirizzo_breve = f"{parti_indirizzo[0].strip()}, {parti_indirizzo[1].strip()}" if len(parti_indirizzo) > 1 else location.address
            return indirizzo_breve
        else:
            return "📍 Indirizzo non trovato (Cerca su Google)"
    except:
        return "📍 Errore di connessione alle mappe"

# --- FUNZIONI DI SALVATAGGIO ---
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r", encoding="utf-8") as f:
            dati_grezzi = json.load(f)
            # Sistema di sicurezza: se il JSON è vecchio (solo voti), lo aggiorniamo al nuovo formato
            dati_aggiornati = {}
            for locale, valore in dati_grezzi.items():
                if isinstance(valore, int): 
                    dati_aggiornati[locale] = {"voti": valore, "indirizzo": "📍 Sconosciuto (Vecchio dato)"}
                else:
                    dati_aggiornati[locale] = valore
            return dati_aggiornati
    else:
        return {
            "Dalla Zita (Panini)": {"voti": 15, "indirizzo": "Via Gorizia, 12"},
            "Caffè Pedrocchi (Storico)": {"voti": 12, "indirizzo": "Via VIII Febbraio, 15"},
            "Pizzeria Pago Pago": {"voti": 9, "indirizzo": "Via Galileo Galilei, 59"}
        }

def salva_dati(dati):
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

def assegna_categoria(nome):
    nome_lower = nome.lower()
    if "panini" in nome_lower or "zita" in nome_lower or "snack" in nome_lower: return "🥪 Panini & Snack"
    elif "pizzeria" in nome_lower or "pizza" in nome_lower or "kebab" in nome_lower or "meze" in nome_lower: return "🍕 Pizza & Kebab"
    elif "osteria" in nome_lower or "bacaro" in nome_lower or "folperia" in nome_lower: return "🍷 Osterie & Bacari"
    elif "gelateria" in nome_lower or "gelato" in nome_lower: return "🍦 Gelaterie"
    elif "caffè" in nome_lower or "bar" in nome_lower: return "☕ Caffè & Storici"
    return "✨ Altro"

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Il Re di Padova", page_icon="🍔", layout="wide")

cookie_manager = stx.get_cookie_manager()
voto_salvato = cookie_manager.get(cookie="ha_votato_padova")

if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

if voto_salvato == "true":
    st.session_state.ha_votato = True
elif 'ha_votato' not in st.session_state:
    st.session_state.ha_votato = False

# Creiamo la tabella includendo il nuovo campo indirizzo
lista_per_tabella = []
for nome, info in st.session_state.locali.items():
    lista_per_tabella.append({
        "Locale": nome, 
        "Voti": info["voti"], 
        "Indirizzo": info.get("indirizzo", "📍 Sconosciuto"),
        "Categoria": assegna_categoria(nome)
    })

df = pd.DataFrame(lista_per_tabella)
df = df.sort_values(by='Voti', ascending=False).reset_index(drop=True)

st.title("🍔 Il Re di Padova")
st.write("Vota i tuoi posti preferiti e scopri dove si trovano!")

# --- SEZIONE: FILTRO PER CATEGORIA ---
st.subheader("📂 Esplora le Categorie")
categorie_disponibili = ["🌍 Tutti i Locali", "🥪 Panini & Snack", "🍕 Pizza & Kebab", "🍷 Osterie & Bacari", "🍦 Gelaterie", "☕ Caffè & Storici", "✨ Altro"]
categoria_selezionata = st.selectbox("Cosa cerchi oggi?", categorie_disponibili)

if categoria_selezionata != "🌍 Tutti i Locali":
    df_visualizzato = df[df['Categoria'] == categoria_selezionata].reset_index(drop=True)
else:
    df_visualizzato = df

st.write("")
num_locali = len(df_visualizzato)

# --- PODIO ---
if num_locali > 0:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="🥇 1° Posto", value=df_visualizzato.iloc[0]['Locale'], delta=f"{df_visualizzato.iloc[0]['Voti']} voti")
    if num_locali > 1:
        with col2: st.metric(label="🥈 2° Posto", value=df_visualizzato.iloc[1]['Locale'], delta=f"{df_visualizzato.iloc[1]['Voti']} voti")
    if num_locali > 2:
        with col3: st.metric(label="🥉 3° Posto", value=df_visualizzato.iloc[2]['Locale'], delta=f"{df_visualizzato.iloc[2]['Voti']} voti")
else:
    st.info("Non ci sono locali in questa categoria.")

st.markdown("---")

# --- TABELLA CLASSIFICA CON INDIRIZZI ---
st.subheader("📊 Classifica e Posizioni")
def evidenzia_podio(row):
    if row.name == 0: return ['background-color: #ffd700; color: black; font-weight: bold'] * len(row)
    elif row.name == 1: return ['background-color: #c0c0c0; color: black'] * len(row)
    elif row.name == 2: return ['background-color: #cd7f32; color: black'] * len(row)
    return [''] * len(row)

if num_locali > 0:
    df_stilizzato = df_visualizzato.style.apply(evidenzia_podio, axis=1)
    st.dataframe(df_stilizzato, use_container_width=True)

# --- SEZIONE: AGGIUNGI UN LOCALE (CON RICERCA AUTO) ---
st.subheader("➕ Aggiungi un locale (Troviamo noi l'indirizzo!)")
with st.form("nuovo_locale_form", clear_on_submit=True):
    nuovo_nome = st.text_input("Nome esatto del locale (es. Pizzeria Da Pino):")
    scelta_tipo = st.selectbox("Categoria:", ["Panini", "Pizza", "Kebab", "Osteria", "Bacaro", "Gelateria", "Caffè", "Altro"])
    bottone_aggiungi = st.form_submit_button("Cerca e Aggiungi 🔍")

    if bottone_aggiungi:
        if nuovo_nome.strip() != "":
            nome_completo = f"{nuovo_nome.strip()} ({scelta_tipo})"
            if nome_completo not in st.session_state.locali:
                with st.spinner('Sto cercando l\'indirizzo online su Padova... 🌍'):
                    # Chiamiamo la funzione magica
                    indirizzo_trovato = trova_indirizzo(nuovo_nome.strip())
                
                # Salviamo il nuovo locale con 1 voto e l'indirizzo trovato
                st.session_state.locali[nome_completo] = {"voti": 1, "indirizzo": indirizzo_trovato}
                salva_dati(st.session_state.locali)
                
                st.success(f"🎉 Aggiunto! Abbiamo trovato questo indirizzo: {indirizzo_trovato}")
                st.rerun()
            else:
                st.warning("Questo locale è già presente!")
        else:
            st.error("Inserisci un nome valido.")

# --- SEZIONE: CASSETTA DELLE VOTAZIONI ---
st.subheader("🗳️ Dai il tuo voto!")
opzione_scelta = st.selectbox("Quale locale vuoi supportare?", df_visualizzato['Locale'] if num_locali > 0 else df['Locale'])

if st.button(f"Regala un voto a: {opzione_scelta}"):
    if st.session_state.ha_votato:
        st.error("🚫 Hai già dato un voto! Sistema bloccato.")
    else:
        st.session_state.locali[opzione_scelta]["voti"] += 1
        salva_dati(st.session_state.locali)
        st.session_state.ha_votato = True
        cookie_manager.set(cookie="ha_votato_padova", val="true", key="salva_blocco")
        st.success(f"Voto registrato per {opzione_scelta}!")
        st.rerun()
