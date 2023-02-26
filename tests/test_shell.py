import json
import platform
import shlex
from subprocess import CalledProcessError  # nosec

import pytest

from corallium.shell import capture_shell, run_shell


def test_shell() -> None:
    """Example to run jq."""
    if platform.system() == 'Windows':
        pytest.skip('jq is not installed on Windows')

    jq = 'gojq'
    try:
        capture_shell(f'{jq} --help')
    except CalledProcessError:
        jq = 'jq'  # Fallback to jq
        capture_shell(f'{jq} --help')

    # Captured Shell Output
    data = {value: value * 1_000 for value in range(3)}
    capture_shell(f"echo '{json.dumps(data)}' | {jq}", printer=print)
    # Printed Shell Output ('With ANSII Color codes)
    run_shell(f"echo '{json.dumps(data)}' | {jq}")


def test_capture_shell_gibberish():
    with pytest.raises(CalledProcessError):
        capture_shell('gibberish')


def test_capture_shell(fake_process):
    process = 'git branch'
    expected = 'fake output'
    fake_process.register(shlex.split(process), stdout=[expected, ''])

    result = capture_shell(process)

    assert result == expected + '\n\n'
