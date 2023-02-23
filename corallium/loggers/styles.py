"""Styles."""

import logging

from beartype import beartype


class _Styles:
    """Inspired by `structlog` and used in `tail-jsonl`.

    https://rich.readthedocs.io/en/latest/style.html

    """

    timestamp: str = '#7b819d'  # originally 'dim grey'
    message: str = 'bold #a9b1d6'

    level_error: str = 'red'
    level_warn: str = 'yellow'
    level_info: str = 'green'  # #b9f27c
    level_debug: str = 'dim blue'

    key: str = '#02bcce'
    value: str = '#ab8ce3'
    value_own_line: str = ''

    @beartype
    def get_style(self, *, level: int) -> str:
        return {
            logging.CRITICAL: self.level_error,
            logging.ERROR: self.level_error,
            logging.WARNING: self.level_warn,
            logging.INFO: self.level_info,
            logging.DEBUG: self.level_debug,
        }.get(level, '')


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

STYLES = _Styles()
