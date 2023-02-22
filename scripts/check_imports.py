"""Check that all imports work as expected in the built package."""

from pprint import pprint

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

pprint(locals())  # noqa: T203
