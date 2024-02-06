"""File utility functions to simplify path logic."""

from pathlib import Path
from typing import Union


def is_path_relative(filename: Union[str, Path]) -> bool:
    """Check if the filename is a relative or absolute path."""
    pth = str(filename)
    if ":" in pth or pth.startswith("\\") or pth.startswith("/"):
        return False
    return True


def complete_path(
    filename: Union[str, Path], working_dir: Union[str, Path, None]
) -> Union[str, Path]:
    """Prefix the filename with the working directory.

    The returned type will be the same as the `filename` type.
    """
    if not working_dir:
        return filename

    if not is_path_relative(filename):
        return filename

    if isinstance(filename, Path):
        return Path(working_dir).joinpath(filename)

    return str(working_dir) + "/" + filename
