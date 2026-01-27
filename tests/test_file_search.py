"""Test file_search."""

from pathlib import Path

import pytest
from beartype.typing import List

from corallium.file_search import (
    _filter_files,
    _zsplit,
    find_project_files,
    find_project_files_by_suffix,
)


@pytest.mark.parametrize(
    ('stdout', 'expected'),
    [
        ('a\0b\0c\0', ['a', 'b', 'c']),
        ('single\0', ['single']),
        ('', []),
        ('\0\0', []),
        ('no-null', ['no-null']),
    ],
)
def test_zsplit_splits_on_null_bytes(stdout: str, expected: List[str]) -> None:
    assert _zsplit(stdout) == expected


def test_filter_files_no_patterns_returns_all() -> None:
    files = ['a.py', 'b.txt', 'c.md']

    result = _filter_files(files, [])

    assert result == files


def test_filter_files_by_extension(tmp_path: Path) -> None:
    (tmp_path / 'a.py').touch()
    (tmp_path / 'b.pyc').touch()

    files = [str(tmp_path / 'a.py'), str(tmp_path / 'b.pyc')]

    result = _filter_files(files, ['*.pyc'])

    assert len(result) == 1
    assert 'a.py' in result[0]


def test_filter_files_by_directory_pattern(tmp_path: Path) -> None:
    cache_dir = tmp_path / '__pycache__'
    cache_dir.mkdir()
    (cache_dir / 'module.pyc').touch()
    (tmp_path / 'main.py').touch()

    files = [
        str(cache_dir / 'module.pyc'),
        str(tmp_path / 'main.py'),
    ]

    result = _filter_files(files, ['*/__pycache__/*'])

    assert len(result) == 1
    assert 'main.py' in result[0]


def test_find_project_files_in_git_repo() -> None:
    project_root = Path(__file__).parent.parent

    result = find_project_files(project_root, ignore_patterns=['*.pyc'])

    assert len(result) > 0
    assert all(isinstance(p, Path) for p in result)
    assert any('corallium' in str(p) for p in result)


def test_find_project_files_respects_ignore_patterns() -> None:
    project_root = Path(__file__).parent.parent

    result = find_project_files(project_root, ignore_patterns=['*.md'])

    assert not any(str(p).endswith('.md') for p in result)


def test_find_project_files_by_suffix_groups_by_extension() -> None:
    project_root = Path(__file__).parent.parent

    result = find_project_files_by_suffix(project_root)

    assert 'py' in result
    assert 'toml' in result
    assert all(p.suffix == '.py' for p in result.get('py', []))


def test_find_project_files_by_suffix_respects_ignore_patterns() -> None:
    project_root = Path(__file__).parent.parent

    result = find_project_files_by_suffix(
        project_root,
        ignore_patterns=['*.lock'],
    )

    assert 'lock' not in result
