from typing import Any, BinaryIO

class TOMLDecodeError(ValueError): ...

def load(fp: BinaryIO, /) -> dict[str, Any]: ...
def loads(s: str, /) -> dict[str, Any]: ...

# Re-export tomllib module (the actual module from stdlib or tomli)
class _TomllibModule:
    TOMLDecodeError = TOMLDecodeError
    load = staticmethod(load)
    loads = staticmethod(loads)

tomllib: _TomllibModule

__all__ = ('TOMLDecodeError', 'tomllib')
