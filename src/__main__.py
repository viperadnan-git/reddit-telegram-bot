import logging

from telegram import BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Defaults,
    TypeHandler,
)

from src.config import Config
from src.handlers.common import start_command_handler
from src.handlers.keys import get_keys_handler
from src.handlers.login import get_login_handler, logout_command_handler
from src.handlers.post import get_post_handler
from src.handlers.subreddit import (
    join_command_handler,
    leave_command_handler,
    subreddit_command_handler,
)
from src.modules.bot_context import BotContext
from src.modules.middleware import user_middleware

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Start the bot"),
            BotCommand("login", "Login to your Reddit account"),
            BotCommand("logout", "Logout from your Reddit account"),
            BotCommand("keys", "Manage your Reddit API keys"),
            BotCommand("post", "Post a message to Reddit"),
            BotCommand("join", "Join a subreddit"),
            BotCommand("leave", "Leave a subreddit"),
            BotCommand("subreddit", "List your subscribed subreddits"),
        ]
    )


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

    application.add_handler(get_keys_handler())
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
