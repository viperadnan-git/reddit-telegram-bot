from telegram import Bot
from telegram.ext import CallbackContext

from src.models.user import User
from src.modules.reddit_manager import RedditManager


class BotContext(CallbackContext[Bot, dict, dict, dict]):
    reddit: RedditManager
    user: User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reddit = None
        self.user = None
