from pathlib import Path
from loguru import logger
import shutil


def clear_directory(directory_path: str):
    """Delete all direcotry

    Args:
        directory_path (str): directory
    """
    try:
        shutil.rmtree(directory_path)
    except OSError as e:
        logger.error("Error: %s - %s." % (e.filename, e.strerror))
