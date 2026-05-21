import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
import time

# Impostazione della pagina Streamlit
st.set_page_config(page_title="Classifica Locali Padova", page_icon="🍕", layout="wide")

# Inizializzazione del Cookie Manager
cookie_manager = stx.CookieManager()

# SIFONE ANTI-RACE: Blocca l'app finché i cookie dal browser non sono stati letti del tutto
if 'cookies_caricati' not in st.session_state:
    time.sleep(0.6)  # Pausa strategica di 600ms per attendere il browser
    st.session_state['cookies_caricati'] = True
    st.rerun()

# Database di emergenza interno per garantire che indirizzi e categorie si vedano SEMPRE correttamente
INFO_LOCALI = {
    "Dalla Zita (Panini)": {"indirizzo": "Via Gorizia, 12", "categoria": "🥪 Panini & Snack"},
    "Caffè Pedrocchi (Storico)": {"indirizzo": "Via VIII Febbraio, 15", "categoria": "☕ Caffè & Storici"},
    "Pizzeria Pago Pago": {"indirizzo": "Via Galileo Galilei, 59", "categoria": "🍕 Pizza & Kebab"},
    "Gelateria GROM": {"indirizzo": "Via Roma, 101", "categoria": "🍦 Gelaterie"},
    "Vicoli (Via Umberto I)": {"indirizzo": "Via Umberto I, 95", "categoria": "✨ Altro"},
    "MEZE TURKISH KEBAB GRILL (Chiesanuova)": {"indirizzo": "Via Chiesanuova, 73", "categoria": "🍕 Pizza & Kebab"},
    "Osteria l'Anfora": {"indirizzo": "Via Soncin, 13", "categoria": "🍷 Osterie & Ristoranti"},
    "Osteria dal Capo": {"indirizzo": "Via degli Obizzi, 2", "categoria": "🍷 Osterie & Ristoranti"},
    "Enoteca Ristorante dei Tadi": {"indirizzo": "Via dei Tadi, 15", "categoria": "🍷 Osterie & Ristoranti"},
    "SO' RIVÁ - Ristorantino": {"indirizzo": "Passaggio Corner Piscopia, 20", "categoria": "🍷 Osterie & Ristoranti"},
    "Bacaro Padovano": {"indirizzo": "Via San Gregorio Barbarigo, 3", "categoria": "🍷 Osterie & Ristoranti"},
    "La Folperia": {"indirizzo": "Piazza della Frutta, 1", "categoria": "🐙 Street Food & Pesce"},
    "Gelateria Romana": {"indirizzo": "Corso Milano, 34", "categoria": "🍦 Gelaterie"}
}

# Funzioni di lettura e scrittura sicura del file JSON
def carica_locali():
    if os.path.exists("Locali_padova.json"):
        try:
            with open("Locali_padova.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salva_locali(dati):
    with open("Locali_padova.json", "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

# Carica i dati dal file JSON su GitHub
dati_json = carica_locali()

# Costruiamo la lista pulita decodificando la struttura del file JSON
lista_classifica = []
for locale, info in dati_json.items():
    # Se il dato è già un dizionario strutturato estrae i valori, altrimenti usa il database interno
    if isinstance(info, dict):
        voti = info.get("voti", 1)
        indirizzo = info.get("indirizzo", INFO_LOCALI.get(locale, {}).get("indirizzo", "📍 Sconosciuto"))
        categoria = info.get("categoria", INFO_LOCALI.get(locale, {}).get("categoria", "✨ Altro"))
    else:
        voti = info
        indirizzo = INFO_LOCALI.get(locale, {}).get("indirizzo", "📍 Sconosciuto")
        categoria = INFO_LOCALI.get(locale, {}).get("categoria", "✨ Altro")
    
    lista_classifica.append({
        "Locale": locale,
        "Voti": voti,
        "Indirizzo": indirizzo,
        "Categoria": categoria
    })

# Se il file JSON era vuoto o corrotto, lo ripopola automaticamente da zero
if not lista_classifica:
    for locale, info in INFO_LOCALI.items():
        lista_classifica.append({
            "Locale": locale,
            "Voti": 1,
            "Indirizzo": info["indirizzo"],
            "Categoria": info["categoria"]
        })
        dati_json[locale] = {"voti": 1, "indirizzo": info["indirizzo"], "categoria": info["categoria"]}
    salva_locali(dati_json)

# Crea il DataFrame pandas e ordina per numero di voti dal più alto al più basso
df = pd.DataFrame(lista_classifica)
df = df.sort_values(by="Voti", ascending=False).reset_index(drop=True)

# --- INTERFACCIA UTENTE ---
st.title("📊 Classifica e Posizioni dei Locali di Padova")

# Sezione del Podio Dinamico
col1, col2, col3 = st.columns(3)
if len(df) >= 1:
    col1.metric("🥇 1° Posto", df.iloc[0]["Locale"], f"{df.iloc[0]['Voti']} voti")
if len(df) >= 2:
    col2.metric("🥈 2° Posto", df.iloc[1]["Locale"], f"{df.iloc[1]['Voti']} voti")
if len(df) >= 3:
    col3.metric("🥉 3° Posto", df.iloc[2]["Locale"], f"{df.iloc[2]['Voti']} voti")

st.write("---")

# Visualizzazione della tabella dati principale
st.subheader("📋 Classifica Completa")
st.dataframe(df, use_container_width=True)

st.write("---")
st.subheader("🗳️ Vota il tuo locale preferito")

# Controllo effettivo dello stato del Cookie salvato nel browser
ha_votato = cookie_manager.get("ha_votato_padova_v2")

if ha_votato == "true":
    st.warning("🚫 Hai già espresso il tuo voto da questo dispositivo per oggi! Non puoi votare più volte.")
else:
    # Form di selezione e invio voto
    locale_selezionato = st.selectbox("Seleziona il locale dall'elenco:", df["Locale"].tolist())
    
    if st.button("Invia il tuo Voto 🗳️"):
        # Controllo di sicurezza istantaneo per evitare doppie risposte rapide
        ha_votato_sicurezza = cookie_manager.get("ha_votato_padova_v2")
        if ha_votato_sicurezza == "true":
            st.error("Azione bloccata: Rilevato tentativo di voto multiplo.")
        else:
            # Aggiorna il valore numerico dei voti
            if locale_selezionato in dati_json and isinstance(dati_json[locale_selezionato], dict):
                dati_json[locale_selezionato]["voti"] += 1
            else:
                dati_json[locale_selezionato] = {
                    "voti": 2,
                    "indirizzo": INFO_LOCALI.get(locale_selezionato, {}).get("indirizzo", "📍 Sconosciuto"),
                    "categoria": INFO_LOCALI.get(locale_selezionato, {}).get("categoria", "✨ Altro")
                }
            
            # Scrive le modifiche sul file JSON
            salva_locali(dati_json)
            
            # Genera il cookie permanente sul browser valido per 24 ore (86400 secondi)
            cookie_manager.set("ha_votato_padova_v2", "true", max_age=86400)
            
            st.success(f"🎉 Voto registrato correttamente per: {locale_selezionato}!")
            time.sleep(1)
            st.rerun()
