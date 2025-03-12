from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.enums import MediaType


@dataclass
class RedditPost:
    title: Optional[str] = None
    media_url: Optional[str] = None
    media_path: Optional[Path] = None
    media_type: Optional[MediaType] = None
    body: Optional[str] = None
    subreddit: Optional[str] = None
    flair_id: Optional[str] = None
