from telegram import Update

from src.modules.bot_context import BotContext
from src.modules.decorators import args_required


@args_required(1, "Please provide a subreddit to join")
async def join_command_handler(update: Update, context: BotContext) -> None:
    subreddit = context.args[0].lower().strip()
    if subreddit.startswith("r/"):
        subreddit = subreddit[2:]
    try:
        context.reddit.subreddit(subreddit).subscribe()
        await update.message.reply_text(f"Joined r/{subreddit}")
    except Exception as e:
        await update.message.reply_text(f"Failed to join r/{subreddit}: {e}")


@args_required(1, "Please provide a subreddit to leave")
async def leave_command_handler(update: Update, context: BotContext) -> None:
    subreddit = context.args[0].lower().strip()
    if subreddit.startswith("r/"):
        subreddit = subreddit[2:]
    try:
        context.reddit.subreddit(subreddit).unsubscribe()
        await update.message.reply_text(f"Left r/{subreddit}")
    except Exception as e:
        await update.message.reply_text(f"Failed to leave r/{subreddit}: {e}")


async def subreddit_command_handler(update: Update, context: BotContext) -> None:
    # list all subreddits
    message = "Subscribed subreddits:\n"
    for subreddit in context.reddit.user.subreddits():
        message += f"r/{subreddit.display_name}\n"
    await update.message.reply_text(message)
