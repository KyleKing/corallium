"""Test file_helpers (referenced in below test)."""

from pathlib import Path

import pytest

from corallium.file_helpers import (
    _parse_mise_lock,
    _parse_mise_toml,
    _parse_tool_versions,
    delete_dir,
    ensure_dir,
    get_tool_versions,
    if_found_unlink,
    read_lines,
    sanitize_filename,
    tail_lines,
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


def test_tail_lines(fix_test_cache):
    path_file = fix_test_cache / 'tmp.txt'
    path_file.write_text('line 1\nline 2\n')

    result = tail_lines(path_file, count=1)

    assert result == ['']
    assert tail_lines(path_file, count=2) == ['line 2', '']
    assert tail_lines(path_file, count=10) == ['line 1', 'line 2', '']


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
    tmp_subdir = tmp_dir / 'subdir'

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


def test_get_tool_versions_prefers_mise_lock(fix_test_cache):
    (fix_test_cache / 'mise.lock').write_text('[tools.python]\nversion = "3.11.11"\n')
    (fix_test_cache / 'mise.toml').write_text('[tools]\npython = "3.10"\n')
    (fix_test_cache / '.tool-versions').write_text('python 3.9.0\n')

    result = get_tool_versions(cwd=fix_test_cache)

    assert result == {'python': ['3.11.11']}


def test_get_tool_versions_falls_back_to_mise_toml(fix_test_cache):
    (fix_test_cache / 'mise.toml').write_text('[tools]\npython = "3.10"\n')
    (fix_test_cache / '.tool-versions').write_text('python 3.9.0\n')

    result = get_tool_versions(cwd=fix_test_cache)

    assert result == {'python': ['3.10']}


def test_get_tool_versions_raises_when_no_file(tmp_path):
    isolated_dir = tmp_path / 'isolated'
    isolated_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        get_tool_versions(cwd=isolated_dir)
