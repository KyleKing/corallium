"""Test sync_dependencies."""

from pathlib import Path
from textwrap import dedent

import pytest
from beartype.typing import Optional, Tuple

from corallium.sync_dependencies import (
    _collect_poetry_dependencies,
    _collect_pyproject_versions,
    _collect_uv_dependencies,
    _extract_base_version,
    _parse_lock_file,
    _parse_pep621_dependency,
    replace_versions,
)


@pytest.mark.parametrize(
    ('version_spec', 'expected'),
    [
        ('>=1.0.0', '1.0.0'),
        ('^2.3.4', '2.3.4'),
        ('~=1.2', '1.2'),
        ('==3.0.0', '3.0.0'),
        ('1.0.0', '1.0.0'),
        ('>=1.0,<2.0', '1.0'),
    ],
)
def test_extract_base_version(version_spec: str, expected: str) -> None:
    assert _extract_base_version(version_spec) == expected


@pytest.mark.parametrize(
    ('dep_spec', 'expected'),
    [
        ('requests>=2.28.0', ('requests', '2.28.0')),
        ('numpy[extra]>=1.24.0', ('numpy', '1.24.0')),
        ('pkg[a,b]>=1.0', ('pkg', '1.0')),
        ('zope.interface>=5.0.0', ('zope.interface', '5.0.0')),
        ('package', None),
        ('', None),
    ],
)
def test_parse_pep621_dependency(dep_spec: str, expected: Optional[Tuple[str, str]]) -> None:
    assert _parse_pep621_dependency(dep_spec) == expected


def test_collect_uv_dependencies_from_project_dependencies() -> None:
    pyproject = {
        'project': {
            'dependencies': ['requests>=2.28.0', 'click>=8.0.0'],
        },
    }

    result = _collect_uv_dependencies(pyproject)

    assert result == {'requests': '2.28.0', 'click': '8.0.0'}


def test_collect_uv_dependencies_from_optional_dependencies() -> None:
    pyproject = {
        'project': {
            'optional-dependencies': {
                'dev': ['pytest>=7.0.0'],
            },
        },
    }

    result = _collect_uv_dependencies(pyproject)

    assert result == {'pytest': '7.0.0'}


def test_collect_uv_dependencies_from_dependency_groups() -> None:
    pyproject = {
        'dependency-groups': {
            'test': ['coverage>=7.0.0'],
        },
    }

    result = _collect_uv_dependencies(pyproject)

    assert result == {'coverage': '7.0.0'}


def test_collect_poetry_dependencies_from_tool_poetry_dependencies() -> None:
    pyproject = {
        'tool': {
            'poetry': {
                'dependencies': {
                    'python': '^3.9',
                    'requests': '^2.28.0',
                },
            },
        },
    }

    result = _collect_poetry_dependencies(pyproject)

    assert result == {'requests': '2.28.0'}
    assert 'python' not in result


def test_collect_poetry_dependencies_from_poetry_groups() -> None:
    pyproject = {
        'tool': {
            'poetry': {
                'dependencies': {},
                'group': {
                    'dev': {
                        'dependencies': {'pytest': '^7.0.0'},
                    },
                },
            },
        },
    }

    result = _collect_poetry_dependencies(pyproject)

    assert result == {'pytest': '7.0.0'}


def test_collect_poetry_dependencies_handles_dict_version_spec() -> None:
    pyproject = {
        'tool': {
            'poetry': {
                'dependencies': {
                    'pkg': {'version': '^1.0.0', 'optional': True},
                },
            },
        },
    }

    result = _collect_poetry_dependencies(pyproject)

    assert result == {'pkg': '1.0.0'}


def test_collect_pyproject_versions_merges_uv_and_poetry_prefers_uv() -> None:
    pyproject_text = dedent("""\
        [project]
        dependencies = ["requests>=2.30.0"]

        [tool.poetry.dependencies]
        requests = "^2.28.0"
    """)

    result = _collect_pyproject_versions(pyproject_text)

    assert result['requests'] == '2.30.0'


def test_parse_lock_file_parses_poetry_lock(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'poetry.lock'
    lock_path.write_text(dedent("""\
        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "click"
        version = "8.1.7"
    """))

    result = _parse_lock_file(lock_path)

    assert result == {'requests': '2.31.0', 'click': '8.1.7'}


def test_parse_lock_file_parses_uv_lock(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'uv.lock'
    lock_path.write_text(dedent("""\
        [[package]]
        name = "requests"
        version = "2.31.0"
    """))

    result = _parse_lock_file(lock_path)

    assert result == {'requests': '2.31.0'}


def test_parse_lock_file_unsupported_lock_raises(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'unknown.lock'
    lock_path.write_text('')

    with pytest.raises(NotImplementedError, match='Unsupported lock file'):
        _parse_lock_file(lock_path)


def test_replace_versions_updates_poetry_versions(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'poetry.lock'
    pyproject_path = fix_test_cache / 'pyproject.toml'

    lock_path.write_text(dedent("""\
        [[package]]
        name = "requests"
        version = "2.31.0"
    """))
    pyproject_path.write_text(dedent("""\
        [tool.poetry.dependencies]
        requests = "^2.28.0"
    """))

    replace_versions(lock_path)

    updated = pyproject_path.read_text()
    assert '2.31.0' in updated
    assert '2.28.0' not in updated


def test_replace_versions_updates_uv_versions(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'uv.lock'
    pyproject_path = fix_test_cache / 'pyproject.toml'

    lock_path.write_text(dedent("""\
        [[package]]
        name = "click"
        version = "8.2.0"
    """))
    pyproject_path.write_text(dedent("""\
        [project]
        dependencies = [
            "click>=8.0.0",
        ]
    """))

    replace_versions(lock_path)

    updated = pyproject_path.read_text()
    assert '8.2.0' in updated
    assert '8.0.0' not in updated


def test_replace_versions_invalid_lock_name_raises(fix_test_cache: Path) -> None:
    lock_path = fix_test_cache / 'invalid.lock'
    lock_path.write_text('')

    with pytest.raises(NotImplementedError):
        replace_versions(lock_path)
