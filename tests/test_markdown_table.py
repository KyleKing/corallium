"""Test markdown_table."""

import math

import pytest
from beartype.typing import List

from corallium.markdown_table import format_table


def test_format_table_basic() -> None:
    headers = ['Name', 'Age']
    records = [{'Name': 'Alice', 'Age': 30}, {'Name': 'Bob', 'Age': 25}]

    result = format_table(headers, records)

    assert '| Name  | Age |' in result
    assert '| Alice | 30  |' in result
    assert '| Bob   | 25  |' in result


def test_format_table_column_width_adjusts_to_content() -> None:
    headers = ['X']
    records = [{'X': 'short'}, {'X': 'much longer value'}]

    result = format_table(headers, records)

    assert '| much longer value |' in result


def test_format_table_empty_records() -> None:
    headers = ['A', 'B']
    records = []

    result = format_table(headers, records)

    assert '| A | B |' in result
    assert result.count('\n') == 1


@pytest.mark.parametrize(
    ('delimiters', 'expected_separator'),
    [
        ([':-'], ':---'),
        (['-:'], '---:'),
        ([':-:'], ':---:'),
        (['-'], '-----'),
    ],
)
def test_format_table_delimiter_alignment(delimiters: List[str], expected_separator: str) -> None:
    headers = ['Col']
    records = [{'Col': 'val'}]

    result = format_table(headers, records, delimiters=delimiters)

    assert expected_separator in result


def test_format_table_delimiter_count_mismatch_raises() -> None:
    headers = ['A', 'B', 'C']
    records = [{'A': 1, 'B': 2, 'C': 3}]

    with pytest.raises(ValueError, match='Incorrect number of delimiters'):
        format_table(headers, records, delimiters=['-', '-'])


def test_format_table_invalid_delimiter_raises() -> None:
    headers = ['A']
    records = [{'A': 1}]

    with pytest.raises(ValueError, match='Delimiters must one of'):
        format_table(headers, records, delimiters=['invalid'])


def test_format_table_numeric_values_converted_to_string() -> None:
    headers = ['Int', 'Float']
    records = [{'Int': 42, 'Float': math.pi}]

    result = format_table(headers, records)

    assert '42' in result
    assert '3.14' in result
