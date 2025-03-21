from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.handlers.common import cancel_handler
from src.models.user import RedditKeys
from src.modules.bot_context import BotContext


class KeysAction(Enum):
    WAITING_FOR_CLIENT_ID = 1
    WAITING_FOR_CLIENT_SECRET = 2
    WAITING_FOR_CONFIRMATION = 3
    WAITING_FOR_ACTION = 4

    END = ConversationHandler.END


async def keys_command_handler(update: Update, context: BotContext):
    if not context.user.keys:
        await update.message.reply_text(
            "No Client ID or Client Secret is set, default is being used.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Add keys", callback_data="action:add_keys")]]
            ),
        )
        return KeysAction.WAITING_FOR_ACTION

    await update.message.reply_text(
        f"Client ID: {context.user.keys.client_id}\nClient Secret: {context.user.keys.client_secret}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Change keys", callback_data="action:add_keys"
                    ),
                    InlineKeyboardButton(
                        "Remove keys", callback_data="action:remove_keys"
                    ),
                ]
            ]
        ),
    )
    return KeysAction.WAITING_FOR_ACTION


async def handle_keys_action(update: Update, context: BotContext):
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1]
    if action == "add_keys":
        await query.message.edit_text("Please enter your Reddit Client ID:")
        return KeysAction.WAITING_FOR_CLIENT_ID
    elif action == "remove_keys":
        context.user.keys = None
        context.user.save()
        await query.message.edit_text(
            "Your Reddit API keys have been removed. Default keys will be used."
        )
        return KeysAction.END


async def client_id_handler(update: Update, context: BotContext):
    client_id = update.message.text.strip()

    # Store client_id in context for later use
    context.user_data["temp_client_id"] = client_id

    await update.message.reply_text("Please enter your Reddit Client Secret:")
    return KeysAction.WAITING_FOR_CLIENT_SECRET


async def client_secret_handler(update: Update, context: BotContext):
    client_secret = update.message.text.strip()
    client_id = context.user_data.get("temp_client_id")

    # Store client_secret in context for confirmation
    context.user_data["temp_client_secret"] = client_secret

    # Show confirmation message with both values
    await update.message.reply_text(
        f"Please confirm your Reddit API Keys:\n\nClient ID: {client_id}\nClient Secret: {client_secret}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Confirm", callback_data="keys_confirm:yes"),
                    InlineKeyboardButton("Cancel", callback_data="keys_confirm:no"),
                ]
            ]
        ),
    )

    return KeysAction.WAITING_FOR_CONFIRMATION


async def confirmation_handler(update: Update, context: BotContext):
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1]

    if action == "yes":
        client_id = context.user_data.get("temp_client_id")
        client_secret = context.user_data.get("temp_client_secret")

        # Save the keys to user object
        context.user.keys = RedditKeys(client_id=client_id, client_secret=client_secret)
        context.user.save()

        # Clean up temporary data
        if "temp_client_id" in context.user_data:
            del context.user_data["temp_client_id"]
        if "temp_client_secret" in context.user_data:
            del context.user_data["temp_client_secret"]

        await query.message.edit_text(
            "Your Reddit API keys have been saved successfully!"
        )
        return KeysAction.END
    else:
        await query.message.edit_text("Operation cancelled.")
        return KeysAction.END


def get_keys_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler(["keys", "key"], keys_command_handler)],
        states={
            KeysAction.WAITING_FOR_ACTION: [
                CallbackQueryHandler(handle_keys_action, pattern=r"^action:")
            ],
            KeysAction.WAITING_FOR_CLIENT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, client_id_handler)
            ],
            KeysAction.WAITING_FOR_CLIENT_SECRET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, client_secret_handler)
            ],
            KeysAction.WAITING_FOR_CONFIRMATION: [
                CallbackQueryHandler(confirmation_handler, pattern=r"^keys_confirm:")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )
