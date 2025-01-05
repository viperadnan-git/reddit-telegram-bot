from functools import wraps
from telegram.ext import Application, CommandHandler, ContextTypes, TypeHandler, Defaults
from telegram.constants import ParseMode
from telegram import Update
import logging
from src.config import Config
from src.constant import ConversationState
from src.handlers.login import auth_code_handler, login_handler
from src.handlers.post import (
    post_body_handler,
    post_flair_handler,
    post_media_handler,
    post_message_handler,
    post_post_confirmation_handler,
    post_title_handler,
    post_subreddit_handler,
)
from src.modules.bot_context import BotContext
from src.modules.reddit_manager import RedditManager
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from src.database import db

logger = logging.getLogger(__name__)


async def start(update: Update, context: BotContext) -> None:
    await update.message.reply_text("Hi, I'm a bot that can help you post to Reddit.")

async def cancel_handler(update: Update, context: BotContext) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationState.END

async def post_init(application: Application) -> None:
    pass


async def user_middleware(update: Update, context: BotContext) -> None:
    user_id = update.effective_user.id

    user = db.get_user(user_id)
    if not user:
        user = db.update_user(
            user_id,
            {
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
    application.add_handler(CommandHandler("start", start))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("login", login_handler)],
        states={
            ConversationState.WAITING_FOR_AUTH_CODE: [MessageHandler(filters.TEXT, auth_code_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    ))

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.TEXT
                    | filters.VIDEO
                    | filters.PHOTO
                    | filters.Document.VIDEO
                    | filters.Document.IMAGE,
                    post_message_handler,
                )
            ],
            states={
                ConversationState.WAITING_FOR_TITLE: [
                    MessageHandler(filters.TEXT, post_title_handler)
                ],
                ConversationState.WAITING_FOR_BODY: [
                    MessageHandler(filters.TEXT, post_body_handler)
                ],
                ConversationState.WAITING_FOR_MEDIA: [
                    MessageHandler(
                        filters.TEXT
                        | filters.VIDEO
                        | filters.PHOTO
                        | filters.Document.VIDEO
                        | filters.Document.IMAGE,
                        post_media_handler,
                    )
                ],
                ConversationState.WAITING_FOR_SUBREDDIT: [
                    CallbackQueryHandler(
                        post_subreddit_handler, pattern="^p_subreddit:"
                    )
                ],
                ConversationState.WAITING_FOR_FLAIR: [
                    CallbackQueryHandler(
                        post_flair_handler, pattern="^p_flair:"
                    )
                ],
                ConversationState.WAITING_FOR_POST_CONFIRMATION: [
                    CallbackQueryHandler(
                        post_post_confirmation_handler, pattern="^p_confirm:"
                    )
                ],
            },
            fallbacks=[],
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()
