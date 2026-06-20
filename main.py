import os
import logging
import requests
from dotenv import load_dotenv, find_dotenv
from anthropic import Anthropic
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main_logger')

# Verbesserte Rotierendes Log-Handler-Konfiguration
handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024*1024,
    backupCount=5,
    encoding='utf-8',
    delay=True
)
handler.setLevel(logging.INFO)  # Nur Meldungen vom INFO-Level oder höher behalten
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

load_dotenv(find_dotenv())

ANTROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Anthropic(api_key=ANTROPIC_API_KEY)

def rewrite_news_for_customers(professional_text: str) -> str:
    logger.info("Sende Text zur Analyse an die KI...")
    system_prompt = """Du bist ein Assistent für einen Versicherungsmakler. 
    Fasse komplexe Versicherungs-News für Privatkunden in 2-3 einfachen Sätzen zusammen. 
    Nutze Emojis und einen freundlichen Ton."""

    try:
        logger.debug(f"Verwende KI-Modell: {client.messages.create.__dict__['model']}")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.5,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Fasse zusammen:\n\n{professional_text}"}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Fehler bei KI-Generierung: {e}")
        return None

def send_to_telegram(message_text: str):
    if not message_text: 
        return
    logger.info("Sende an Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("Erfolgreich an Telegram gesendet!")
    except Exception as e:
        logger.error(f"Telegram Fehler: {e}")

if __name__ == "__main__":
    dummy_text = "BGH-Urteil (Az. IV ZR 123/25): Richter entscheiden zugunsten der Versicherungsnehmer bei grober Fahrlässigkeit in Gebäudeversicherungen."
    if not all([ANTROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logger.error("Fehlende API Keys in .env!")
    else:
        output = rewrite_news_for_customers(dummy_text)
        send_to_telegram(output)