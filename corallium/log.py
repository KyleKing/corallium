"""Log."""

import logging
from datetime import datetime
from functools import cached_property, partial
from typing import runtime_checkable

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Protocol
from pydantic import BaseModel
from rich.console import Console
from rich.text import Text

_DEF_LEVEL = logging.ERROR


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

    @cached_property
    def level_lookup(self) -> Dict[int, str]:
        return {
            logging.CRITICAL: self.level_error,
            logging.ERROR: self.level_error,
            logging.WARNING: self.level_warn,
            logging.INFO: self.level_info,
            logging.DEBUG: self.level_debug,
        }


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

_STYLES = _Styles()


@runtime_checkable
class _LogCallable(Protocol):
    """Defined the kwargs accepted for a delegated task."""

    def __call__(
        self,
        message: str,
        *,
        _this_level: int,
        _console: Console,
        _log_level: int,
        is_header: bool,
        _is_text: bool,
    ) -> Any:
        ...


@beartype
def _rich_printer(
    message: str,
    *,
    _this_level: int,
    _console: Console,
    _log_level: int = _DEF_LEVEL,
    is_header: bool = False,
    _is_text: bool = False,
    _keys_on_own_line: Optional[List[str]] = None,
    **kwargs: Any,
) -> None:
    """Default log function."""
    if _this_level < _log_level:
        return

    text = Text()
    if _is_text:
        if is_header:
            print('')  # noqa: T201
        mesage_style = ('underline2 ' if is_header else '') + _STYLES.message
        text.append(f'{message}', style=mesage_style)
    else:
        timestamp = kwargs.pop('timestamp', datetime.now())  # noqa: DTZ005
        text.append(f'{timestamp: <28} ', style=_STYLES.timestamp)
        text.append('[', style=_STYLES.timestamp)
        level_style = _STYLES.level_lookup.get(_this_level)
        text.append(f"{_LEVEL_TO_NAME.get(_this_level, ''): <7}", style=level_style)
        text.append(']', style=_STYLES.timestamp)
        text.append(f' {message}', style=_STYLES.message)

    full_lines = []
    for key in _keys_on_own_line or []:
        line = kwargs.pop(key, None)
        if line:
            full_lines.append((key, line))
    for key, value in kwargs.items():
        text.append(f' {key}=', style=_STYLES.key)
        text.append(f'{str(value)}', style=_STYLES.value)
    _console.print(text)
    for key, line in full_lines:
        new_text = Text()
        new_text.append(f' ∟ {key}', style=_STYLES.key)
        new_text.append(f': {line}', style=_STYLES.value_own_line)
        _console.print(new_text)

    if _this_level == logging.CRITICAL:
        _console.print_exception(show_locals=True)
        # > or 'from rich.traceback import install; install(show_locals=True)'


class _LogSingleton(BaseModel):
    """Store pointer to log function."""

    log: _LogCallable

    class Config:
        arbitrary_types_allowed = True


_LOG_SINGLETON = _LogSingleton(log=partial(_rich_printer, _console=Console()))


class _Logger:

    @beartype
    def text(self, message: str, *, is_header: bool = False, **kwargs: Any) -> None:
        """Print the content without a leading timestamp.

        If writing to a file or not natively supported by the logger, will appear in the logs as level info.

        """
        self.info(message, **{'_is_text': True, 'is_header': is_header, **kwargs})

    @beartype
    def text_debug(self, message: str, *, is_header: bool = False, **kwargs: Any) -> None:
        """Variation on text that will appear as a debug log if not supported."""
        self.debug(message, **{'_is_text': True, 'is_header': is_header, **kwargs})

    @beartype
    def debug(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.DEBUG, **kwargs)

    @beartype
    def info(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.INFO, **kwargs)

    @beartype
    def warning(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.WARNING, **kwargs)

    @beartype
    def error(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.ERROR, **kwargs)

    @beartype
    def exception(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.CRITICAL, **kwargs)


@beartype
def configure_logger(log_level: int = _DEF_LEVEL) -> None:
    """Configure global logger."""
    _LOG_SINGLETON.log = partial(_rich_printer, _log_level=log_level, _console=Console())


@beartype
def get_logger() -> _Logger:
    """Retrieve global logger."""
    return _Logger()


logger = get_logger()
