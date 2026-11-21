import asyncio
import platform
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired

import pytest

from corallium.shell import capture_shell, capture_shell_async, run_shell

pytestmark = pytest.mark.skipif(platform.system() == 'Windows', reason='POSIX shell semantics')


def _capture_async(cmd: str, **kwargs) -> str:
    return asyncio.run(capture_shell_async(cmd, **kwargs))


def test_capture_shell_returns_both_streams_and_prints_each_line():
    printed: list[str] = []

    result = capture_shell('echo out; echo err >&2', printer=printed.append)

    assert result == 'out\nerr\n'
    assert printed == ['out', 'err']


@pytest.mark.parametrize('capture', [capture_shell, _capture_async])
def test_capture_runs_in_cwd(capture, tmp_path: Path):
    (tmp_path / 'marker.txt').write_text('')

    # capture_shell keeps the trailing newline and the async form strips it
    assert capture('ls', cwd=tmp_path).strip() == 'marker.txt'


def test_capture_shell_raises_with_the_output_on_failure():
    with pytest.raises(CalledProcessError) as exc:
        capture_shell('echo partial; exit 3')

    assert exc.value.returncode == 3  # noqa: PLR2004
    assert exc.value.output == 'partial\n'


def test_capture_shell_stops_a_chatty_command_at_the_timeout():
    # The deadline is checked between lines, so a command that prints nothing
    # (`sleep 5`) runs past it; this pins the case that does work.
    with pytest.raises(TimeoutExpired):
        capture_shell('while true; do echo tick; sleep 0.1; done', timeout=1)


def test_capture_shell_refuses_a_negative_timeout():
    with pytest.raises(ValueError, match='Negative timeouts'):
        capture_shell('true', timeout=-1)


def test_run_shell_runs_in_cwd_and_raises_on_failure(tmp_path: Path):
    run_shell('touch made', cwd=tmp_path)

    assert (tmp_path / 'made').is_file()
    with pytest.raises(CalledProcessError):
        run_shell('exit 2')


@pytest.mark.parametrize('run', [capture_shell, _capture_async, run_shell])
@pytest.mark.parametrize('cmd', ['echo a; echo b', 'echo $(whoami)', 'cat < /etc/hosts', 'true && true'])
def test_validate_cmd_refuses_injection_patterns(run, cmd):
    with pytest.raises(ValueError, match='dangerous pattern'):
        run(cmd, validate_cmd=True)


@pytest.mark.parametrize('run', [capture_shell, _capture_async, run_shell])
def test_validate_cmd_allows_a_plain_command(run):
    run('echo plain', validate_cmd=True)
