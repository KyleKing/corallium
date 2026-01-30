"""Tests for corallium.vcs._jj_commands."""

from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

from corallium.vcs._jj_commands import jj_file_annotate, jj_file_list, jj_git_remote_list, jj_root


def test_jj_file_list_parses_newlines():
    with patch('corallium.vcs._jj_commands.capture_shell', return_value='src/main.py\nREADME.md\n'):
        result = jj_file_list(cwd=Path('/fake'))

    assert result == ['src/main.py', 'README.md']


def test_jj_file_list_empty_output():
    with patch('corallium.vcs._jj_commands.capture_shell', return_value=''):
        result = jj_file_list(cwd=Path('/fake'))

    assert result == []


def test_jj_file_list_returns_none_on_failure():
    with patch('corallium.vcs._jj_commands.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        result = jj_file_list(cwd=Path('/fake'))

    assert result is None


def test_jj_root_parses_path():
    with patch('corallium.vcs._jj_commands.capture_shell', return_value='/home/user/repo\n'):
        result = jj_root(cwd=Path('/fake'))

    assert result == Path('/home/user/repo')


def test_jj_root_returns_none_on_failure():
    with patch('corallium.vcs._jj_commands.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        result = jj_root(cwd=Path('/fake'))

    assert result is None


def test_jj_git_remote_list():
    with patch('corallium.vcs._jj_commands.capture_shell', return_value='origin https://github.com/user/repo\n'):
        result = jj_git_remote_list(cwd=Path('/fake'))

    assert result == 'origin https://github.com/user/repo\n'


def test_jj_git_remote_list_returns_none_on_failure():
    with patch('corallium.vcs._jj_commands.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        result = jj_git_remote_list(cwd=Path('/fake'))

    assert result is None


def test_jj_file_annotate():
    annotate_output = 'qpvuntsm user@email.com 2024-01-01 line content\n'
    with patch('corallium.vcs._jj_commands.capture_shell', return_value=annotate_output):
        result = jj_file_annotate(file_path=Path('src/main.py'), line=1, cwd=Path('/fake'))

    assert result == annotate_output


def test_jj_file_annotate_returns_none_on_failure():
    with patch('corallium.vcs._jj_commands.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        result = jj_file_annotate(file_path=Path('src/main.py'), line=1, cwd=Path('/fake'))

    assert result is None
