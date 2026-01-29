"""Test file_search."""

from pathlib import Path

import pytest

from corallium.file_search import (
    _filter_files,
    _get_all_files,
    _get_default_ignore_patterns,
    _walk_files,
    _zsplit,
    find_project_files,
    find_project_files_by_suffix,
)

from .configuration import TEST_DATA_DIR

SAMPLE_README_DIR = TEST_DATA_DIR / 'sample_doc_files'


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
def test_zsplit_splits_on_null_bytes(stdout: str, expected: list[str]) -> None:
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


def test_find_project_files_by_suffix_with_sample_data() -> None:
    expected_suffixes = ['', 'md']

    result = find_project_files_by_suffix(SAMPLE_README_DIR, ignore_patterns=[])

    assert len(result) != 0
    assert sorted(result.keys()) == expected_suffixes
    assert result[''][0].name == '.dotfile'


def test_walk_files_basic(tmp_path: Path) -> None:
    (tmp_path / 'file1.py').write_text('content')
    (tmp_path / 'subdir').mkdir()
    (tmp_path / 'subdir' / 'file2.py').write_text('content')

    files = _walk_files(cwd=tmp_path)

    assert 'file1.py' in files
    assert 'subdir/file2.py' in files


def test_get_all_files_fallback(tmp_path: Path) -> None:
    (tmp_path / 'test.py').write_text('content')

    files, used_git = _get_all_files(cwd=tmp_path)

    assert not used_git
    assert 'test.py' in files


def test_default_ignore_patterns_applied(tmp_path: Path) -> None:
    (tmp_path / '__pycache__').mkdir()
    (tmp_path / '__pycache__' / 'cached.pyc').write_text('')
    (tmp_path / 'source.py').write_text('# code')

    files = find_project_files(tmp_path, ignore_patterns=[])

    file_names = [f.name for f in files]
    assert 'source.py' in file_names
    assert 'cached.pyc' not in file_names


@pytest.mark.parametrize(
    'expected_pattern',
    [
        '**/__pycache__/**',
        '**/*.pyc',
        '**/.git/**',
        '**/.jj/**',
        '**/node_modules/**',
        '**/.venv/**',
        '**/venv/**',
        '**/.pytest_cache/**',
        '**/.mypy_cache/**',
        '**/.ruff_cache/**',
        '**/dist/**',
        '**/build/**',
    ],
)
def test_get_default_ignore_patterns(expected_pattern: str) -> None:
    patterns = _get_default_ignore_patterns()
    assert expected_pattern in patterns
