"""Run shell commands."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from time import time

from .log import LOGGER


def capture_shell(
    cmd: str,
    *,
    timeout: int = 120,
    cwd: Path | None = None,
    printer: Callable[[str], None] | None = None,
) -> str:
    """Run shell command, return the output, and optionally print in real time.

    Inspired by: https://stackoverflow.com/a/38745040/3219667

    Args:
        cmd: shell command
        timeout: process timeout. Defaults to 2 minutes
        cwd: optional path for shell execution
        printer: optional callable to output the lines in real time

    Returns:
        str: stripped output

    Raises:
        CalledProcessError: if return code is non-zero

    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd, printer=printer)

    start = time()
    lines = []
    with subprocess.Popen(
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
            if timeout != 0 and time() - start >= timeout:
                proc.kill()
                break
            if line := stdout.readline():
                lines.append(line)
                if printer:
                    printer(line.rstrip())
            else:
                return_code = proc.poll()

    output = ''.join(lines)
    if return_code != 0:
        raise subprocess.CalledProcessError(returncode=return_code or 404, cmd=cmd, output=output)
    return output


async def _capture_shell_async(cmd: str, *, cwd: Path | None = None) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    stdout, _stderr = await proc.communicate()
    output = stdout.decode().strip()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(returncode=proc.returncode or 404, cmd=cmd, output=output)
    return output


async def capture_shell_async(cmd: str, *, timeout: int = 120, cwd: Path | None = None) -> str:
    """Run a shell command asynchronously and return the output.

    ```py
    print(asyncio.run(capture_shell_async('ls ~/.config')))
    ```

    Args:
        cmd: shell command
        timeout: process timeout. Defaults to 2 minutes
        cwd: optional path for shell execution

    Returns:
        str: stripped output

    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd)
    return await asyncio.wait_for(_capture_shell_async(cmd=cmd, cwd=cwd), timeout=timeout)


def run_shell(cmd: str, *, timeout: int = 120, cwd: Path | None = None) -> None:
    """Run a shell command without capturing the output.

    Args:
        cmd: shell command
        timeout: process timeout. Defaults to 2 minutes
        cwd: optional path for shell execution

    """
    LOGGER.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd)

    subprocess.run(
        cmd,
        timeout=timeout or None,
        cwd=cwd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
        shell=True,
    )
