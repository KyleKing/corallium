"""Repo root discovery, VCS detection, and metadata resolution."""

from __future__ import annotations

from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError

from corallium.shell import capture_shell

from ._forge import detect_forge, parse_remote_url
from ._git_commands import git_show_toplevel
from ._types import RepoMetadata, VcsKind

_VCS_MARKERS = {
    '.git': VcsKind.GIT,
    '.jj': VcsKind.JUJUTSU,
}


def find_repo_root(start_path: Path | None = None) -> Path | None:
    """Find the repository root by searching for .git or .jj directory.

    Args:
        start_path: Path to start searching from. Defaults to current working directory.

    Returns:
        Path to the repository root, or None if not found

    """
    current = (start_path or Path.cwd()).resolve()
    while current != current.parent:
        if any((current / marker).is_dir() for marker in _VCS_MARKERS):
            return current
        current = current.parent
    return None


def detect_vcs_kind(repo_root: Path) -> VcsKind | None:
    """Detect which VCS is in use at the given repo root."""
    for marker, kind in _VCS_MARKERS.items():
        if (repo_root / marker).is_dir():
            return kind
    return None


def _get_remote_url(*, cwd: Path) -> str:
    with suppress(CalledProcessError):
        return capture_shell('git remote get-url origin', cwd=cwd).strip()
    return ''


def _get_branch(*, cwd: Path) -> str:
    with suppress(CalledProcessError):
        return capture_shell('git branch --show-current', cwd=cwd).strip()
    return ''


@lru_cache(maxsize=128)
def get_repo_metadata(cwd: Path) -> RepoMetadata | None:
    """Resolve full repository metadata from a working directory.

    Cached to avoid repeated subprocess calls for the same directory.

    Args:
        cwd: Path to the current working directory

    Returns:
        RepoMetadata, or None if no VCS repository is found

    """
    if git_root := git_show_toplevel(cwd=cwd):
        root = git_root
        vcs = VcsKind.GIT
    elif repo_root := find_repo_root(cwd):
        root = repo_root
        vcs = detect_vcs_kind(root) or VcsKind.GIT
    else:
        return None

    remote_url = _get_remote_url(cwd=root)
    owner, repo_name = parse_remote_url(remote_url)
    branch = _get_branch(cwd=root)
    forge = detect_forge(remote_url)

    return RepoMetadata(
        root=root,
        vcs=vcs,
        remote_url=remote_url,
        owner=owner,
        repo_name=repo_name,
        branch=branch,
        forge=forge,
    )
