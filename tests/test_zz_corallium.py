"""Final test alphabetically (zz) to catch general integration cases."""

from pathlib import Path

from corallium import __version__
from corallium.tomllib import tomllib


def test_version():
    """Check that PyProject and package __version__ are equivalent."""
    data = Path('pyproject.toml').read_text(encoding='utf-8')

    result = tomllib.loads(data)['tool']['poetry']['version']

    assert result == __version__
