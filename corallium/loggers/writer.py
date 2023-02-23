"""Generic Log Writer."""

from beartype import beartype
from beartype.typing import Any


@beartype
def writer(
    message: str,  # noqa: ARG001
    *,
    is_header: bool,  # noqa: ARG001
    _this_level: int,
    _is_text: bool,
    # Logger-specific parameters that need to be initialized with partial(...)
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Generic log writer.."""
    raise NotImplementedError('The writer is for testing hot-swapping and has not yet been implemented')
