"""Test markup_table."""

import math

import pytest
from beartype.typing import Any, Dict, List

from corallium.markup_table import format_table


@pytest.fixture
def basic_table_data() -> tuple[List[str], List[Dict[str, Any]]]:
    """Common test data for table formatting."""
    return ['Name', 'Age'], [{'Name': 'Alice', 'Age': 30}, {'Name': 'Bob', 'Age': 25}]


@pytest.mark.parametrize(
    ('headers', 'records', 'delimiters'),
    [
        (['Name', 'Age'], [{'Name': 'Alice', 'Age': 30}, {'Name': 'Bob', 'Age': 25}], None),
        (['X'], [{'X': 'short'}, {'X': 'much longer value'}], None),
        (['A', 'B'], [], None),
        (['Int', 'Float'], [{'Int': 42, 'Float': math.pi}], None),
        (['Col'], [{'Col': 'val'}], [':-']),
        (['Col'], [{'Col': 'val'}], ['-:']),
        (['Col'], [{'Col': 'val'}], [':-:']),
        (['Col'], [{'Col': 'val'}], ['-']),
    ],
)
def test_format_table(
    snapshot,
    headers: List[str],
    records: List[Dict[str, Any]],
    delimiters: List[str] | None,
) -> None:
    """Test table formatting with various inputs using snapshots."""
    result = format_table(headers, records, delimiters=delimiters)
    assert result == snapshot


@pytest.mark.parametrize(
    ('headers', 'records', 'delimiters', 'error_match'),
    [
        (['A', 'B', 'C'], [{'A': 1, 'B': 2, 'C': 3}], ['-', '-'], 'Incorrect number of delimiters'),
        (['A'], [{'A': 1}], ['invalid'], 'Delimiters must be one of'),
    ],
)
def test_format_table_errors(
    headers: List[str],
    records: List[Dict[str, Any]],
    delimiters: List[str],
    error_match: str,
) -> None:
    """Test table formatting error cases."""
    with pytest.raises(ValueError, match=error_match):
        format_table(headers, records, delimiters=delimiters)
