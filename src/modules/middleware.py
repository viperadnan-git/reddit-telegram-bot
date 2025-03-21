import logging

from telegram import Update

from src.database import db
from src.models.user import User
from src.modules.bot_context import BotContext
from src.modules.reddit_manager import RedditManager

logger = logging.getLogger(__name__)


def update_user(update: Update, context: BotContext, user_id: str) -> None:
    user = db.get_user(user_id)
    if not user:
        user = User(
            id=user_id,
            name=update.effective_user.full_name,
            username=update.effective_user.username,
        )
        user.save()

    context.user = user
    context.user_data["user"] = user
    if refresh_token := user.refresh_token:
        # Use user's keys if available
        client_id = None
        client_secret = None
        if user.keys:
            client_id = user.keys.client_id
            client_secret = user.keys.client_secret

        context.reddit = RedditManager(
            refresh_token, client_id=client_id, client_secret=client_secret
        )
        context.user_data["reddit"] = context.reddit


async def user_middleware(update: Update, context: BotContext) -> None:
    if update.effective_user:
        user_id = update.effective_user.id
        logger.info(f"Incoming update from user {user_id}")

        if not context.user_data.get("user"):
            update_user(update, context, user_id)
        else:
            context.user = context.user_data["user"]
            context.reddit = context.user_data.get("reddit")
