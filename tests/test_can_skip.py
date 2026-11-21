"""Test can_skip."""

import os
from pathlib import Path

import pytest

from corallium.can_skip import can_skip, dont_skip


def _touch(path: Path, mtime: int) -> Path:
    path.write_text(path.name, encoding='utf-8')
    os.utime(path, (mtime, mtime))
    return path


@pytest.mark.parametrize(
    ('prereq_mtimes', 'target_mtimes', 'expected'),
    [
        pytest.param([100], [200], True, id='target newer'),
        pytest.param([200], [100], False, id='prerequisite newer'),
        pytest.param([100], [None], False, id='target missing'),
        pytest.param([100, 150, 120], [200, 300], True, id='every target newer than every prerequisite'),
        pytest.param([100, 250], [200, 300], False, id='one prerequisite newer than the oldest target'),
    ],
)
def test_can_skip(tmp_path: Path, prereq_mtimes: list[int], target_mtimes: list[int | None], *, expected: bool):
    prereqs = [_touch(tmp_path / f'src{i}.py', m) for i, m in enumerate(prereq_mtimes)]
    targets = [
        _touch(tmp_path / f'out{i}.txt', m) if m is not None else tmp_path / f'missing{i}.txt'
        for i, m in enumerate(target_mtimes)
    ]

    assert can_skip(prerequisites=prereqs, targets=targets) is expected
    assert dont_skip(prerequisites=prereqs, targets=targets) is False


@pytest.mark.parametrize(
    ('prereq_names', 'error'),
    [
        (['missing.py'], FileNotFoundError),
        ([], ValueError),
    ],
)
def test_can_skip_refuses_missing_prerequisites(tmp_path: Path, prereq_names: list[str], error: type[Exception]):
    target = _touch(tmp_path / 'output.txt', 100)

    with pytest.raises(error):
        can_skip(prerequisites=[tmp_path / n for n in prereq_names], targets=[target])
