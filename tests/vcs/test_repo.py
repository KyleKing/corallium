"""Tests for corallium.vcs._repo."""

from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

from corallium.vcs._repo import (
    _get_jj_bookmark,
    _get_jj_remote_url,
    detect_vcs_kind,
    find_repo_root,
    get_repo_metadata,
)
from corallium.vcs._types import ForgeKind, VcsKind


def test_find_repo_root_git(tmp_path: Path):
    repo_dir = tmp_path / 'project'
    repo_dir.mkdir()
    (repo_dir / '.git').mkdir()

    assert find_repo_root(repo_dir) == repo_dir


def test_find_repo_root_jj(tmp_path: Path):
    repo_dir = tmp_path / 'project'
    repo_dir.mkdir()
    (repo_dir / '.jj').mkdir()

    assert find_repo_root(repo_dir) == repo_dir


def test_find_repo_root_from_nested_subdirectory(tmp_path: Path):
    repo_dir = tmp_path / 'project'
    nested = repo_dir / 'src' / 'pkg'
    nested.mkdir(parents=True)
    (repo_dir / '.git').mkdir()

    assert find_repo_root(nested) == repo_dir


def test_find_repo_root_returns_none_outside_repo(tmp_path: Path):
    isolated = tmp_path / 'no_repo'
    isolated.mkdir()

    assert find_repo_root(isolated) is None


def test_detect_vcs_kind_git(tmp_path: Path):
    (tmp_path / '.git').mkdir()
    assert detect_vcs_kind(tmp_path) == VcsKind.GIT


def test_detect_vcs_kind_jj(tmp_path: Path):
    (tmp_path / '.jj').mkdir()
    assert detect_vcs_kind(tmp_path) == VcsKind.JUJUTSU


def test_detect_vcs_kind_none(tmp_path: Path):
    assert detect_vcs_kind(tmp_path) is None


def test_get_repo_metadata_in_repo():
    project_root = Path(__file__).parent.parent.parent
    result = get_repo_metadata(project_root)

    assert result is not None
    assert result.root.is_dir()
    assert result.vcs == VcsKind.GIT


def test_get_repo_metadata_returns_none_outside_repo(tmp_path: Path):
    assert get_repo_metadata(tmp_path) is None


def test_get_repo_metadata_has_forge_info():
    project_root = Path(__file__).parent.parent.parent
    result = get_repo_metadata(project_root)

    assert result is not None
    assert result.forge in {ForgeKind.GITHUB, ForgeKind.GITLAB, ForgeKind.BITBUCKET, ForgeKind.UNKNOWN}


def test_get_jj_remote_url_parses_origin():
    raw = 'origin https://github.com/user/repo\nupstream https://github.com/other/repo\n'
    with patch('corallium.vcs._repo.jj_git_remote_list', return_value=raw):
        result = _get_jj_remote_url(cwd=Path('/fake'))

    assert result == 'https://github.com/user/repo'


def test_get_jj_remote_url_no_origin_returns_empty():
    raw = 'upstream https://github.com/other/repo\n'
    with patch('corallium.vcs._repo.jj_git_remote_list', return_value=raw):
        result = _get_jj_remote_url(cwd=Path('/fake'))

    assert not result


def test_get_jj_remote_url_returns_empty_on_none():
    with patch('corallium.vcs._repo.jj_git_remote_list', return_value=None):
        result = _get_jj_remote_url(cwd=Path('/fake'))

    assert not result


def test_get_jj_bookmark_returns_first():
    raw = 'main: qpvuntsm abc123\ndev: rlvkpnrz def456\n'
    with patch('corallium.vcs._repo.capture_shell', return_value=raw):
        result = _get_jj_bookmark(cwd=Path('/fake'))

    assert result == 'main'


def test_get_jj_bookmark_returns_empty_on_failure():
    with patch('corallium.vcs._repo.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        result = _get_jj_bookmark(cwd=Path('/fake'))

    assert not result


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
    get_repo_metadata.cache_clear()
