"""Test pretty_process."""

from multiprocessing.managers import DictProxy

from corallium.pretty_process import _chunked, pretty_process


def test_chunked_empty_list():
    result = _chunked(list[int](), 3)

    assert result == []


def test_chunked_zero_count():
    result = _chunked([1, 2, 3], 0)

    assert result == [[1, 2, 3]]


def test_chunked_negative_count():
    result = _chunked([1, 2, 3], -1)

    assert result == [[1, 2, 3]]


def test_chunked_normal_split():
    result = _chunked([1, 2, 3, 4, 5, 6], 3)

    assert result == [[1, 2], [3, 4], [5, 6]]


def test_chunked_uneven_split():
    result = _chunked([1, 2, 3, 4, 5], 3)

    assert result == [[1, 2], [3, 4], [5]]


def test_chunked_more_chunks_than_items():
    result = _chunked([1, 2], 5)

    assert result == [[1], [2]]


def _increment_task(task_id: int, shared_progress: DictProxy, data: list[int]) -> int:  # type: ignore[type-arg]
    total = 0
    for val in data:
        total += val
        shared_progress[task_id] += 1
    return total


def test_pretty_process_runs_without_error():
    data = [1, 2, 3]
    result = pretty_process(_increment_task, data=data, num_workers=2, num_cpus=2)

    assert sum(result) == sum(data)
