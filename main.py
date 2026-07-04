import os
import logging
import requests
from dotenv import load_dotenv, find_dotenv
from anthropic import Anthropic
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main_logger')

# Improved rotating log handler configuration (max 5 files each up to 1MB)
handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024*1024,
    backupCount=5,
    encoding='utf-8',
    delay=True
)
handler.setLevel(logging.INFO)  # Only keep messages of INFO level or higher
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

load_dotenv(find_dotenv())

ANTROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Anthropic(api_key=ANTROPIC_API_KEY)

def rewrite_news_for_customers(professional_text: str) -> str:
    logger.info("Sending text for analysis to AI...")
    # This is the system prompt that guides the AI's response
    system_prompt = """You are an assistant for a insurance broker. 
    Summarize complex insurance news for private customers in 2-3 simple sentences. 
    Use emojis and a friendly tone."""

    try:
        logger.debug(f"Using AI model: {client.messages.create.__dict__['model']}")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.5,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Summarize:\n\n{professional_text}"}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error in AI generation: {e}")
        return None

def send_to_telegram(message_text: str):
    if not message_text: 
        return
    logger.info("Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # This URL is used to send messages to the specified chat ID via Telegram Bot API
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    # The payload contains the necessary information to deliver the message

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("Successfully sent to Telegram!")
    except Exception as e:
        logger.error(f"Telegram error: {e}")

if __name__ == "__main__":
    dummy_text = "BGH-Ruling (Case IV ZR 123/25): Judges rule in favor of insurance policyholders in cases of gross negligence in building insurance."
    if not all([ANTROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logger.error("Missing API keys in .env!")
    else:
        output = rewrite_news_for_customers(dummy_text)
        send_to_telegram(output)