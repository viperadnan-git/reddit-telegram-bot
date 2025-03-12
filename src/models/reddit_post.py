from dataclasses import dataclass

from src.enums import MediaType


@dataclass
class RedditPost:
    title: str | None = None
    media_url: str | None = None
    media_path: str | None = None
    media_type: MediaType | None = None
    body: str | None = None
    subreddit: str | None = None
    flair_id: str | None = None
