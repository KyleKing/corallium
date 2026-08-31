## Conventions

- Use `beartype.typing` imports (`List`, `Dict`, `Tuple`, `Sequence`) instead of
    `list[...]`, `dict[...]` syntax for beartype-checked signatures;
    `from __future__ import annotations` doesn't fully resolve this for runtime type
    checking with beartype
