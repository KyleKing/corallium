"""Tests for corallium.vcs._forge."""

import pytest

from corallium.vcs._forge import (
    detect_forge,
    forge_blame_url,
    forge_file_url,
    forge_repo_url,
    parse_remote_url,
)
from corallium.vcs._types import ForgeKind


@pytest.mark.parametrize(
    ('remote_url', 'expected'),
    [
        ('https://github.com/KyleKing/calcipy.git', ('KyleKing', 'calcipy')),
        ('git@github.com:KyleKing/calcipy.git', ('KyleKing', 'calcipy')),
        ('https://gitlab.com/org/project.git', ('org', 'project')),
        ('git@gitlab.com:org/project.git', ('org', 'project')),
        ('https://bitbucket.org/team/repo.git', ('team', 'repo')),
        ('git@bitbucket.org:team/repo.git', ('team', 'repo')),
        ('https://github.com/owner/repo', ('owner', 'repo')),
        ('', ('', '')),
        ('not-a-url', ('', '')),
    ],
)
def test_parse_remote_url(remote_url: str, expected: tuple[str, str]):
    assert parse_remote_url(remote_url) == expected


@pytest.mark.parametrize(
    ('remote_url', 'expected'),
    [
        ('git@github.com:KyleKing/calcipy.git', ForgeKind.GITHUB),
        ('https://github.com/KyleKing/calcipy.git', ForgeKind.GITHUB),
        ('git@gitlab.com:org/project.git', ForgeKind.GITLAB),
        ('https://bitbucket.org/team/repo.git', ForgeKind.BITBUCKET),
        ('https://selfhosted.example.com/foo/bar.git', ForgeKind.UNKNOWN),
        ('', ForgeKind.UNKNOWN),
    ],
)
def test_detect_forge(remote_url: str, expected: ForgeKind):
    assert detect_forge(remote_url) == expected


@pytest.mark.parametrize(
    ('forge', 'expected'),
    [
        (ForgeKind.GITHUB, 'https://github.com/owner/repo'),
        (ForgeKind.GITLAB, 'https://gitlab.com/owner/repo'),
        (ForgeKind.BITBUCKET, 'https://bitbucket.org/owner/repo'),
        (ForgeKind.UNKNOWN, ''),
    ],
)
def test_forge_repo_url(forge: ForgeKind, expected: str):
    assert forge_repo_url(forge=forge, owner='owner', repo='repo') == expected


@pytest.mark.parametrize(
    ('forge', 'expected'),
    [
        (ForgeKind.GITHUB, 'https://github.com/o/r/blame/abc123/src/main.py#L42'),
        (ForgeKind.GITLAB, 'https://gitlab.com/o/r/-/blame/abc123/src/main.py#L42'),
        (ForgeKind.BITBUCKET, 'https://bitbucket.org/o/r/annotate/abc123/src/main.py#src/main.py-42'),
        (ForgeKind.UNKNOWN, ''),
    ],
)
def test_forge_blame_url(forge: ForgeKind, expected: str):
    assert forge_blame_url(forge=forge, owner='o', repo='r', rev='abc123', path='src/main.py', line=42) == expected


@pytest.mark.parametrize(
    ('forge', 'expected'),
    [
        (ForgeKind.GITHUB, 'https://github.com/o/r/blob/abc123/src/main.py#L42'),
        (ForgeKind.GITLAB, 'https://gitlab.com/o/r/-/blob/abc123/src/main.py#L42'),
        (ForgeKind.BITBUCKET, 'https://bitbucket.org/o/r/src/abc123/src/main.py#src/main.py-42'),
        (ForgeKind.UNKNOWN, ''),
    ],
)
def test_forge_file_url(forge: ForgeKind, expected: str):
    assert forge_file_url(forge=forge, owner='o', repo='r', rev='abc123', path='src/main.py', line=42) == expected
