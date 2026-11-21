"""Tests for corallium.vcs._jj_commands."""

from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

from corallium.vcs._jj_commands import jj_file_annotate, jj_file_list, jj_git_remote_list, jj_root

_ANNOTATE = 'qpvuntsm user@email.com 2024-01-01 line content\n'


def _annotate(cwd: Path):
    return jj_file_annotate(file_path=Path('src/main.py'), line=1, cwd=cwd)


@pytest.mark.parametrize(
    ('command', 'output', 'expected'),
    [
        (jj_file_list, 'src/main.py\nREADME.md\n', ['src/main.py', 'README.md']),
        (jj_file_list, '', []),
        (jj_root, '/home/user/repo\n', Path('/home/user/repo')),
        (jj_git_remote_list, 'origin https://github.com/user/repo\n', 'origin https://github.com/user/repo\n'),
        (_annotate, _ANNOTATE, _ANNOTATE),
    ],
)
def test_parses_jj_output(command, output, expected):
    with patch('corallium.vcs._jj_commands.capture_shell', return_value=output):
        assert command(cwd=Path('/fake')) == expected


@pytest.mark.parametrize('command', [jj_file_list, jj_root, jj_git_remote_list, _annotate])
def test_a_failed_jj_call_returns_none(command):
    with patch('corallium.vcs._jj_commands.capture_shell', side_effect=CalledProcessError(1, 'jj')):
        assert command(cwd=Path('/fake')) is None
