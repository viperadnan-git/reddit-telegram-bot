from telegram import Update

from src.constant import ConversationState
from src.modules.bot_context import BotContext


async def start_command_handler(update: Update, context: BotContext) -> None:
    message = "Hi, I'm a bot that can help you post to Reddit."
    update_message = await update.message.reply_text(message)

    if context.reddit:
        me = context.reddit.user.me()
        message += f"\n\nYou are logged in as <a href='https://www.reddit.com/u/{me.name}'>{me.name}</a>."
        if me.is_suspended:
            message += "\n⚠️ Your Reddit account is suspended."

        await update_message.edit_text(message)


async def cancel_handler(update: Update, context: BotContext) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationState.END
