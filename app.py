import streamlit as st
import pandas as pd
import json
import os

# Nome del file in cui salveremo i dati
FILE_DATI = "locali_padova.json"

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

# FUNZIONE 3: Assegna automaticamente la categoria in base al nome
def assegna_categoria(nome):
    nome_lower = nome.lower()
    if "panini" in nome_lower or "zita" in nome_lower or "snack" in nome_lower:
        return "🥪 Panini & Snack"
    elif "pizzeria" in nome_lower or "pizza" in nome_lower or "kebab" in nome_lower or "meze" in nome_lower:
        return "🍕 Pizza & Kebab"
    elif "osteria" in nome_lower or "bacaro" in nome_lower or "tadi" in nome_lower or "rivá" in nome_lower or "capo" in nome_lower or "anfora" in nome_lower or "folperia" in nome_lower:
        return "🍷 Osterie & Bacari"
    elif "gelateria" in nome_lower or "grom" in nome_lower or "romana" in nome_lower or "gelato" in nome_lower:
        return "🍦 Gelaterie"
    elif "caffè" in nome_lower or "pedrocchi" in nome_lower or "bar" in nome_lower:
        return "☕ Caffè & Storici"
    return "✨ Altro"

# --- INIZIO APPLICAZIONE STREAMLIT ---
st.set_page_config(page_title="Il Re di Padova", page_icon="🍔", layout="wide")

st.title("🍔 Il Re di Padova - Classifica Locali")
st.write("Vota i tuoi posti preferiti, filtra per categoria e stravolgi la classifica!")

# Inizializziamo la sessione caricando i dati dal file
if 'locali' not in st.session_state:
    st.session_state.locali = carica_dati()

# Inizializziamo il controllo del voto nel browser dell'utente
if 'ha_votato' not in st.session_state:
    st.session_state.ha_votato = False

# Trasformiamo i dati in un DataFrame e assegniamo le categorie
df = pd.DataFrame(list(st.session_state.locali.items()), columns=['Locale', 'Voti'])
df['Categoria'] = df['Locale'].apply(assegna_categoria)
df = df.sort_values(by='Voti', ascending=False).reset_index(drop=True)


# --- NUOVA SEZIONE: FILTRO PER CATEGORIA ---
st.subheader("📂 Esplora le Categorie")
categorie_disponibili = ["🌍 Tutti i Locali", "🥪 Panini & Snack", "🍕 Pizza & Kebab", "🍷 Osterie & Bacari", "🍦 Gelaterie", "☕ Caffè & Storici", "✨ Altro"]
categoria_selezionata = st.selectbox("Cosa ti va di mangiare oggi?", categorie_disponibili)

# Filtriamo il DataFrame in base alla scelta dell'utente
if categoria_selezionata != "🌍 Tutti i Locali":
    df_visualizzato = df[df['Categoria'] == categoria_selezionata].reset_index(drop=True)
else:
    df_visualizzato = df


# --- SEZIONE: IL PODIO VISIVO (TOP 3 FILTRATO) ---
st.write("")
num_locali = len(df_visualizzato)

if num_locali > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🥇 1° Posto", value=df_visualizzato.iloc[0]['Locale'], delta=f"{df_visualizzato.iloc[0]['Voti']} voti")
    if num_locali > 1:
        with col2:
            st.metric(label="🥈 2° Posto", value=df_visualizzato.iloc[1]['Locale'], delta=f"{df_visualizzato.iloc[1]['Voti']} voti")
    if num_locali > 2:
        with col3:
            st.metric(label="🥉 3° Posto", value=df_visualizzato.iloc[2]['Locale'], delta=f"{df_visualizzato.iloc[2]['Voti']} voti")
else:
    st.info("Non ci sono ancora locali in questa categoria. Aggiungine uno tu qua sotto!")

st.markdown("---")


# --- TABELLA COLORATA ---
st.subheader("📊 Classifica")

def evidenzia_podio(row):
    if row.name == 0:
        return ['background-color: #ffd700; color: black; font-weight: bold'] * len(row)
    elif row.name == 1:
        return ['background-color: #c0c0c0; color: black'] * len(row)
    elif row.name == 2:
        return ['background-color: #cd7f32; color: black'] * len(row)
    return [''] * len(row)

if num_locali > 0:
    df_stilizzato = df_visualizzato.style.apply(evidenzia_podio, axis=1)
    st.dataframe(df_stilizzato, use_container_width=True)


# --- SEZIONE: AGGIUNGI UN LOCALE ---
st.subheader("➕ Non vedi il tuo posto preferito? Aggiungilo!")

with st.form("nuovo_locale_form", clear_on_submit=True):
    nuovo_nome = st.text_input("Nome del locale:")
    scelta_tipo = st.selectbox("Categoria:", ["Panini", "Pizza", "Kebab", "Osteria", "Bacaro", "Gelateria", "Caffè", "Altro"])
    bottone_aggiungi = st.form_submit_button("Inserisci nella classifica")

    if bottone_aggiungi:
        if nuovo_nome.strip() != "":
            # Creiamo il nome includendo il tipo scelto per aiutare la funzione di auto-categoria
            nome_completo = f"{nuovo_nome.strip()} ({scelta_tipo})"
            if nome_completo not in st.session_state.locali:
                st.session_state.locali[nome_completo] = 1
                salva_dati(st.session_state.locali)
                st.success(f"🎉 {nome_completo} aggiunto con successo!")
                st.rerun()
            else:
                st.warning("Questo locale è già presente!")
        else:
            st.error("Inserisci un nome valido.")


# --- SEZIONE: CASSETTA DELLE VOTAZIONI ---
st.subheader("🗳️ Dai il tuo voto!")
# Facciamo votare solo partendo dai locali visibili nella categoria selezionata per comodità
opzione_scelta = st.selectbox("Quale locale vuoi supportare?", df_visualizzato['Locale'] if num_locali > 0 else df['Locale'])

if st.button(f"Regala un voto a: {opzione_scelta}"):
    if st.session_state.ha_votato:
        st.error("🚫 Hai già dato un voto in questa sessione!")
    else:
        st.session_state.locali[opzione_scelta] += 1
        salva_dati(st.session_state.locali)
        st.session_state.ha_votato = True
        st.success(f"Grazie! Il tuo voto per {opzione_scelta} è stato registrato!")
        st.rerun()
