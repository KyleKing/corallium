from typing import Any, BinaryIO

class TOMLDecodeError(ValueError): ...

def load(fp: BinaryIO, /) -> dict[str, Any]: ...
def loads(s: str, /) -> dict[str, Any]: ...

# Re-export as module for backward compatibility
class Tomllib:
    TOMLDecodeError = TOMLDecodeError
    load = staticmethod(load)
    loads = staticmethod(loads)

__all__ = ('TOMLDecodeError', 'Tomllib', 'load', 'loads')
