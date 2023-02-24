"""Styles."""

import logging

from pydantic import BaseModel
from beartype import beartype


class Styles(BaseModel):
    """Inspired by `loguru` and `structlog` and used in `tail-jsonl`.

    https://rich.readthedocs.io/en/latest/style.html

    Inspired by: https://github.com/Delgan/loguru/blob/07f94f3c8373733119f85aa8b9ca05ace3325a4b/loguru/_defaults.py#L31-L73

    And: https://github.com/hynek/structlog/blob/bcfc7f9e60640c150bffbdaeed6328e582f93d1e/src/structlog/dev.py#L126-L141

    """  # noqa: E501

    timestamp: str = '#7b819d'  # dim grey
    message: str = 'bold #a9b1d6'  # light grey

    level_error: str = '#24283b'  # red
    level_warn: str = 'yellow'
    level_info: str = 'green'
    level_debug: str = 'dim blue'
    level_fallback: str = '#af2ab4'  # hot pink

    key: str = '#02bcce'  # greem
    value: str = '#ab8ce3'  # light purple
    value_own_line: str = '#ab8ce3'

    @beartype
    def get_style(self, *, level: int) -> str:
        """Return the right style for the specified level."""
        return {
            logging.CRITICAL: self.level_error,
            logging.ERROR: self.level_error,
            logging.WARNING: self.level_warn,
            logging.INFO: self.level_info,
            logging.DEBUG: self.level_debug,
        }.get(level, self.level_fallback)


@beartype
def get_level(*, name: str) -> int:
    """Return the logging level based on the provided name."""
    return {
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'WARN': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }.get(name.upper(), logging.NOTSET)


@beartype
def get_name(*, level: int) -> str:
    """Return the logging name based on the provided level.

    https://docs.python.org/3.11/library/logging.html#logging-levels

    """
    return {
        logging.CRITICAL: 'EXCEPTION',
        logging.ERROR: 'ERROR',
        logging.WARNING: 'WARNING',
        logging.INFO: 'INFO',
        logging.DEBUG: 'DEBUG',
        logging.NOTSET: 'NOTSET',
    }.get(level, '')


STYLES = Styles()
