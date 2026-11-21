"""Test file_helpers (referenced in below test)."""

import os
import time
from pathlib import Path

import pytest

from corallium.file_helpers import (
    _parse_mise_lock,
    _parse_mise_toml,
    _parse_tool_versions,
    delete_dir,
    delete_old_files,
    ensure_dir,
    get_tool_versions,
    if_found_unlink,
    read_lines,
    read_package_name,
    sanitize_filename,
    tail_lines,
    trim_trailing_whitespace,
)


def test_sanitize_filename():
    result = sanitize_filename('_dash-09-ϑ//.// SUPER.py')

    assert result == '_dash-09-___.___SUPER.py'


def test_read_lines():
    at_least_this_many_lines = 22
    result = read_lines(Path(__file__).resolve())

    assert result[0] == '"""Test file_helpers (referenced in below test)."""'
    assert len(result) > at_least_this_many_lines
    assert len(read_lines(Path.cwd() / 'not a file.tbd')) == 0


@pytest.mark.parametrize(
    ('content', 'count', 'expected'),
    [
        ('line 1\nline 2\n', 1, ['']),
        ('line 1\nline 2\n', 2, ['line 2', '']),
        ('line 1\nline 2\n', 10, ['line 1', 'line 2', '']),
        ('', 3, []),
        # Longer than one 8 KB read, so the lines are stitched across chunks
        (''.join(f'row {i:05d}\n' for i in range(2000)), 3, ['row 01998', 'row 01999', '']),
        (''.join(f'row {i:05d}\n' for i in range(2000)), 2001, [*(f'row {i:05d}' for i in range(2000)), '']),
    ],
)
def test_tail_lines(tmp_path, content: str, count: int, expected: list[str]):
    path_file = tmp_path / 'tmp.txt'
    path_file.write_text(content)

    assert tail_lines(path_file, count=count) == expected


def test_if_found_unlink(fix_test_cache):
    path_file = fix_test_cache / 'if_found_unlink-test_file.txt'

    path_file.write_text('')

    assert path_file.is_file()
    if_found_unlink(path_file)
    assert not path_file.is_file()


def test_dir_tools(fix_test_cache):
    tmp_dir = fix_test_cache / '.tmp-test_delete_dir'
    tmp_dir.mkdir(exist_ok=True)
    (tmp_dir / 'tmp.txt').write_text('Placeholder\n')
    tmp_subdir = tmp_dir / 'subdir' / 'nested'

    ensure_dir(tmp_subdir)

    assert tmp_subdir.is_dir()
    delete_dir(tmp_dir)
    assert not tmp_dir.is_dir()


def test_parse_mise_lock(fix_test_cache):
    lock_path = fix_test_cache / 'mise.lock'
    lock_path.write_text("""\
[tools.python]
version = "3.11.11"

[tools.node]
version = "20.10.0"
""")

    result = _parse_mise_lock(lock_path)

    assert result == {'python': ['3.11.11'], 'node': ['20.10.0']}


def test_parse_mise_toml_single_version(fix_test_cache):
    mise_path = fix_test_cache / 'mise.toml'
    mise_path.write_text("""\
[tools]
python = "3.11"
node = "20"
""")

    result = _parse_mise_toml(mise_path)

    assert result == {'python': ['3.11'], 'node': ['20']}


def test_parse_mise_toml_multiple_versions(fix_test_cache):
    mise_path = fix_test_cache / 'mise.toml'
    mise_path.write_text("""\
[tools]
python = ["3.10.16", "3.11.11", "3.12.5"]
""")

    result = _parse_mise_toml(mise_path)

    assert result == {'python': ['3.10.16', '3.11.11', '3.12.5']}


def test_parse_tool_versions(fix_test_cache):
    tv_path = fix_test_cache / '.tool-versions'
    tv_path.write_text('python 3.10.16 3.11.11\nnode 20.10.0\n')

    result = _parse_tool_versions(tv_path)

    assert result == {'python': ['3.10.16', '3.11.11'], 'node': ['20.10.0']}


@pytest.mark.parametrize(
    ('files', 'expected'),
    [
        pytest.param(
            {
                'mise.lock': '[tools.python]\nversion = "3.11.11"\n',
                'mise.toml': '[tools]\npython = "3.10"\n',
                '.tool-versions': 'python 3.9.0\n',
            },
            {'python': ['3.11.11']},
            id='mise.lock first',
        ),
        pytest.param(
            {'mise.toml': '[tools]\npython = "3.10"\n', '.tool-versions': 'python 3.9.0\n'},
            {'python': ['3.10']},
            id='then mise.toml',
        ),
        pytest.param({'.tool-versions': 'python 3.9.0\n'}, {'python': ['3.9.0']}, id='then .tool-versions'),
    ],
)
def test_get_tool_versions_by_precedence(tmp_path, files: dict[str, str], expected: dict[str, list[str]]):
    for name, text in files.items():
        (tmp_path / name).write_text(text)

    assert get_tool_versions(cwd=tmp_path) == expected


def test_get_tool_versions_raises_when_no_file(tmp_path):
    isolated_dir = tmp_path / 'isolated'
    isolated_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        get_tool_versions(cwd=isolated_dir)


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('a  \nb\t \n  c\n', 'a\nb\t\n  c\n'),
        pytest.param(
            'a  \r\nb \r\n',
            'a\r\nb\r\n',
            marks=pytest.mark.xfail(
                strict=True,
                reason='read_text translates CRLF to LF, so the documented CRLF preservation never happens',
            ),
        ),
    ],
)
def test_trim_trailing_whitespace_keeps_line_endings_and_tabs(tmp_path, text: str, expected: str):
    pth = tmp_path / 'f.txt'
    pth.write_bytes(text.encode())

    trim_trailing_whitespace(pth)

    assert pth.read_bytes() == expected.encode()


def test_delete_old_files_removes_only_stale_files_and_never_follows_links(tmp_path):
    outside = tmp_path / 'outside.txt'
    outside.write_text('keep')
    cache = tmp_path / 'cache'
    (cache / 'sub').mkdir(parents=True)
    for name in ('old.txt', 'sub/old.txt', 'fresh.txt'):
        (cache / name).write_text(name)
    stale = time.time() - 3600
    for pth in (cache / 'old.txt', cache / 'sub' / 'old.txt', outside):
        os.utime(pth, (stale, stale))
    (cache / 'link.txt').symlink_to(outside)

    delete_old_files(cache, ttl_seconds=60)

    assert sorted(p.relative_to(cache).as_posix() for p in cache.rglob('*')) == ['fresh.txt', 'link.txt', 'sub']
    assert outside.is_file()


@pytest.mark.parametrize(
    ('pyproject', 'expected'),
    [
        ('[project]\nname = "uv-pkg"\n', 'uv-pkg'),
        ('[tool.poetry]\nname = "poetry-pkg"\n', 'poetry-pkg'),
        ('[project]\nname = "both"\n[tool.poetry]\nname = "ignored"\n', 'both'),
    ],
)
def test_read_package_name(tmp_path, pyproject: str, expected: str):
    (tmp_path / 'pyproject.toml').write_text(pyproject)

    assert read_package_name(cwd=tmp_path) == expected
