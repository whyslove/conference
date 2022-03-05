from pathlib import Path
from loguru import logger
import shutil


def clear_directory(directory_path: str):
    import os

    f = open("123.txt", "w")
    try:
        shutil.rmtree(directory_path)
    except OSError as e:
        logger.error("Error: %s - %s." % (e.filename, e.strerror))
