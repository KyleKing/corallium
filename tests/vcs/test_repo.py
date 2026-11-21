"""Tests for corallium.vcs._repo."""

from pathlib import Path
from subprocess import CalledProcessError
from typing import Any
from unittest.mock import patch

import pytest

from corallium.shell import capture_shell
from corallium.vcs._repo import (
    _get_jj_bookmark,
    _get_jj_remote_url,
    detect_vcs_kind,
    find_repo_root,
    get_repo_metadata,
)
from corallium.vcs._types import ForgeKind, VcsKind


@pytest.mark.parametrize(
    ('marker', 'start', 'expected_kind'),
    [
        ('.git', '.', VcsKind.GIT),
        ('.jj', '.', VcsKind.JUJUTSU),
        ('.git', 'src/pkg', VcsKind.GIT),
        (None, '.', None),
    ],
)
def test_find_repo_root_and_kind(tmp_path: Path, marker: str | None, start: str, expected_kind: VcsKind | None):
    repo_dir = tmp_path / 'project'
    (repo_dir / start).mkdir(parents=True)
    if marker:
        (repo_dir / marker).mkdir()

    root = find_repo_root(repo_dir / start)

    assert root == (repo_dir if marker else None)
    assert detect_vcs_kind(repo_dir) == expected_kind


def test_get_repo_metadata_reads_a_real_git_repo(tmp_path: Path):
    capture_shell('git init -q -b trunk', cwd=tmp_path)
    capture_shell('git remote add origin https://github.com/user/repo.git', cwd=tmp_path)
    (tmp_path / 'nested').mkdir()
    get_repo_metadata.cache_clear()

    result = get_repo_metadata(tmp_path / 'nested')

    assert result is not None
    assert (result.root, result.vcs, result.branch) == (tmp_path, VcsKind.GIT, 'trunk')
    assert result.remote_url == 'https://github.com/user/repo.git'
    assert result.forge == ForgeKind.GITHUB
    get_repo_metadata.cache_clear()


def test_get_repo_metadata_without_a_remote_has_empty_url(tmp_path: Path):
    capture_shell('git init -q', cwd=tmp_path)
    get_repo_metadata.cache_clear()

    result = get_repo_metadata(tmp_path)

    assert result is not None
    assert result.remote_url == ''  # noqa: PLC1901 (the empty string, not None)
    get_repo_metadata.cache_clear()


def test_get_repo_metadata_returns_none_outside_repo(tmp_path: Path):
    assert get_repo_metadata(tmp_path) is None


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('origin https://github.com/user/repo\nupstream https://github.com/other/repo\n', 'https://github.com/user/repo'),
        ('upstream https://github.com/other/repo\norigin https://gitlab.com/u/r\n', 'https://gitlab.com/u/r'),
        ('upstream https://github.com/other/repo\n', ''),
        (None, ''),
    ],
)
def test_get_jj_remote_url(raw: str | None, expected: str):
    with patch('corallium.vcs._repo.jj_git_remote_list', return_value=raw):
        assert _get_jj_remote_url(cwd=Path('/fake')) == expected


@pytest.mark.parametrize(
    ('shell', 'expected'),
    [
        ({'return_value': 'main: qpvuntsm abc123\ndev: rlvkpnrz def456\n'}, 'main'),
        ({'return_value': '\n: orphan\nfeature: abc\n'}, 'feature'),
        ({'side_effect': CalledProcessError(1, 'jj')}, ''),
    ],
)
def test_get_jj_bookmark(shell: dict[str, Any], expected: str):
    with patch('corallium.vcs._repo.capture_shell', **shell):
        assert _get_jj_bookmark(cwd=Path('/fake')) == expected


def test_get_repo_metadata_jj_repo(tmp_path: Path):
    jj_root_path = tmp_path / 'jj_project'
    jj_root_path.mkdir()
    (jj_root_path / '.jj').mkdir()

    get_repo_metadata.cache_clear()
    with (
        patch('corallium.vcs._repo.git_show_toplevel', return_value=None),
        patch('corallium.vcs._repo.jj_root', return_value=jj_root_path),
        patch('corallium.vcs._repo._get_jj_remote_url', return_value='https://github.com/user/repo'),
        patch('corallium.vcs._repo._get_jj_bookmark', return_value='main'),
    ):
        result = get_repo_metadata(jj_root_path)

    assert result is not None
    assert result.vcs == VcsKind.JUJUTSU
    assert result.root == jj_root_path
    assert result.branch == 'main'
    assert result.remote_url == 'https://github.com/user/repo'
    assert result.forge == ForgeKind.GITHUB
    get_repo_metadata.cache_clear()
