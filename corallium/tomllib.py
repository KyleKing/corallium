"""Export tomllib."""

try:
    import tomllib  # type: ignore[import-not-found] # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found, unused-ignore] # pyright: ignore[reportMissingImports]
__all__ = ('tomllib',)
