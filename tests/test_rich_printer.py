import logging

import pytest
from rich.console import Console

from corallium.loggers.rich_printer import _format_level, rich_printer
from corallium.loggers.styles import STYLES, TRACE


@pytest.fixture
def printer():
    console = Console(width=200)

    def _print(**kwargs) -> str:
        console.begin_capture()
        rich_printer(
            is_header=False,
            _is_text=False,
            _console=console,
            _styles=STYLES,
            timestamp='2026-01-01T00:00:00Z',
            **kwargs,
        )
        return console.end_capture()

    return _print


@pytest.mark.parametrize(
    ('name', 'expected'),
    [
        ('EXCEPTION', 'EXCEPTN'),
        ('CRITICAL', 'CRITICL'),
        ('WARNING', 'WARNING'),
        ('trace', 'TRACE  '),
        ('info', 'INFO   '),
    ],
)
def test_format_level(name, expected):
    assert _format_level(name) == expected


def test_level_name_override(printer):
    result = printer(message='boom', _this_level=logging.CRITICAL, _level_name='fatal')

    assert '[FATAL  ]' in result


def test_level_name_defaults_to_the_level(printer):
    result = printer(message='enter', _this_level=TRACE)

    assert '[TRACE  ]' in result


def test_critical_without_an_active_exception(printer):
    """Rich raises when asked for a traceback outside an `except:` block."""
    result = printer(message='boom', _this_level=logging.CRITICAL)

    assert '[EXCEPTN] boom' in result
    assert 'Traceback' not in result


def test_critical_with_an_active_exception(printer):
    result = ''
    try:
        _ = 1 // 0
    except ZeroDivisionError:
        result = printer(message='boom', _this_level=logging.CRITICAL)

    assert 'Traceback' in result
    assert 'ZeroDivisionError' in result
