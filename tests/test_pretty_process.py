"""Test pretty_process."""

from multiprocessing.managers import DictProxy

import pytest

from corallium.pretty_process import _chunked, pretty_process


@pytest.mark.parametrize(
    ('data', 'count', 'expected'),
    [
        ([], 3, []),
        ([1, 2, 3], 0, [[1, 2, 3]]),
        ([1, 2, 3], -1, [[1, 2, 3]]),
        ([1, 2, 3, 4, 5, 6], 3, [[1, 2], [3, 4], [5, 6]]),
        ([1, 2, 3, 4, 5], 3, [[1, 2], [3, 4], [5]]),
        ([1, 2], 5, [[1], [2]]),
    ],
)
def test_chunked(data, count, expected):
    assert _chunked(data, count) == expected


def _increment_task(task_id: int, shared_progress: DictProxy, data: list[int]) -> int:  # type: ignore[type-arg]
    total = 0
    for val in data:
        total += val
        shared_progress[task_id] += 1
    return total


def test_pretty_process_returns_each_chunks_result_in_order():
    result = pretty_process(_increment_task, data=[1, 2, 3, 4, 5, 6], num_workers=2, num_cpus=3)

    assert result == [3, 7, 11]
