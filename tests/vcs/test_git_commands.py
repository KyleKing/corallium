"""Tests for corallium.vcs._git_commands."""

from pathlib import Path

import pytest

from corallium.vcs._git_commands import git_blame_porcelain, git_ls_files, git_show_toplevel, zsplit


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
def test_zsplit(stdout: str, expected: list[str]):
    assert zsplit(stdout) == expected


def test_git_ls_files_in_repo():
    project_root = Path(__file__).parent.parent.parent
    result = git_ls_files(cwd=project_root)

    assert result is not None
    assert len(result) > 0
    assert any('corallium' in f for f in result)


def test_git_ls_files_returns_none_outside_repo(tmp_path: Path):
    assert git_ls_files(cwd=tmp_path) is None


def test_git_show_toplevel_in_repo():
    project_root = Path(__file__).parent.parent.parent
    result = git_show_toplevel(cwd=project_root)

    assert result is not None
    assert result.is_dir()


def test_git_show_toplevel_returns_none_outside_repo(tmp_path: Path):
    assert git_show_toplevel(cwd=tmp_path) is None


def test_git_blame_porcelain_returns_none_outside_repo(tmp_path: Path):
    dummy = tmp_path / 'dummy.py'
    dummy.write_text('hello')
    assert git_blame_porcelain(file_path=dummy, line=1, cwd=tmp_path) is None
