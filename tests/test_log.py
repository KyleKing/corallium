import logging
from typing import Any

import pytest
import structlog

from corallium.log import configure_logger, get_logger
from corallium.loggers.plain_printer import plain_printer
from corallium.loggers.structlog_logger import structlog_logger

from .configuration import DEFAULT_LOGGER


def not_implemented_printer(
    message: str,
    *,
    is_header: bool,
    _this_level: int,
    _is_text: bool,
    # Logger-specific parameters that need to be initialized with partial(...)
    **kwargs: Any,
) -> None:
    raise NotImplementedError('This logger is for testing hot-swapping')


def test_configure_logger_writer():
    logger = get_logger()
    configure_logger(log_level=logging.DEBUG, logger=plain_printer)
    logger.error('No problems here')

    configure_logger(log_level=logging.INFO, logger=not_implemented_printer)
    logger.debug("Won't raise an error")  # not sent to logger

    with pytest.raises(NotImplementedError):
        logger.info('Should raise an error')

    configure_logger(log_level=logging.DEBUG, logger=DEFAULT_LOGGER)  # Reset logger


def test_configure_logger_new(log):
    """Use the structlog_logger to capture log events."""
    logger = get_logger()
    configure_logger(log_level=logging.NOTSET, logger=structlog_logger)
    structlog.configure(processors=[structlog.stdlib.add_log_level])

    logger.text('TEXT')
    logger.text_debug('TEXT_DEBUG')
    logger.debug('DEBUG')
    logger.info('INFO', var=1)  # log.events[3]
    logger.warning('WARNING')
    logger.error('ERROR')

    try:
        _ = 1 // 0
    except Exception as exc:
        logger.exception('EXCEPTION')
        logger.warning('Attached Exception', exc_info=exc)  # log.events[7]

    assert [event['level'] for event in log.events] == [
        'info',  # text
        'debug',  # text_debug
        'debug',
        'info',
        'warning',
        'error',
        'error',  # Exception
        'warning',
    ]
    assert log.events[3] == {
        '_is_text': False,
        '_this_level': 20,
        'event': 'INFO',
        'is_header': False,
        'level': 'info',
        'var': 1,
    }
    assert str(log.events[7].pop('exc_info')) == str(
        ZeroDivisionError('integer division or modulo by zero'),
    )
    assert log.events[7] == {
        '_is_text': False,
        '_this_level': 30,
        'event': 'Attached Exception',
        'is_header': False,
        'level': 'warning',
    }
