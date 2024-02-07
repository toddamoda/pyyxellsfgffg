#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""File utility functions to simplify path logic."""

from pathlib import Path, PurePath
from typing import Union

from typing_extensions import overload


def is_path_relative(filename: Union[str, Path]) -> bool:
    """Check if the filename is a relative or absolute path.

    Examples
    --------
    >>> from pathlib import Path
    >>> is_path_relative("file.fits")
    True
    >>> is_path_relative(Path("/file.fits"))
    False
    >>> is_path_relative("https://server/file.fits")
    False
    """
    if isinstance(filename, PurePath):
        return not filename.is_absolute()

    if ":" in filename or filename.startswith("\\") or filename.startswith("/"):
        return False
    return True


@overload
def complete_path(filename: str, working_dir: Union[str, Path, None]) -> str: ...


@overload
def complete_path(filename: Path, working_dir: Union[str, Path, None]) -> Path: ...


def complete_path(
    filename: Union[str, Path], working_dir: Union[str, Path, None]
) -> Union[str, Path]:
    """Prefix the filename with the working directory.

    The returned type will be the same as the `filename` type.

    Examples
    --------
    >>> from pathlib import Path
    >>> complete_path(filename="file.fits", working_directory=None)
    'file.fits'
    >>> complete_path(filename=Path("file.fits"), working_directory="/folder")
    Path('/folder/file.fits')
    >>> complete_path(filename="/my_folder/file.fits", working_dir="/folder")
    '/my_folder/file.fits'
    >>> complete_path(filename="https://server/file.fits", working_dir="/folder")
    'https://server/file.fits'
    """
    if not working_dir or not is_path_relative(filename):
        return filename

    if isinstance(filename, Path):
        return Path(working_dir).joinpath(filename)

    return str(working_dir) + "/" + filename
