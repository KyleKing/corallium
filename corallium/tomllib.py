"""Export tomllib."""

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # noqa: F401
