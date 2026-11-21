import re

import pytest

from corallium.code_tag_collector import CODE_TAG_RE, COMMON_CODE_TAGS, SKIP_PHRASE, write_code_tag_file
from corallium.code_tag_collector._collector import (
    _LEGACY_SKIP_PHRASES,
    _CodeTag,
    _format_report,
    _search_lines,
    _Tags,
)
from tests.configuration import TEST_DATA_DIR

TEST_PROJECT = TEST_DATA_DIR / 'test_project'


def test_search_lines(snapshot):
    lines = [
        '# DEBUG: Show dodo.py in the documentation',
        'print("FIXME: Show README.md in the documentation (may need to update paths?)")',
        '# FYI: Replace src_examples_dir and make more generic to specify code to include in documentation',
        '# HACK: Show table of contents in __init__.py file',
        '# NOTE: Show table of contents in __init__.py file',
        '# PLANNED: Show table of contents in __init__.py file',
        '# REVIEW: Show table of contents in __init__.py file',
        '# TBD: Show table of contents in __init__.py file',
        '# TODO: Show table of contents in __init__.py file',
        '# HACK - Support unconventional dashed code tags',
        'class Code: # TODO: Complete',
        '   //TODO: Not matched',
        '   ...  # Both FIXME: and FYI: in the same line, but only match the first',
        '# FIXME: ' + 'For a long line is ignored ...' * 14,
    ]
    tag_order = ['FIXME', 'FYI', 'HACK', 'REVIEW']
    matcher = CODE_TAG_RE.format(tag='|'.join(tag_order))

    comments = _search_lines(lines, re.compile(matcher))

    assert comments == snapshot


def test_format_report(fake_process, snapshot):
    fake_process.pass_command([fake_process.any()])
    fake_process.keep_last_process(keep=True)
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']
    comments = [
        _CodeTag(lineno=lineno, **dict(zip(('tag', 'text'), line.split('# ')[1].split(': '), strict=False)))
        for lineno, line in enumerate(lines)
    ]
    tagged_collection = [_Tags(path_source=TEST_DATA_DIR / 'test_project', code_tags=comments)]
    tag_order = ['TODO']

    output = _format_report(TEST_DATA_DIR.parent, tagged_collection, tag_order=tag_order)

    assert output == snapshot


@pytest.fixture
def todo_regex():
    """Compiled TODO regex pattern."""
    return re.compile(CODE_TAG_RE.format(tag='TODO'))


@pytest.fixture
def all_tags_regex():
    """Compiled regex for all common code tags."""
    return re.compile(CODE_TAG_RE.format(tag='|'.join(COMMON_CODE_TAGS)))


@pytest.mark.parametrize(
    ('lines', 'expected_count', 'expected_tags', 'skip_phrase_override'),
    [
        (
            ['# Some code', '# TODO: Fix this later', 'def foo(): pass'],
            1,
            ['TODO'],
            None,
        ),
        (
            ['# TODO: First task', '# FIXME: Broken code', '# HACK: Temporary workaround'],
            3,
            ['TODO', 'FIXME', 'HACK'],
            None,
        ),
        (
            ['# TODO: This should be ignored', '', f'<!-- {SKIP_PHRASE} -->'],
            0,
            [],
            None,
        ),
        (
            ['# TODO: ' + 'x' * 500],
            0,
            [],
            None,
        ),
        (
            ['# TODO: Should be found', '', '# custom_skip'],
            0,
            [],
            'custom_skip',
        ),
        *[
            (['# TODO: This should be skipped', '', f'<!-- {legacy} -->'], 0, [], None)
            for legacy in _LEGACY_SKIP_PHRASES
        ],
        (
            ['# TODO: kept, because the skip phrase is not in the final two lines', f'<!-- {SKIP_PHRASE} -->', '', ''],
            1,
            ['TODO'],
            None,
        ),
        (
            ['# TODO: ' + 'x' * (400 - len('# TODO: '))],
            1,
            ['TODO'],
            None,
        ),
    ],
)
def test_search_lines_variations(
    lines: list[str],
    expected_count: int,
    expected_tags: list[str],
    skip_phrase_override: str | None,
    *,
    todo_regex,
    all_tags_regex,
):
    """Test _search_lines with various scenarios."""
    regex = all_tags_regex if len(expected_tags) > 1 else todo_regex
    kwargs = {'skip_phrase': skip_phrase_override} if skip_phrase_override else {}

    result = _search_lines(lines, regex, **kwargs)

    assert len(result) == expected_count
    for idx, expected_tag in enumerate(expected_tags):
        assert result[idx].tag == expected_tag


def test_write_code_tag_file_when_no_matches(fix_test_cache):
    path_tag_summary = fix_test_cache / 'code_tags.md'
    path_tag_summary.write_text('Should be removed.')
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('No FIXMES or TODOS here')

    write_code_tag_file(
        path_tag_summary=path_tag_summary,
        paths_source=[tmp_code_file],
        base_dir=fix_test_cache,
    )

    assert not path_tag_summary.is_file()


def test_write_code_tag_file_round_trip(tmp_path):
    source = tmp_path / 'src.py'
    source.write_text('# TODO: first\n# FIXME: second\n# HACK: not asked for\n')
    summary = tmp_path / 'nested' / 'docs' / 'CODE_TAGS.md'

    write_code_tag_file(path_tag_summary=summary, paths_source=[source], base_dir=tmp_path, tags='FIXME, TODO')

    text = summary.read_text()
    assert text == (
        '# Task Summary\n\nAuto-Generated by `corallium`\n\n'
        '| Type  | Comment | Last Edit | Source File |\n'
        '|-------|---------|-----------|-------------|\n'
        '| TODO  | first   | N/A       | src.py:1    |\n'
        '| FIXME | second  | N/A       | src.py:2    |\n\n'
        'Found code tags for FIXME (1), TODO (1)\n\n'
        f'<!-- {SKIP_PHRASE} -->\n'
    )
    assert SKIP_PHRASE == 'corallium_skip_tags'
    # The summary carries the skip phrase, so a later scan that includes it finds nothing in it
    regex = re.compile(CODE_TAG_RE.format(tag='TODO|FIXME'))
    assert _search_lines(text.splitlines(), regex) == []


# corallium_skip_tags
