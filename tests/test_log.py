import logging

import pytest
import structlog
from beartype import beartype
from beartype.typing import Any

from corallium.log import configure_logger, get_logger
from corallium.loggers.writer import writer


def test_configure_logger_writer():
    logger = get_logger()
    configure_logger(log_level=logging.INFO, logger=writer)
    logger.debug('Should raise an error')  # not sent to logger

    with pytest.raises(NotImplementedError):
        logger.info('Should raise an error')

    configure_logger(logger=None)  # Reset logger


@beartype
def structlog_logger(
    message: str,
    *,
    is_header: bool,
    _this_level: int,
    _is_text: bool,
    # Logger-specific parameters that need to be initialized with partial(...)
    **kwargs: Any,
) -> None:
    logger = structlog.get_logger()
    log = {
        logging.CRITICAL: logger.exception,
        logging.ERROR: logger.error,
        logging.WARNING: logger.warning,
        logging.INFO: logger.info,
        logging.DEBUG: logger.debug,
        logging.NOTSET: logger.debug,
    }.get(_this_level, logger.msg)
    log(message, is_header=is_header, _this_level=_this_level, _is_text=_is_text, **kwargs)


def test_configure_logger_new(log):
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
