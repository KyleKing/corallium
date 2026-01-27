"""Test can_skip."""

import time
from pathlib import Path

import pytest

from corallium.can_skip import can_skip, dont_skip


def test_can_skip_when_targets_newer(fix_test_cache: Path) -> None:
    prereq = fix_test_cache / 'source.py'
    target = fix_test_cache / 'output.txt'

    prereq.write_text('source')
    time.sleep(0.01)  # ensure different mtime
    target.write_text('output')

    assert can_skip(prerequisites=[prereq], targets=[target]) is True


def test_can_skip_when_prerequisites_newer(fix_test_cache: Path) -> None:
    prereq = fix_test_cache / 'source.py'
    target = fix_test_cache / 'output.txt'

    target.write_text('output')
    time.sleep(0.01)
    prereq.write_text('source')

    assert can_skip(prerequisites=[prereq], targets=[target]) is False


def test_can_skip_when_target_missing(fix_test_cache: Path) -> None:
    prereq = fix_test_cache / 'source.py'
    prereq.write_text('source')
    missing_target = fix_test_cache / 'missing.txt'

    assert can_skip(prerequisites=[prereq], targets=[missing_target]) is False


def test_can_skip_raises_when_prerequisite_missing(fix_test_cache: Path) -> None:
    missing = fix_test_cache / 'missing.py'
    target = fix_test_cache / 'output.txt'
    target.write_text('output')

    with pytest.raises(FileNotFoundError):
        can_skip(prerequisites=[missing], targets=[target])


def test_can_skip_with_empty_prerequisites_raises(fix_test_cache: Path) -> None:
    target = fix_test_cache / 'output.txt'
    target.write_text('output')

    with pytest.raises(ValueError, match='Required files do not exist'):
        can_skip(prerequisites=[], targets=[target])


def test_can_skip_with_multiple_prerequisites_and_targets(fix_test_cache: Path) -> None:
    prereqs = [fix_test_cache / f'src{i}.py' for i in range(3)]
    targets = [fix_test_cache / f'out{i}.txt' for i in range(2)]

    for p in prereqs:
        p.write_text('source')
    time.sleep(0.01)
    for t in targets:
        t.write_text('output')

    assert can_skip(prerequisites=prereqs, targets=targets) is True


def test_dont_skip_always_returns_false(fix_test_cache: Path) -> None:
    prereq = fix_test_cache / 'source.py'
    target = fix_test_cache / 'output.txt'
    prereq.write_text('source')
    time.sleep(0.01)
    target.write_text('output')

    assert dont_skip(prerequisites=[prereq], targets=[target]) is False
