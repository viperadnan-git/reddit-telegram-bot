from functools import wraps

from telegram import Update

from src.constant import ConversationState
from src.modules.bot_context import BotContext


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if not context.reddit:
            await update.message.reply_text(
                "You need to authenticate with Reddit first. Use /login to do that."
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def args_required(count: int, message: str):
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: BotContext, *args, **kwargs):
            if len(context.args) < count:
                await update.message.reply_text(message)
                return ConversationState.END
            return await func(update, context, *args, **kwargs)

        return wrapped

    return decorator
