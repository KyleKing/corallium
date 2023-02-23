"""Rich Printer."""

import logging
from datetime import datetime

from beartype import beartype
from beartype.typing import Any
from rich.console import Console
from rich.text import Text

from .styles import _LEVEL_TO_NAME, STYLES


@beartype
def rich_printer(  # noqa: CAC001
    message: str,
    *,
    is_header: bool,
    _this_level: int,
    _is_text: bool,
    # Logger-specific parameters that need to be initialized with partial(...)
    _console: Console,
    **kwargs: Any,
) -> None:
    """Generic log writer.."""
    text = Text()
    if _is_text:
        if is_header:
            print('')  # noqa: T201
        mesage_style = ('underline ' if is_header else '') + STYLES.message
        text.append(f'{message}', style=mesage_style)
    else:
        timestamp = kwargs.pop('timestamp', datetime.now())  # noqa: DTZ005
        text.append(f'{timestamp: <28} ', style=STYLES.timestamp)
        text.append('[', style=STYLES.timestamp)
        level_style = STYLES.get_style(level=_this_level)
        text.append(f"{_LEVEL_TO_NAME.get(_this_level, ''): <7}", style=level_style)
        text.append(']', style=STYLES.timestamp)
        text.append(f' {message}', style=STYLES.message)

    full_lines = []
    _keys_on_own_line = kwargs.pop('_keys_on_own_line', [])
    for key in _keys_on_own_line:
        line = kwargs.pop(key, None)
        if line:
            full_lines.append((key, line))
    for key, value in kwargs.items():
        text.append(f' {key}=', style=STYLES.key)
        text.append(f'{str(value)}', style=STYLES.value)
    _console.print(text)
    for key, line in full_lines:
        new_text = Text()
        new_text.append(f' ∟ {key}', style=STYLES.key)
        new_text.append(f': {line}', style=STYLES.value_own_line)
        _console.print(new_text)

    if _this_level == logging.CRITICAL:
        _console.print_exception(show_locals=True)
        # > or 'from rich.traceback import install; install(show_locals=True)'
