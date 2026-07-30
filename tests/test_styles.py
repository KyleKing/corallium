import logging

import pytest

from corallium.loggers.styles import LEVELS, NOTICE, STYLES, TRACE, Colors, get_level, get_name


@pytest.mark.parametrize(
    ('name', 'expected'),
    [
        ('critical', logging.CRITICAL),
        ('exception', logging.CRITICAL),
        ('fatal', logging.CRITICAL),
        ('error', logging.ERROR),
        ('warn', logging.WARNING),
        ('warning', logging.WARNING),
        ('notice', NOTICE),
        ('info', logging.INFO),
        ('debug', logging.DEBUG),
        ('trace', TRACE),
        ('Error', logging.ERROR),
        ('unrecognized', logging.NOTSET),
        ('', logging.NOTSET),
    ],
)
def test_get_level(name, expected):
    assert get_level(name=name) == expected


def test_levels_are_upper_case_and_resolvable():
    assert all(name == name.upper() for name in LEVELS)
    assert all(get_level(name=name) == level for name, level in LEVELS.items())


def test_get_level_orders_severity():
    names = ['trace', 'debug', 'info', 'notice', 'warning', 'error', 'critical']
    levels = [get_level(name=_) for _ in names]

    assert levels == sorted(levels)
    assert len(set(levels)) == len(levels)


@pytest.mark.parametrize(
    ('level', 'expected'),
    [
        (logging.CRITICAL, 'EXCEPTION'),
        (logging.ERROR, 'ERROR'),
        (logging.WARNING, 'WARNING'),
        (NOTICE, 'NOTICE'),
        (logging.INFO, 'INFO'),
        (logging.DEBUG, 'DEBUG'),
        (TRACE, 'TRACE'),
        (logging.NOTSET, 'NOTSET'),
        (11, ''),
    ],
)
def test_get_name(level, expected):
    assert get_name(level=level) == expected


@pytest.mark.parametrize(
    ('level', 'expected'),
    [
        (logging.CRITICAL, Colors.level_error),
        (logging.ERROR, Colors.level_error),
        (logging.WARNING, Colors.level_warn),
        (NOTICE, Colors.level_info),
        (logging.INFO, Colors.level_info),
        (logging.DEBUG, Colors.level_debug),
        (TRACE, Colors.level_debug),
        (logging.NOTSET, Colors.level_fallback),
    ],
)
def test_get_style(level, expected):
    assert STYLES.get_style(level=level) == expected
