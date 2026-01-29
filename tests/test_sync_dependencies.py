"""Tests for sync_package_dependencies."""

from pathlib import Path
from textwrap import dedent

import pytest

from corallium.sync_dependencies import (
    _collect_poetry_dependencies,
    _collect_pyproject_versions,
    _collect_uv_dependencies,
    _extract_base_version,
    _is_dependency_section,
    _parse_lock_file,
    _parse_pep621_dependency,
    _replace_pyproject_versions,
    replace_versions,
)
from corallium.tomllib import tomllib


@pytest.fixture
def poetry_pyproject() -> str:
    """Poetry format pyproject.toml."""
    return dedent("""
        [tool.poetry.dependencies]
        python = "^3.9"
        requests = ">=2.0.0,<3.0.0"
        flask = "2.0.0"

        [tool.poetry.group.dev.dependencies]
        pytest = "^7.0.0"
    """)


@pytest.fixture
def uv_pyproject() -> str:
    """UV format pyproject.toml."""
    return dedent("""
        [project]
        dependencies = [
            "requests>=2.0.0",
            "flask>=2.0.0",
        ]

        [project.optional-dependencies]
        dev = [
            "pytest>=7.0.0",
        ]

        [dependency-groups]
        docs = [
            "mkdocs>=1.5.0",
        ]
    """)


@pytest.mark.parametrize(
    ('version_spec', 'expected'),
    [
        ('>=1.0.0,<2.0.0', '1.0.0'),
        ('1.0.0', '1.0.0'),
        ('^1.0.0', '1.0.0'),
        ('~=1.2.3', '1.2.3'),
    ],
)
def test_extract_base_version(version_spec: str, expected: str):
    """Test _extract_base_version with various version specifications."""
    assert _extract_base_version(version_spec) == expected


@pytest.mark.parametrize(
    ('dependency', 'expected'),
    [
        ('requests>=2.0.0', ('requests', '2.0.0')),
        ('flask==3.0.0', ('flask', '3.0.0')),
        ('mkdocstrings[python]>=0.26.1', ('mkdocstrings', '0.26.1')),
        ('package[extra1,extra2]>=1.0.0', ('package', '1.0.0')),
        ('package', None),
        ('package[extra]', None),
        ('package>=1.0.0,<2.0.0', ('package', '1.0.0')),
        ('zope.interface>=5.0.0', ('zope.interface', '5.0.0')),
        ('backports.tarfile>=1.0.0', ('backports.tarfile', '1.0.0')),
    ],
)
def test_parse_pep621_dependency(dependency: str, expected: tuple[str, str] | None):
    """Test _parse_pep621_dependency with various dependency formats."""
    assert _parse_pep621_dependency(dependency) == expected


@pytest.mark.parametrize(
    ('section', 'is_dependency'),
    [
        ('[project]', True),
        ('[project.optional-dependencies]', True),
        ('[dependency-groups]', True),
        ('[tool.poetry.dependencies]', True),
        ('[tool.poetry.group.dev.dependencies]', True),
        ('[project.urls]', False),
        ('[project.scripts]', False),
        ('[tool.ruff]', False),
        ('[tool.mypy]', False),
    ],
)
def test_is_dependency_section(section: str, *, is_dependency: bool):
    """Test _is_dependency_section identification."""
    assert _is_dependency_section(section) == is_dependency


def test_collect_pyproject_versions_poetry(poetry_pyproject: str):
    """Test _collect_pyproject_versions with Poetry format."""
    versions = _collect_pyproject_versions(poetry_pyproject)
    assert versions == {'requests': '2.0.0', 'flask': '2.0.0', 'pytest': '7.0.0'}


def test_collect_pyproject_versions_uv(uv_pyproject: str):
    """Test _collect_pyproject_versions with UV format."""
    versions = _collect_pyproject_versions(uv_pyproject)
    assert versions == {
        'requests': '2.0.0',
        'flask': '2.0.0',
        'pytest': '7.0.0',
        'mkdocs': '1.5.0',
    }


def test_collect_uv_dependencies(uv_pyproject: str):
    """Test _collect_uv_dependencies function."""
    pyproject = tomllib.loads(uv_pyproject)
    versions = _collect_uv_dependencies(pyproject)
    assert versions == {
        'requests': '2.0.0',
        'flask': '2.0.0',
        'pytest': '7.0.0',
        'mkdocs': '1.5.0',
    }


@pytest.mark.parametrize(
    ('dependencies', 'expected'),
    [
        (
            ['mkdocstrings[python]>=0.26.1', 'hypothesis[cli]>=6.112.4'],
            {'mkdocstrings': '0.26.1', 'hypothesis': '6.112.4'},
        ),
    ],
)
def test_collect_uv_dependencies_with_extras(dependencies: list[str], expected: dict[str, str]):
    """Test _collect_uv_dependencies handles packages with extras."""
    pyproject_text = dedent("""
        [project]
        dependencies = {}
    """).format(dependencies)
    pyproject = tomllib.loads(pyproject_text)
    versions = _collect_uv_dependencies(pyproject)
    assert versions == expected


def test_collect_poetry_dependencies(poetry_pyproject: str):
    """Test _collect_poetry_dependencies function."""
    pyproject = tomllib.loads(poetry_pyproject)
    versions = _collect_poetry_dependencies(pyproject)
    assert 'requests' in versions
    assert 'flask' in versions
    assert 'pytest' in versions


def test_collect_pyproject_versions_mixed_format():
    """Test _collect_pyproject_versions with both poetry and uv formats."""
    pyproject_text = dedent("""
        [project]
        dependencies = [
            "requests>=2.0.0",
        ]

        [tool.poetry.dependencies]
        flask = "2.0.0"
    """)
    versions = _collect_pyproject_versions(pyproject_text)
    assert 'requests' in versions
    assert 'flask' in versions
    assert versions['requests'] == '2.0.0'
    assert versions['flask'] == '2.0.0'


@pytest.mark.parametrize(
    ('pyproject_text', 'lock_versions', 'pyproject_versions'),
    [
        (
            dedent("""
                [tool.poetry.dependencies]
                requests = ">=2.0.0,<3.0.0"
                flask = "2.0.0"
            """),
            {'requests': '2.1.0', 'flask': '2.1.0'},
            {'requests': '2.0.0', 'flask': '2.0.0'},
        ),
        (
            dedent("""
                [project]
                dependencies = [
                    "requests>=2.0.0",
                    "flask>=2.0.0",
                ]
            """),
            {'requests': '2.1.0', 'flask': '2.1.0'},
            {'requests': '2.0.0', 'flask': '2.0.0'},
        ),
        (
            dedent("""
                [project.optional-dependencies]
                doc = [
                    "mkdocstrings[python]>=0.26.1",
                ]
            """),
            {'mkdocstrings': '0.27.0'},
            {'mkdocstrings': '0.26.1'},
        ),
        (
            dedent("""
                [project]
                dependencies = ["requests>=2.0.0"]
            """),
            {'requests': '2.1.0'},
            {'requests': '2.0.0'},
        ),
        (
            dedent("""
                [dependency-groups]
                dev = [  # development dependencies
                    "pytest>=7.0.0",
                ]
            """),
            {'pytest': '7.1.0'},
            {'pytest': '7.0.0'},
        ),
    ],
)
def test_replace_pyproject_versions(
    snapshot,
    pyproject_text: str,
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
):
    """Test _replace_pyproject_versions with various formats using snapshots."""
    new_text = _replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text)
    assert new_text == snapshot


@pytest.fixture
def lock_content() -> str:
    """Common lock file content."""
    return dedent("""
        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "flask"
        version = "3.0.0"
    """)


@pytest.mark.parametrize('lock_filename', ['uv.lock', 'poetry.lock'])
def test_parse_lock_file(tmp_path: Path, lock_content: str, lock_filename: str):
    """Test _parse_lock_file with different lock file formats."""
    lock_file = tmp_path / lock_filename
    content = lock_content if lock_filename == 'poetry.lock' else f'version = 1\n{lock_content}'
    lock_file.write_text(content)

    versions = _parse_lock_file(lock_file)
    assert versions == {'requests': '2.31.0', 'flask': '3.0.0'}


def test_end_to_end_replacement(snapshot, tmp_path: Path):
    """Test end-to-end version replacement."""
    uv_lock = tmp_path / 'uv.lock'
    uv_lock.write_text(
        dedent("""
        version = 1

        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "mkdocstrings"
        version = "0.27.0"

        [[package]]
        name = "zope.interface"
        version = "6.0.0"
    """),
    )

    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text(
        dedent("""
        [project]
        name = "test-package"
        dependencies = [
            "requests>=2.28.0",
            "zope.interface>=5.5.0",
        ]

        [project.optional-dependencies]
        doc = [
            "mkdocstrings[python]>=0.26.0",
        ]
    """),
    )

    replace_versions(uv_lock)

    assert pyproject.read_text() == snapshot
