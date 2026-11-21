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


@pytest.mark.parametrize(
    ('kwargs', 'expected'),
    [
        pytest.param(
            {'message': 'boom', '_this_level': logging.CRITICAL, '_level_name': 'fatal'},
            '2026-01-01T00:00:00Z         [FATAL  ] boom\n',
            id='level name override',
        ),
        pytest.param(
            {'message': 'enter', '_this_level': TRACE, 'user': 'ada', 'n': 3},
            '2026-01-01T00:00:00Z         [TRACE  ] enter user=ada n=3\n',
            id='level from number, then key=value pairs in order',
        ),
        pytest.param(
            {
                'message': 'ran',
                '_this_level': logging.INFO,
                '_keys_on_own_line': ['out', 'err'],
                'out': 'a\nb',
                'err': '',
            },
            '2026-01-01T00:00:00Z         [INFO   ] ran\n ∟ out: a\nb\n',
            id='own-line keys follow the record, and an empty one is dropped',
        ),
        pytest.param(
            {'message': 'boom', '_this_level': logging.CRITICAL},
            '2026-01-01T00:00:00Z         [EXCEPTN] boom\n',
            id='critical outside an except block prints no traceback',
        ),
    ],
)
def test_rendered_record(printer, kwargs, expected):
    assert printer(**kwargs) == expected


def test_text_mode_prints_only_the_message_and_a_header_gap(capsys):
    console = Console(width=200)
    console.begin_capture()
    rich_printer('Title', is_header=True, _this_level=logging.INFO, _is_text=True, _console=console, _styles=STYLES)
    rich_printer('body', is_header=False, _this_level=logging.INFO, _is_text=True, _console=console, _styles=STYLES)

    assert console.end_capture() == 'Title\nbody\n'
    assert capsys.readouterr().out == '\n'


def test_critical_with_an_active_exception(printer):
    result = ''
    try:
        _ = 1 // 0
    except ZeroDivisionError:
        result = printer(message='boom', _this_level=logging.CRITICAL)

    assert 'Traceback' in result
    assert 'ZeroDivisionError' in result
