from telegram import Bot
from telegram.ext import CallbackContext

from src.modules.reddit_manager import RedditManager


class BotContext(CallbackContext[Bot, dict, dict, dict]):
    reddit: RedditManager

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
