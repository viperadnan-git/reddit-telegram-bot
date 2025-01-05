import os
import praw
from src.config import Config
import logging
from src.database import db

logger = logging.getLogger(__name__)

class RedditManager(praw.Reddit):
    def __init__(self, refresh_token: str):
        super().__init__(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            refresh_token=refresh_token,
            user_agent=Config.USERAGENT,
            check_for_async=False,
        )

    @staticmethod
    def create_auth_url(user_id: str) -> str:
        reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.USERAGENT,
            redirect_uri="https://mostly.pages.dev/copy-code/",
            check_for_async=False,
        )
        return reddit.auth.url(scopes=["*"], state=user_id, duration="permanent")

    @staticmethod
    def authorize_user(user_id: str, code: str) -> str:
        reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.USERAGENT,
            redirect_uri="https://mostly.pages.dev/copy-code/",
            check_for_async=False,
        )
        refresh_token = reddit.auth.authorize(code)
        db.update_user(user_id, {"refresh_token": refresh_token})
        return refresh_token, str(reddit.user.me())
