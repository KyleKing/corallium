"""Run shell commands."""

from __future__ import annotations

import asyncio
import subprocess  # noqa: S404
import sys
from collections.abc import Callable
from pathlib import Path
from time import time

from .log import LOGGER


def capture_shell(
    cmd: str,
    *,
    timeout: int | None = 120,
    cwd: Path | None = None,
    printer: Callable[[str], None] | None = None,
) -> str:
    """Run shell command, return the output, and optionally print in real time.

    WARNING: This function uses shell=True which can be a security risk.
    Only use with trusted input.

    Inspired by: https://stackoverflow.com/a/38745040/3219667

    Args:
        cmd: shell command
        timeout: process timeout in seconds. Defaults to 2 minutes. Use None for no timeout.
        cwd: optional path for shell execution
        printer: optional callable to output the lines in real time

    Returns:
        str: stripped output

    Raises:
        CalledProcessError: if return code is non-zero
        TimeoutExpired: if timeout is reached

    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd, printer=printer)
    if timeout < 0:
        raise ValueError('Negative timeouts are not allowed')

    start = time()
    lines = []
    with subprocess.Popen(  # noqa: S602
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True,
    ) as proc:
        if not (stdout := proc.stdout):
            raise NotImplementedError('Failed to read stdout from process.')
        return_code = None
        while return_code is None:
            if timeout is not None and time() - start >= timeout:
                proc.kill()
                break
            if line := stdout.readline():
                lines.append(line)
                if printer:
                    printer(line.rstrip())
            else:
                return_code = proc.poll()

    output = ''.join(lines)
    if return_code is None:
        # Process was killed due to timeout
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output=output)
    if return_code != 0:
        raise subprocess.CalledProcessError(returncode=return_code, cmd=cmd, output=output)

    duration = time() - start
    LOGGER.debug('Shell command completed', cmd=cmd, returncode=0, duration_seconds=round(duration, 2), cwd=cwd)

    return output


async def _capture_shell_async(cmd: str, *, cwd: Path | None = None, start_time: float = 0) -> str:
    proc = await asyncio.create_subprocess_shell(  # noqa: S604
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    stdout, _stderr = await proc.communicate()
    output = stdout.decode().strip()
    if proc.returncode is None:
        # Process returncode should not be None after communicate(), but handle defensively
        raise RuntimeError(f'Process returncode is None after communicate() for command: {cmd}')
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(returncode=proc.returncode, cmd=cmd, output=output)

    duration = time() - start_time if start_time else 0
    LOGGER.debug('Shell command completed', cmd=cmd, returncode=0, duration_seconds=round(duration, 2), cwd=cwd)

    return output


async def capture_shell_async(cmd: str, *, timeout: int | None = 120, cwd: Path | None = None) -> str:
    """Run a shell command asynchronously and return the output.

    WARNING: This function uses shell=True which can be a security risk.
    Only use with trusted input.

    ```py
    print(asyncio.run(capture_shell_async('ls ~/.config')))
    ```

    Args:
        cmd: shell command
        timeout: process timeout in seconds. Defaults to 2 minutes. Use None for no timeout.
        cwd: optional path for shell execution

    Returns:
        str: stripped output
    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd)
    start = time()
    return await asyncio.wait_for(
        _capture_shell_async(cmd=cmd, cwd=cwd, start_time=start),
        timeout=timeout or None,
    )


def run_shell(cmd: str, *, timeout: int | None = 120, cwd: Path | None = None) -> None:
    """Run a shell command without capturing the output.

    WARNING: This function uses shell=True which can be a security risk.
    Only use with trusted input.

    Args:
        cmd: shell command
        timeout: process timeout in seconds. Defaults to 2 minutes. Use None for no timeout.
        cwd: optional path for shell execution

    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd)

    start = time()
    subprocess.run(  # noqa: S602
        cmd,
        timeout=timeout or None,
        cwd=cwd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
        shell=True,
    )

    duration = time() - start
    LOGGER.debug('Shell command completed', cmd=cmd, returncode=0, duration_seconds=round(duration, 2), cwd=cwd)
