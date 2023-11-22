#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage to load images and tables."""

import csv
from collections.abc import Sequence
from contextlib import suppress
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional, Union

import fsspec
import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import DTypeLike
from PIL import Image

from pyxel.options import global_options


def load_image(filename: Union[str, Path]) -> np.ndarray:
    """Load a 2D image.

    Parameters
    ----------
    filename : str or Path
        Filename to read an image.
        {.npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff} are accepted.

    Returns
    -------
    ndarray
        A 2D array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.

    Examples
    --------
    >>> from pyxel import load_image
    >>> load_image("frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("https://hostname/folder/frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("another_frame.npy")
    array([[-1.10136521, -0.93890239, ...]])

    >>> load_image("rgb_frame.jpg")
    array([[234, 211, ...]])
    """
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        full_filename: Path = filename.expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)

    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    if suffix.startswith(".fits"):
        # with fits.open(url_path, use_fsspec=True, fsspec_kwargs=extras) as file_handler:
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            from astropy.io import fits  # Late import to speed-up general import time

            with BytesIO(file_handler.read()) as content:
                data_2d: np.ndarray = fits.getdata(content)

    elif suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            data_2d = np.load(file_handler)

    elif suffix.startswith((".txt", ".data")):
        for sep in ("\t", " ", ",", "|", ";"):
            with suppress(ValueError):
                with fsspec.open(url_path, mode="r", **extras) as file_handler:
                    data_2d = np.loadtxt(file_handler, delimiter=sep, ndmin=2)
                break
        else:
            raise ValueError(f"Cannot find the separator for filename '{url_path}'.")

    elif suffix.startswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            image_2d = Image.open(file_handler)
            image_2d_converted = image_2d.convert("LA")  # RGB to grayscale conversion

        data_2d = np.array(image_2d_converted)[:, :, 0]

    else:
        raise ValueError(
            "Image format not supported. List of supported image formats: "
            ".npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff, .tif."
        )

    return data_2d


# TODO: needs tests!
# TODO: add units
# TODO: reduce complexity and remove ruff noqa.
# ruff: noqa: C901, PTH123
def load_image_v2(
    filename: Union[str, Path],
    rename_dims: dict,
    data_path: Union[str, int, None] = None,
) -> xr.DataArray:
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        full_filename: Path = filename.expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)

    else:
        url_path = filename

    if suffix.startswith(".fits"):
        from astropy.io import fits

        with fits.open(url_path) as hdus:
            if data_path is None:
                data_path = 0
            assert isinstance(data_path, int)
            image_data: np.ndarray = hdus[data_path].data
            # TODO: check if hdus data_path is image hdu.
            if image_data.ndim == 2:
                data_array = xr.DataArray(image_data, dims=["y", "x"])
            elif image_data.ndim == 3:
                dims = []
                for ax in [0, 1, 2]:
                    for key, value in rename_dims.items():
                        if value == ax:
                            dims.append(key)
                            break
                    else:
                        raise ValueError
                data_array = xr.DataArray(image_data, dims=dims)
            else:
                raise NotImplementedError()

    elif suffix.startswith(".npy"):
        with open(url_path, mode="rb") as file_handler:
            data_2d: np.ndarray = np.load(file_handler)
            assert data_2d.ndim == 2
            data_array = xr.DataArray(data_2d, dims=["y", "x"])

    elif suffix.startswith((".txt", ".data")):
        for sep in ("\t", " ", ",", "|", ";"):
            with suppress(ValueError):
                with open(url_path) as file_handler:
                    data_2d = np.loadtxt(file_handler, delimiter=sep, ndmin=2)
                break

        else:
            raise ValueError(f"Cannot find the separator for filename '{url_path}'.")
        data_array = xr.DataArray(data_2d, dims=["y", "x"])

    elif suffix.startswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")):
        with open(url_path, mode="rb") as file_handler:
            image_2d = Image.open(file_handler)
            image_2d_converted = image_2d.convert("LA")  # RGB to grayscale conversion
            data_array = xr.DataArray(image_2d_converted, dims=["y", "x"])

    return data_array


def load_table(
    filename: Union[str, Path],
    header: bool = False,
    dtype: DTypeLike = "float",
) -> "pd.DataFrame":
    """Load a table from a file and returns a pandas dataframe. No header is expected in xlsx.

    Parameters
    ----------
    filename : str or Path
        Filename to read the table.
        {.npy, .xlsx, .csv, .txt., .data} are accepted.
    header : bool, default: False
        Remove the header.
    dtype

    Returns
    -------
    DataFrame

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.
    """
    # Late import to speedup start-up time
    import pandas as pd

    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        full_filename = Path(filename).expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)
    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    if suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.DataFrame(np.load(file_handler), dtype=dtype)

    elif suffix.startswith(".xlsx"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.read_excel(
                file_handler,
                header=0 if header else None,
                dtype=float,
            )

    elif suffix.startswith((".txt", ".data", ".csv")):
        # Read file
        with fsspec.open(url_path, mode="r", **extras) as file_handler:
            data: str = file_handler.read()

        valid_delimiters: Sequence[str] = ("\t", " ", ",", "|", ";")
        valid_delimiters_str = "".join(valid_delimiters)

        # Find a delimiter
        try:
            dialect = csv.Sniffer().sniff(data, delimiters=valid_delimiters_str)
        except csv.Error as exc:
            raise ValueError("Cannot find the separator") from exc

        delimiter: str = dialect.delimiter

        if delimiter not in valid_delimiters:
            raise ValueError(f"Cannot find the separator. {delimiter=!r}")

        with StringIO(data) as file_handler:
            if suffix.startswith("csv"):
                table = pd.read_csv(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    dtype=dtype,
                )
            else:
                table = pd.read_table(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    dtype=dtype,
                )

    else:
        raise ValueError("Only .npy, .xlsx, .csv, .txt and .data implemented.")

    return table


# TODO: needs tests!
# TODO: add units
def load_table_v2(
    filename: Union[str, Path],
    rename_cols: Optional[dict] = None,
    data_path: Union[str, int, None] = None,
    header: bool = False,
) -> pd.DataFrame:
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        full_filename = Path(filename).expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)
    else:
        url_path = filename

    if suffix.startswith(".fits"):
        from astropy.io import fits
        from astropy.table import Table

        with fits.open(url_path) as hdus:
            if data_path is None:
                data_path = 0
            assert isinstance(data_path, int)
            assert isinstance(hdus[data_path], (fits.TableHDU, fits.BinTableHDU))
        table: pd.DataFrame = Table.read(url_path, hdu=data_path).to_pandas()
        if rename_cols:
            col_new = {value: key for key, value in rename_cols.items()}
            table_data = table.rename(columns=col_new)[list(rename_cols)]
        else:
            table_data = table

    elif suffix.startswith((".txt", ".data", ".csv")):
        with open(url_path) as file_handler:
            data: str = file_handler.read()
        valid_delimiters: Sequence[str] = ("\t", " ", ",", "|", ";")
        valid_delimiters_str = "".join(valid_delimiters)

        # Find a delimiter
        try:
            dialect = csv.Sniffer().sniff(data, delimiters=valid_delimiters_str)
        except csv.Error as exc:
            raise ValueError("Cannot find the separator") from exc

        delimiter: str = dialect.delimiter

        if delimiter not in valid_delimiters:
            raise ValueError(f"Cannot find the separator. {delimiter=!r}")

        with StringIO(data) as file_handler:
            if suffix.startswith("csv"):
                table = pd.read_csv(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    usecols=[key for key, value in rename_cols.items()]
                    if rename_cols
                    else None,
                )
            else:
                table = pd.read_table(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    usecols=[key for key, value in rename_cols.items()]
                    if rename_cols
                    else None,
                )
            if rename_cols:
                table_data = table.rename(columns=rename_cols)
            else:
                table_data = table
    else:
        raise NotImplementedError

    return table_data


def load_dataarray(filename: Union[str, Path]) -> "xr.DataArray":
    """Load a ``DataArray`` image.

    Parameters
    ----------
    filename : str of Path

    Returns
    -------
    DataArray
        A multi-dimensional array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    """
    if isinstance(filename, Path):
        full_filename: Path = filename.expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)

    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    import xarray as xr

    with fsspec.open(url_path, mode="rb", **extras) as file_handler:
        data_array = xr.load_dataarray(file_handler)

    return data_array


def load_datacube(filename: Union[str, Path]) -> np.ndarray:
    """Load a 3D datacube.

    Parameters
    ----------
    filename : str or Path
        Filename to read a datacube.
        {.npy} are accepted.

    Returns
    -------
    array : ndarray
        A 3D array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.
    """
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        full_filename: Path = filename.expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path: str = str(full_filename)

    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    if suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            data_3d: np.ndarray = np.load(file_handler)
        if np.ndim(data_3d) != 3:
            raise ValueError("Input datacube is not 3-dimensional!")

    else:
        raise ValueError(
            "Image format not supported. List of supported image formats: .npy"
        )

    return data_3d
