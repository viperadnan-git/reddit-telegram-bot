from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.constant import ConversationState
from src.database import db
from src.handlers.common import cancel_handler
from src.modules.bot_context import BotContext
from src.modules.reddit_manager import RedditManager
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters


async def login_command_handler(update: Update, context: BotContext):
    if context.reddit:
        await update.message.reply_text(
            "You are already authenticated. Please use /logout to logout."
        )
        return ConversationState.END

    auth_url = RedditManager.create_auth_url(update.message.from_user.id)

    keyboard = [[InlineKeyboardButton("Authenticate Reddit", url=auth_url)]]

    await update.message.reply_text(
        f"Please visit this URL to and authenticate with Reddit. Copy the code from the URL and paste it here.\n\n<i>Send /cancel to cancel the process</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ConversationState.WAITING_FOR_AUTH_CODE


async def auth_code_handler(update: Update, context: BotContext):
    auth_code = update.message.text
    refresh_token, username = RedditManager.authorize_user(
        update.message.from_user.id, auth_code
    )
    db.update_user(update.message.from_user.id, set={"refresh_token": refresh_token})

    context.reddit = RedditManager(refresh_token)
    await update.message.reply_text(
        f"Reddit authenticated successfully as u/{username}"
    )
    return ConversationState.END


async def logout_command_handler(update: Update, context: BotContext):
    db.update_user(update.message.from_user.id, unset={"refresh_token": ""})
    await update.message.reply_text("Reddit logged out successfully")
    return ConversationState.END


def get_login_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("login", login_command_handler)],
        states={
            ConversationState.WAITING_FOR_AUTH_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth_code_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )
