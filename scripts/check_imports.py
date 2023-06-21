"""Check that all imports work as expected in the built package."""

import logging
from pprint import pprint
from timeit import timeit

from corallium.file_helpers import (
    COPIER_ANSWERS,
    LOCK,
    MKDOCS_CONFIG,
    PROJECT_TOML,
    delete_dir,
    delete_old_files,
    ensure_dir,
    get_relative,
    get_tool_versions,
    if_found_unlink,
    open_in_browser,
    read_lines,
    read_package_name,
    read_pyproject,
    read_yaml_file,
    sanitize_filename,
    tail_lines,
    trim_trailing_whitespace,
)
from corallium.log import configure_logger, get_logger, logger

# Compare logging performance
configure_logger(log_level=logging.DEBUG)
time_get = timeit(lambda: get_logger().info('123'), number=30)
time_import = timeit(lambda: logger.info('123'), number=30)
logger.text('get_logger', time=time_get)
logger.text('logger   .', time=time_import)
# > get_logger time=0.0038560839893762022
# > logger   . time=0.0030106669873930514

pprint(locals())  # noqa: T203
