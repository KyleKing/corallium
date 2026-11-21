"""Tests for corallium.vcs._git_commands."""

from pathlib import Path

import pytest

from corallium.shell import capture_shell
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


def test_git_commands_in_a_repo(tmp_path: Path):
    capture_shell('git init -q', cwd=tmp_path)
    (tmp_path / 'tracked.py').write_text('hello\n', encoding='utf-8')
    capture_shell('git add tracked.py', cwd=tmp_path)
    capture_shell('git -c user.name=A -c user.email=a@example.com commit -qm init', cwd=tmp_path)
    (tmp_path / 'sub').mkdir()

    assert git_ls_files(cwd=tmp_path) == ['tracked.py']
    assert git_show_toplevel(cwd=tmp_path / 'sub') == tmp_path
    blame = git_blame_porcelain(file_path=tmp_path / 'tracked.py', line=1, cwd=tmp_path)
    assert blame is not None
    assert 'author A' in blame


@pytest.mark.parametrize(
    'command',
    [
        lambda cwd: git_ls_files(cwd=cwd),
        lambda cwd: git_show_toplevel(cwd=cwd),
        lambda cwd: git_blame_porcelain(file_path=cwd / 'dummy.py', line=1, cwd=cwd),
    ],
)
def test_git_commands_return_none_outside_a_repo(tmp_path: Path, command):
    (tmp_path / 'dummy.py').write_text('hello')

    assert command(tmp_path) is None
