"""Styles."""

import logging
from functools import singledispatchmethod

from beartype import beartype
from beartype.typing import Any


class Styles:
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

    @singledispatchmethod
    @beartype
    def get_style(self, *, level: Any) -> str:
        """Return the right style for the specified level."""
        raise NotImplementedError('Cannot negate a')

    @get_style.register
    @beartype
    def _(self, *, level: int) -> str:
        """Return the right style for the specified level."""
        return {
            logging.CRITICAL: self.level_error,
            logging.ERROR: self.level_error,
            logging.WARNING: self.level_warn,
            logging.INFO: self.level_info,
            logging.DEBUG: self.level_debug,
        }.get(level, self.level_fallback)

    @get_style.register
    @beartype
    def _(self, *, level: str) -> str:
        """Return the right style for the specified level."""
        level_value: int = {
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
        }.get(level, logging.NOTSET)
        return self.get_style(level=level_value)


_LEVEL_TO_NAME = {
    logging.CRITICAL: 'EXCEPTION',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET',
}
"""Mapping to logging level name.

https://docs.python.org/3.11/library/logging.html#logging-levels

"""

STYLES = Styles()
