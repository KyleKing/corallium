"""Type stubs for tomllib compatibility layer."""

from typing import Any, BinaryIO

class TOMLDecodeError(ValueError): ...

def load(fp: BinaryIO, /) -> dict[str, Any]: ...
def loads(s: str, /) -> dict[str, Any]: ...

# Re-export as module for backward compatibility
class tomllib:
    TOMLDecodeError = TOMLDecodeError
    load = staticmethod(load)
    loads = staticmethod(loads)

__all__ = ('TOMLDecodeError', 'load', 'loads', 'tomllib')
