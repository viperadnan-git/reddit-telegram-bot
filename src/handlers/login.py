from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters

from src.constant import ConversationState
from src.database import db
from src.handlers.common import cancel_handler
from src.modules.bot_context import BotContext
from src.modules.middleware import update_user
from src.modules.reddit_manager import RedditManager


async def login_command_handler(update: Update, context: BotContext):
    if context.reddit:
        await update.message.reply_text(
            "You are already authenticated. Please use /logout to logout."
        )
        return ConversationState.END

    # Use user's keys if available
    client_id = None
    client_secret = None
    if context.user.keys:
        client_id = context.user.keys.client_id
        client_secret = context.user.keys.client_secret

    auth_url = RedditManager.create_auth_url(
        update.message.from_user.id, client_id=client_id, client_secret=client_secret
    )

    keyboard = [[InlineKeyboardButton("Authenticate Reddit", url=auth_url)]]

    await update.message.reply_text(
        f"Please visit this URL to and authenticate with Reddit. Copy the code from the URL and paste it here.\n\n<i>Send /cancel to cancel the process</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ConversationState.WAITING_FOR_AUTH_CODE


async def auth_code_handler(update: Update, context: BotContext):
    auth_code = update.message.text
    user_id = update.message.from_user.id

    # Use user's keys if available
    client_id = None
    client_secret = None
    if context.user.keys:
        client_id = context.user.keys.client_id
        client_secret = context.user.keys.client_secret

    refresh_token, username = RedditManager.authorize_user(
        user_id, auth_code, client_id=client_id, client_secret=client_secret
    )
    db.update_user(user_id, set={"refresh_token": refresh_token})

    update_user(update, context, user_id)
    await update.message.reply_text(
        f"Reddit authenticated successfully as u/{username}"
    )
    return ConversationState.END


async def logout_command_handler(update: Update, context: BotContext):
    context.user.refresh_token = None
    context.user.save()

    context.user_data.pop("reddit", None)
    context.user_data.pop("user", None)
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
