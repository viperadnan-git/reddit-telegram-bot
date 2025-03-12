import logging
import os
import re
import shutil

logger = logging.getLogger(__name__)


def is_url(url: str) -> bool:
    return re.match(r"^https?://[^\s/$.?#].[^\s]*$", url) is not None


def delete_file(*args: str) -> None:
    for file in args:
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file)
        else:
            logger.debug(f"File {file} not found")
