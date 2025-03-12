from uuid import uuid4

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.config import Config
from src.constant import ConversationState
from src.enums import MediaType
from src.handlers.common import cancel_handler
from src.models.reddit_post import RedditPost
from src.modules.bot_context import BotContext
from src.modules.decorators import restricted
from src.utils import delete_file, is_url


async def get_telegram_file_url(message: Message) -> tuple[str, MediaType, str]:
    file = None
    media_type = None
    file_path = None
    if message.video:
        file = await message.video.get_file()
        media_type = MediaType.VIDEO
        ext = message.video.file_name.split(".")[-1]
        file_path = Config.TMP_DIR / f"video_{uuid4()}.{ext}"
    elif message.photo:
        file = await message.photo[-1].get_file()
        media_type = MediaType.IMAGE
        file_path = Config.TMP_DIR / f"image_{uuid4()}.jpg"
    elif message.document:
        file = await message.document.get_file()
        media_type = (
            MediaType.IMAGE
            if message.document.mime_type.startswith("image")
            else (
                MediaType.VIDEO
                if message.document.mime_type.startswith("video")
                else MediaType.UNKNOWN
            )
        )
        ext = message.document.file_path.split(".")[-1]
        file_path = Config.TMP_DIR / f"document_{uuid4()}.{ext}"
    return file.file_path, media_type, file_path


async def ask_for_title(update: Update, context: BotContext) -> None:
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please enter the title of the post\n\n<i>Send /skip to skip this step</i>",
    )
    return ConversationState.WAITING_FOR_TITLE


async def ask_for_body(update: Update, context: BotContext) -> None:
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please enter the body of the post\n\n<i>Send /skip to skip this step</i>",
    )
    return ConversationState.WAITING_FOR_BODY


async def ask_for_media(update: Update, context: BotContext) -> None:
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please enter the media of the post\n\n<i>Send /skip to skip this step</i>",
    )
    return ConversationState.WAITING_FOR_MEDIA


async def ask_for_subreddit(update: Update, context: BotContext) -> None:
    keyboard = []
    for subreddit in context.reddit.user.subreddits():
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"r/{subreddit.display_name}",
                    callback_data=f"p_subreddit:{subreddit.display_name}",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please select the subreddit",
        reply_markup=reply_markup,
    )
    return ConversationState.WAITING_FOR_SUBREDDIT


async def ask_for_post_confirmation(update: Update, context: BotContext) -> None:
    post = context.user_data["post"]

    await update.callback_query.edit_message_text(
        text=f"Title: {post.title}\nBody: {post.body}\nMedia: {bool(post.media_url)}\nSubreddit: {post.subreddit}",
    )

    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="p_confirm:no"),
            InlineKeyboardButton("Yes", callback_data="p_confirm:yes"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text="Are you sure you want to post this?",
        reply_markup=reply_markup,
    )
    return ConversationState.WAITING_FOR_POST_CONFIRMATION


async def ask_for_flair(update: Update, context: BotContext) -> None:
    post = context.user_data["post"]

    flair_options = list(context.reddit.subreddit(post.subreddit).flair.link_templates)

    keyboard = []
    for flair in flair_options:
        keyboard.append(
            [
                InlineKeyboardButton(
                    flair["text"], callback_data=f"p_flair:{flair['id']}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="Please select the flair for the post", reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please select the flair for the post",
            reply_markup=reply_markup,
        )
    return ConversationState.WAITING_FOR_FLAIR


@restricted
async def post_message_handler(update: Update, context: BotContext) -> None:
    post = RedditPost()
    context.user_data["post"] = post

    if update.message.video or update.message.photo or update.message.document:
        file_url, media_type, file_path = await get_telegram_file_url(update.message)

        if media_type == MediaType.UNKNOWN:
            await context.bot.send_message(
                chat_id=update.message.chat_id, text="Unsupported media type"
            )
            return ConversationState.END

        post.media_url = file_url
        post.media_type = media_type
        post.media_path = file_path

        caption = update.message.caption or update.message.text
        if caption:
            post.title = caption
            return await ask_for_body(update, context)
        else:
            return await ask_for_title(update, context)
    else:
        message_text = update.message.text

        if is_url(message_text):
            post.media_url = message_text
            return await ask_for_title(update, context)
        else:
            post.title = message_text
            return await ask_for_media(update, context)


async def post_title_handler(update: Update, context: BotContext) -> None:
    caption = update.message.caption or update.message.text
    post = context.user_data["post"]

    post.title = caption
    return await ask_for_body(update, context)


async def post_body_handler(update: Update, context: BotContext) -> None:
    post = context.user_data["post"]

    if "/skip" == update.message.text:
        return await ask_for_subreddit(update, context)

    post.body = update.message.text
    return await ask_for_subreddit(update, context)


async def post_media_handler(update: Update, context: BotContext) -> None:
    post = context.user_data["post"]

    if "/skip" == update.message.text:
        return await ask_for_body(update, context)

    if update.message.text and is_url(update.message.text):
        post.media_url = update.message.text
        post.media_type = MediaType.URL
        return await ask_for_body(update, context)

    media_url, media_type, file_path = await get_telegram_file_url(update.message)

    if media_type == MediaType.UNKNOWN:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Unsupported media type, please try again",
        )
        return ConversationState.WAITING_FOR_MEDIA

    post.media_url = media_url
    post.media_type = media_type
    post.media_path = file_path
    return await ask_for_body(update, context)


async def post_subreddit_handler(update: Update, context: BotContext) -> None:
    subreddit_name = update.callback_query.data.split(":")[1]
    post = context.user_data["post"]
    post.subreddit = subreddit_name

    post_requirements = context.reddit.subreddit(post.subreddit).post_requirements()
    if post_requirements.get("is_flair_required"):
        return await ask_for_flair(update, context)

    return await ask_for_post_confirmation(update, context)


async def post_flair_handler(update: Update, context: BotContext) -> None:
    flair_id = update.callback_query.data.split(":")[1]
    post = context.user_data["post"]
    post.flair_id = flair_id
    return await ask_for_post_confirmation(update, context)


def download_media(url: str, output_path: str) -> str:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return output_path


async def post_post_confirmation_handler(update: Update, context: BotContext) -> None:
    callback_query = update.callback_query
    if callback_query.data == "p_confirm:no":
        await callback_query.message.edit_text(text="Post cancelled")
        return ConversationState.END

    post = context.user_data["post"]
    message = await update.callback_query.message.edit_text(text="Posting...")

    if post.media_type:
        if post.media_type == MediaType.URL:
            media_path = post.media_url
        else:
            media_path = download_media(post.media_url, post.media_path)

    if post.media_type == MediaType.IMAGE:
        context.reddit.subreddit(post.subreddit).submit_image(
            title=post.title, image_path=media_path, flair_id=post.flair_id
        )
    elif post.media_type == MediaType.VIDEO:
        context.reddit.subreddit(post.subreddit).submit_video(
            title=post.title, video_path=media_path, flair_id=post.flair_id
        )
    elif post.media_type == MediaType.URL:
        context.reddit.subreddit(post.subreddit).submit(
            title=post.title, url=post.media_url, flair_id=post.flair_id
        )
    else:
        context.reddit.subreddit(post.subreddit).submit(
            title=post.title, selftext=post.body, flair_id=post.flair_id
        )

    delete_file(post.media_path)

    await message.edit_text(text="Post posted successfully")
    return ConversationState.END


def get_post_handler() -> ConversationHandler:
    return ConversationHandler(
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
                CallbackQueryHandler(post_subreddit_handler, pattern="^p_subreddit:")
            ],
            ConversationState.WAITING_FOR_FLAIR: [
                CallbackQueryHandler(post_flair_handler, pattern="^p_flair:")
            ],
            ConversationState.WAITING_FOR_POST_CONFIRMATION: [
                CallbackQueryHandler(
                    post_post_confirmation_handler, pattern="^p_confirm:"
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
        ],
    )
