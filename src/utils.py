import re


def is_url(url: str) -> bool:
    return re.match(r"^https?://[^\s/$.?#].[^\s]*$", url) is not None