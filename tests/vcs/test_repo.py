"""Tests for corallium.vcs._repo."""

from pathlib import Path

from corallium.vcs._repo import detect_vcs_kind, find_repo_root, get_repo_metadata
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
