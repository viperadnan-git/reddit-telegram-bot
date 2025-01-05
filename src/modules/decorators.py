from functools import wraps

from src.modules.reddit_manager import RedditManager


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if not context.reddit:
            await update.message.reply_text("You need to authenticate with Reddit first. Use /login to do that.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
