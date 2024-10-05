import streamlit as st
from streamlit_sortables import sort_items
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

import os

# Ihre E-Mail-Adresse und das App-Passwort aus Umgebungsvariablen
sender_email = st.secrets["MAILADRESSE"]
password = st.secrets["MAILPASSWORT"]

# Empfängeradresse (kann dieselbe sein)
receiver_email = sender_email  # oder eine andere E-Mail-Adresse

st.set_page_config(page_title="Pralinen Umfrage", page_icon="🍫", layout="wide")

# Überprüfen, ob die Umfrage bereits abgeschlossen wurde
if 'abfrage_beendet' in st.session_state and st.session_state['abfrage_beendet']:
    st.write("Vielen Dank für das Ausfüllen der Umfrage!")
    st.stop()

st.title("Pralinen Umfrage")
st.write("Bitte nehmen Sie sich einen Moment Zeit, um unsere Pralinen zu bewerten.")

# Optionales Namensfeld
name = st.text_input("Ihr Name (optional)")

# Liste der Pralinen mit Beschreibungen und Bildpfaden
pralinen = [
    {
        "name": "Praline 1",
        "beschreibung": "Füllung: Nougat, Topping: Haselnuss",
        "bild": "praline1.jpg"
    },
    {
        "name": "Praline 2",
        "beschreibung": "Füllung: Marzipan, Topping: Mandelsplitter",
        "bild": "praline2.jpg"
    },
    {
        "name": "Praline 3",
        "beschreibung": "Füllung: Karamell, Topping: Meersalz",
        "bild": "praline3.jpg"
    },
    {
        "name": "Praline 4",
        "beschreibung": "Füllung: Himbeere, Topping: Weiße Schokolade",
        "bild": "praline4.jpg"
    },
    {
        "name": "Praline 5",
        "beschreibung": "Füllung: Pistazie, Topping: Dunkle Schokolade",
        "bild": "praline5.jpg"
    },
    {
        "name": "Praline 6",
        "beschreibung": "Füllung: Kaffeecreme, Topping: Kakaopulver",
        "bild": "praline6.jpg"
    },
    {
        "name": "Praline 7",
        "beschreibung": "Füllung: Orange, Topping: Zartbitterschokolade",
        "bild": "praline7.jpg"
    },
    {
        "name": "Praline 8",
        "beschreibung": "Füllung: Minze, Topping: Schokostreusel",
        "bild": "praline8.jpg"
    }
]

# Bewertungsoptionen
options = ["Sehr gut", "Gut", "Neutral", "Weniger gut", "Schlecht"]

# Platz für die Bewertungen
bewertungen = {}

for praline in pralinen:
    st.header(praline["name"])
    cols = st.columns([1, 2])
    with cols[0]:
        st.image(praline["bild"], use_column_width=True)
    with cols[1]:
        st.write(praline["beschreibung"])
        bewertungen[praline["name"]] = {}
        bewertungen[praline["name"]]["füllung"] = st.radio(
            f"Bewerten Sie die Füllung von {praline['name']}",
            options=options,
            index=2,
            key=f"füllung_{praline['name']}"
        )
        bewertungen[praline["name"]]["topping"] = st.radio(
            f"Bewerten Sie das Topping von {praline['name']}",
            options=options,
            index=2,
            key=f"topping_{praline['name']}"
        )
        bewertungen[praline["name"]]["gesamt"] = st.radio(
            f"Gesamtbewertung für {praline['name']}",
            options=options,
            index=2,
            key=f"gesamt_{praline['name']}"
        )

st.header("Ranking der Pralinen")
st.write("Bitte ordnen Sie die Pralinen nach Ihrer Präferenz (von Lieblingspraline bis weniger beliebt).")

# Namen der Pralinen für das Ranking
pralinen_namen = [praline["name"] for praline in pralinen]

# Ranking-Funktion
try:
    ranking = sort_items(pralinen_namen, direction="vertical", key='sortable_namen')
except Exception as e:
    st.write("Bitte installieren Sie das 'streamlit-sortables' Package für das Ranking.")
    st.write(f"Fehler: {e}")
    ranking = []

st.header("Ihre Ideen und Rückmeldungen")
neue_sorten = st.text_area("Haben Sie Ideen für neue Pralinensorten?")
feedback = st.text_area("Weitere Rückmeldungen:")

# Daten speichern und per E-Mail senden
if st.button("Abschicken"):
    # Daten sammeln
    umfrage_daten = {
        "name": name,
        "bewertungen": bewertungen,
        "ranking": ranking,
        "neue_sorten": neue_sorten,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }

    # Daten als JSON-String formatieren
    umfrage_json = json.dumps(umfrage_daten, ensure_ascii=False, indent=4)

    # E-Mail-Versand einrichten
    message = MIMEMultipart()
    message["Subject"] = "Neue Pralinen-Umfrage eingegangen"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Nachricht erstellen
    text = f"Es wurde eine neue Umfrage von {name} ausgefüllt. Die Ergebnisse finden sich im Anhang."
    part1 = MIMEText(text, "plain", "utf-8")
    message.attach(part1)

    # JSON-Datei erstellen und anhängen
    filename = f"umfrage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    part2 = MIMEApplication(umfrage_json.encode('utf-8'), Name=filename)
    part2['Content-Disposition'] = f'attachment; filename="{filename}"'
    message.attach(part2)

    try:
        # Mit dem Gmail SMTP-Server verbinden und E-Mail senden
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        st.success("Vielen Dank für Ihre Teilnahme! Ihre Antworten wurden gesendet.")

        # Session State aktualisieren und Seite neu laden
        st.session_state['abfrage_beendet'] = True
        st.rerun()

    except Exception as e:
        st.error(f"Es gab ein Problem beim Versenden Ihrer Antworten: {e}")
