from telegram.ext import ConversationHandler


class ConversationState:
    WAITING_FOR_AUTH_CODE = "waiting_for_auth_code"

    WAITING_FOR_TITLE = "waiting_for_title"
    WAITING_FOR_BODY = "waiting_for_body"
    WAITING_FOR_MEDIA = "waiting_for_media"
    WAITING_FOR_SUBREDDIT = "waiting_for_subreddit"
    WAITING_FOR_FLAIR = "waiting_for_flair"
    WAITING_FOR_POST_CONFIRMATION = "waiting_for_post_confirmation"
    END = ConversationHandler.END
