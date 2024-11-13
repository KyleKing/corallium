"""File Helpers."""

from __future__ import annotations

import os
import shutil
import string
import time
import webbrowser
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from typing import Any

from .log import LOGGER
from .tomllib import tomllib


@lru_cache(maxsize=1)
def get_lock() -> Path:
    """Return path to dependency manager's lock file.

    Raises:
        FileNotFoundError: if a lock file can't be located

    """
    for pth in map(Path, ('uv.lock', 'poetry.lock')):
        if pth.is_file():
            return pth
    raise FileNotFoundError('Could not locate a known lock file type')


LOCK = Path('poetry.lock')
"""poetry.lock Path."""

PROJECT_TOML = Path('pyproject.toml')
"""pyproject.toml Path."""

COPIER_ANSWERS = Path('.copier-answers.yml')
"""Copier Answer file name."""

MKDOCS_CONFIG = Path('mkdocs.yml')
"""mkdocs.yml Path."""

# ----------------------------------------------------------------------------------------------------------------------
# Read General Text Files


def read_lines(path_file: Path, encoding: str | None = 'utf-8', errors: str | None = None) -> list[str]:
    """Read a file and split on newlines for later parsing.

    Args:
        path_file: path to the file
        encoding: defaults to 'utf-8'
        errors: defaults to None. Use 'ignore' if needed. Full documentation: https://docs.python.org/3.12/library/functions.html#open

    Returns:
        List[str]: lines of text as list

    """
    return path_file.read_text(encoding=encoding, errors=errors).splitlines() if path_file.is_file() else []


def tail_lines(path_file: Path, *, count: int) -> list[str]:
    """Tail a file for up to the last count (or full file) lines.

    Based on: https://stackoverflow.com/a/54278929

    > Tip: `file_size = fh.tell()` -or- `os.fstat(fh.fileno()).st_size` -or- return from `fh.seek(0, os.SEEK_END)`

    Args:
        path_file: path to the file
        count: maximum number of lines to return

    Returns:
        List[str]: lines of text as list

    """
    with path_file.open('rb') as f_h:
        rem_bytes = f_h.seek(0, os.SEEK_END)
        step_size = 1  # Initially set to 1 so that the last byte is read
        found_lines = 0
        while found_lines < count and rem_bytes >= step_size:
            rem_bytes = f_h.seek(-1 * step_size, os.SEEK_CUR)
            if f_h.read(1) == b'\n':
                found_lines += 1
            step_size = 2  # Increase so that repeats(read 1 / back 2)

        if rem_bytes < step_size:
            f_h.seek(0, os.SEEK_SET)
        return [line.rstrip('\r') for line in f_h.read().decode().split('\n')]


# ----------------------------------------------------------------------------------------------------------------------
# Read Specific File Types


def find_in_parents(*, name: str, cwd: Path | None = None) -> Path:
    """Return path to specific file by recursively searching in cwd and parents.

    Raises:
        FileNotFoundError: if not found

    """
    msg = f'Could not locate {name} in {cwd} or in any parent directory'
    start_path = (cwd or Path()).resolve() / name
    try:
        while not start_path.is_file():
            start_path = start_path.parents[1] / name
    except IndexError:
        raise FileNotFoundError(msg) from None
    return start_path


# TODO: Also read the `.mise.toml` file
def get_tool_versions(cwd: Path | None = None) -> dict[str, list[str]]:
    """Return versions from `.tool-versions` file."""
    tv_path = find_in_parents(name='.tool-versions', cwd=cwd)
    return {line.split(' ')[0]: line.split(' ')[1:] for line in tv_path.read_text().splitlines()}


@lru_cache(maxsize=5)
def read_pyproject(cwd: Path | None = None) -> Any:
    """Return the 'pyproject.toml' file contents.

    Raises:
        FileNotFoundError: if not found

    """
    toml_path = find_in_parents(name='pyproject.toml', cwd=cwd)
    try:
        pyproject_txt = toml_path.read_text(encoding='utf-8')
    except Exception as exc:
        msg = f'Could not locate: {toml_path}'
        raise FileNotFoundError(msg) from exc
    return tomllib.loads(pyproject_txt)  # pyright: ignore[reportAttributeAccessIssue]


@lru_cache(maxsize=5)
def read_package_name(cwd: Path | None = None) -> str:
    """Return the package name."""
    poetry_config = read_pyproject(cwd=cwd)
    return str(poetry_config['tool']['poetry']['name'])


def read_yaml_file(path_yaml: Path) -> Any:
    """Attempt to read the specified yaml file. Returns an empty dictionary if not found or a parser error occurs.

    > Note: suppresses all tags in the YAML file

    Args:
        path_yaml: path to the yaml file

    Returns:
        dictionary representation of the source file

    Raises:
        RuntimeError: when yaml dependency is missing

    """
    try:
        import yaml  # noqa: PLC0415 # lazy-load the optional dependency
    except ImportError as exc:
        raise RuntimeError("The 'calcipy[docs]' extras are missing") from exc

    # PLANNED: Refactor so that unsafe_load isn't necessary:
    #   read_text; remove any line containing ': !!python'; then yaml.loag

    # Based on: https://github.com/yaml/pyyaml/issues/86#issuecomment-380252434
    yaml.add_multi_constructor('', lambda _loader, _suffix, _node: None)
    yaml.add_multi_constructor('!', lambda _loader, _suffix, _node: None)
    yaml.add_multi_constructor('!!', lambda _loader, _suffix, _node: None)
    try:
        return yaml.unsafe_load(path_yaml.read_text())
    except (FileNotFoundError, KeyError) as exc:  # pragma: no cover
        LOGGER.warning('Unexpected read error', path_yaml=path_yaml, error=str(exc))
        return {}
    except yaml.constructor.ConstructorError:
        LOGGER.exception('Warning: burying poorly handled yaml error')
        return {}


# ----------------------------------------------------------------------------------------------------------------------
# General

ALLOWED_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits + '-_.'
"""Default string of acceptable characters in a filename."""


def sanitize_filename(filename: str, repl_char: str = '_', allowed_chars: str = ALLOWED_CHARS) -> str:
    """Replace all characters not in the `allow_chars` with `repl_char`.

    Args:
        filename: string filename (stem and suffix only)
        repl_char: replacement character. Default is `_`
        allowed_chars: all allowed characters. Default is `ALLOWED_CHARS`

    Returns:
        str: sanitized filename

    """
    return ''.join((char if char in allowed_chars else repl_char) for char in filename)


def trim_trailing_whitespace(pth: Path) -> None:
    """Trim trailing whitespace from the specified file.

    PLANNED: handle carriage returns

    """
    line_break = '\n'
    stripped = [line.rstrip(' ') for line in pth.read_text().split(line_break)]
    pth.write_text(line_break.join(stripped))


# ----------------------------------------------------------------------------------------------------------------------
# Manage Files and Directories


def if_found_unlink(path_file: Path) -> None:
    """Remove file if it exists. Function is intended to a doit action.

    Args:
        path_file: Path to file to remove

    """
    if path_file.is_file():
        LOGGER.text('Deleting', path_file=path_file)
        path_file.unlink()


def delete_old_files(dir_path: Path, *, ttl_seconds: int) -> None:
    """Delete old files within the specified directory.

    Args:
        dir_path: Path to directory to delete
        ttl_seconds: if last modified within this number of seconds, will not be deleted

    """
    for pth in dir_path.rglob('*'):
        if pth.is_file() and (time.time() - pth.stat().st_mtime) > ttl_seconds:
            pth.unlink()


def delete_dir(dir_path: Path) -> None:
    """Delete the specified directory from a doit task.

    Args:
        dir_path: Path to directory to delete

    """
    if dir_path.is_dir():
        LOGGER.text('Deleting', dir_path=dir_path)
        shutil.rmtree(dir_path)


def ensure_dir(dir_path: Path) -> None:
    """Make sure that the specified dir_path exists and create any missing folders from a doit task.

    Args:
        dir_path: Path to directory that needs to exists

    """
    LOGGER.text('Creating', dir_path=dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


def get_relative(full_path: Path, other_path: Path) -> Path | None:
    """Try to return the relative path between the two paths. None if no match.

    Args:
        full_path: the full path to use
        other_path: the path that the full_path may be relative to

    Returns:
        relative path

    """
    with suppress(ValueError):
        return full_path.relative_to(other_path)
    return None


# ----------------------------------------------------------------------------------------------------------------------
# Open Files


def open_in_browser(path_file: Path) -> None:  # pragma: no cover
    """Open the path in the default web browser.

    Args:
        path_file: Path to file

    """
    webbrowser.open(path_file.resolve().as_uri())
