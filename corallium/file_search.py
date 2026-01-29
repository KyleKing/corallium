"""Find files using git.

Migrated from calcipy.file_search for git-based file discovery.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from corallium.log import LOGGER
from corallium.shell import capture_shell


def _zsplit(stdout: str) -> list[str]:
    """Split output from git when used with `-z`.

    Args:
        stdout: Output from git command with null-byte separators

    Returns:
        List of non-empty strings split on null bytes

    """
    return [item for item in stdout.split('\0') if item]


def _get_all_files(*, cwd: Path) -> list[str]:
    """Get all files using git.

    Modified from pre-commit's get_all_files to accept cwd parameter. Based on:
    https://github.com/pre-commit/pre-commit/blob/488b1999f36cac62b6b0d9bc8eae99418ae5c226/pre_commit/git.py#L153

    Args:
        cwd: Current working directory to pass to git command

    Returns:
        List of all file paths relative to the cwd

    """
    return _zsplit(capture_shell('git ls-files -z', cwd=cwd))


def _filter_files(rel_filepaths: list[str], ignore_patterns: list[str]) -> list[str]:
    """Filter a list of string file paths with specified ignore patterns in glob syntax.

    Args:
        rel_filepaths: List of string file paths
        ignore_patterns: Glob ignore patterns (e.g., ['*.pyc', '__pycache__/*'])

    Returns:
        List of all non-ignored file path names

    """
    if ignore_patterns:
        matches = []
        for fp in rel_filepaths:
            pth = Path(fp).resolve()
            if not any(pth.match(pat) for pat in ignore_patterns):
                matches.append(fp)
        return matches
    return rel_filepaths


def find_project_files(path_project: Path, ignore_patterns: list[str]) -> list[Path]:
    """Find project files in git version control.

    Note: Uses git ls-files and verifies that each file exists.
    Requires git to be installed and the directory to be a git repository.

    Args:
        path_project: Path to the project directory
        ignore_patterns: Glob ignore patterns

    Returns:
        List of Path objects for all tracked, non-ignored files

    Example:
        >>> from pathlib import Path
        >>> files = find_project_files(
        ...     Path('.'),
        ...     ignore_patterns=['*.pyc', '__pycache__/*', '.git/*']
        ... )

    """
    file_paths = []
    rel_filepaths = _get_all_files(cwd=path_project)
    filtered_rel_files = _filter_files(rel_filepaths=rel_filepaths, ignore_patterns=ignore_patterns)
    for rel_file in filtered_rel_files:
        path_file = path_project / rel_file
        if path_file.is_file():
            file_paths.append(path_file)
        else:  # pragma: no cover
            LOGGER.warning('Could not find the specified file', path_file=path_file)
    return file_paths


def find_project_files_by_suffix(
    path_project: Path,
    *,
    ignore_patterns: list[str] | None = None,
) -> dict[str, list[Path]]:
    """Find project files in git version control grouped by file extension.

    Note: Uses git ls-files and verifies that each file exists.
    Requires git to be installed and the directory to be a git repository.

    Args:
        path_project: Path to the project directory
        ignore_patterns: Glob ignore patterns (optional)

    Returns:
        Dictionary where keys are file extensions (without leading dot) and
        values are lists of Path objects with that extension

    Example:
        >>> from pathlib import Path
        >>> files_by_ext = find_project_files_by_suffix(
        ...     Path('.'),
        ...     ignore_patterns=['*.pyc', '__pycache__/*']
        ... )
        >>> py_files = files_by_ext.get('py', [])
        >>> md_files = files_by_ext.get('md', [])

    """
    file_lookup: dict[str, list[Path]] = defaultdict(list)
    for path_file in find_project_files(path_project, ignore_patterns or []):
        file_lookup[path_file.suffix.lstrip('.')].append(path_file)
    return dict(file_lookup)
