# Corallium Development Notes

## Python Version Support

This project supports Python 3.9+. To maintain compatibility:

- Use `beartype.typing` imports (`List`, `Dict`, `Tuple`, `Sequence`) instead of `list[...]`, `dict[...]` syntax
- The `from __future__ import annotations` doesn't fully resolve this for runtime type checking with beartype
- Example: `from beartype.typing import List, Dict` instead of using `list[T]` directly
