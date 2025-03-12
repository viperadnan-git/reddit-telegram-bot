import logging
import os

from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


class Config:
    try:
        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
        REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
        REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
        MONGO_URI = os.environ["MONGO_URI"]

        TEMP_DIR = os.environ.get("TEMP_DIR", "tmp")
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise

    USERAGENT = "Reddit-Telegram-Bot by viperadnan / 1.0"
