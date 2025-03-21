import logging

import praw

from src.config import Config

logger = logging.getLogger(__name__)


class RedditManager(praw.Reddit):
    def __init__(self, refresh_token: str, client_id=None, client_secret=None):
        super().__init__(
            client_id=client_id or Config.REDDIT_CLIENT_ID,
            client_secret=client_secret or Config.REDDIT_CLIENT_SECRET,
            refresh_token=refresh_token,
            user_agent=Config.USERAGENT,
            check_for_async=False,
        )

    @staticmethod
    def create_auth_url(user_id: str, client_id=None, client_secret=None) -> str:
        reddit = praw.Reddit(
            client_id=client_id or Config.REDDIT_CLIENT_ID,
            client_secret=client_secret or Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.USERAGENT,
            redirect_uri="https://mostly.pages.dev/copy-code/",
            check_for_async=False,
        )
        return reddit.auth.url(scopes=["*"], state=user_id, duration="permanent")

    @staticmethod
    def authorize_user(
        user_id: str, code: str, client_id=None, client_secret=None
    ) -> str:
        reddit = praw.Reddit(
            client_id=client_id or Config.REDDIT_CLIENT_ID,
            client_secret=client_secret or Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.USERAGENT,
            redirect_uri="https://mostly.pages.dev/copy-code/",
            check_for_async=False,
        )
        refresh_token = reddit.auth.authorize(code)
        return refresh_token, str(reddit.user.me())
