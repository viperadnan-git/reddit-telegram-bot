import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    Defaults,
    MessageHandler,
    TypeHandler,
    filters,
)

from src.config import Config
from src.constant import ConversationState
from src.database import db
from src.handlers.common import cancel_handler, start_command_handler
from src.handlers.login import auth_code_handler, get_login_handler, login_command_handler, logout_command_handler
from src.handlers.post import get_post_handler
from src.handlers.subreddit import (
    join_command_handler,
    leave_command_handler,
    subreddit_command_handler,
)
from src.modules.bot_context import BotContext
from src.modules.reddit_manager import RedditManager

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    pass


async def user_middleware(update: Update, context: BotContext) -> None:
    if update.effective_user:
        user_id = update.effective_user.id

        user = db.get_user(user_id)
        if not user:
            user = db.update_user(
                user_id,
                set={
                    "name": update.effective_user.full_name,
                    "username": update.effective_user.username,
                },
            )

        context.user_data["user"] = user
        if refresh_token := user.get("refresh_token"):
            context.reddit = RedditManager(refresh_token)


def main():
    context_types = ContextTypes(context=BotContext)
    defaults = Defaults(parse_mode=ParseMode.HTML)
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .context_types(context_types)
        .defaults(defaults)
        .build()
    )

    application.add_handler(TypeHandler(Update, user_middleware), group=-1)
    application.add_handler(CommandHandler("start", start_command_handler))
    application.add_handler(CommandHandler("join", join_command_handler))
    application.add_handler(CommandHandler("leave", leave_command_handler))
    application.add_handler(
        CommandHandler(["subreddits", "subs", "subreddit"], subreddit_command_handler)
    )

    application.add_handler(get_login_handler())
    application.add_handler(CommandHandler("logout", logout_command_handler))

    application.add_handler(get_post_handler())

    if Config.WEBHOOK_URL:
        application.run_webhook(
            listen=Config.HOST,
            port=Config.PORT,
            webhook_url=Config.WEBHOOK_URL,
            secret_token=Config.SECRET_TOKEN,
        )
    else:
        application.run_polling()


if __name__ == "__main__":
    main()
