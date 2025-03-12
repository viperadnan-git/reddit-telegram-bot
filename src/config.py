import hashlib
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


class Config:
    try:
        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
        REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
        REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
        MONGO_URI = os.environ["MONGO_URI"]
        WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", 8000)
        WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")

        __TMP_DIR = os.getenv("TMP_DIR", "tmp")
        TMP_DIR = Path(__TMP_DIR)
        if not TMP_DIR.exists():
            TMP_DIR.mkdir(parents=True, exist_ok=True)
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise

    USERAGENT = "Reddit-Telegram-Bot by viperadnan / 1.0"
    SECRET_TOKEN = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).hexdigest()
