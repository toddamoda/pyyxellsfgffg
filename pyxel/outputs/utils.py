#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""General purpose functions to save data."""

import logging
import re
from collections.abc import Mapping
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol

import numpy as np
from typing_extensions import Literal

from pyxel import __version__ as version
from pyxel.options import global_options
from pyxel.util import complete_path

if TYPE_CHECKING:
    # Import 'DataTree'
    try:
        from xarray.core.datatree import DataTree
    except ImportError:
        from datatree import DataTree  # type: ignore[assignment]  # noqa: F401

    from astropy.io import fits


class SaveToFileProtocol(Protocol):
    """Protocol defining a callable to save data into a file."""

    def __call__(
        self,
        current_output_folder: Path,
        data: Any,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
        header: Optional[Mapping] = None,
    ) -> Path: ...


ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png", "jpg", "jpeg"]


# TODO: Refactor this in 'def apply_run_number(folder, template_filename) -> Path'.
#       See #332.
def apply_run_number(template_filename: Path, run_number: Optional[int] = None) -> Path:
    """Convert the file name numeric placeholder to a unique number.

    Parameters
    ----------
    template_filename
    run_number

    Returns
    -------
    output_path: Path
    """
    template_str = str(template_filename)

    def get_number(string: str) -> int:
        search = re.search(r"\d+$", string.split(".")[-2])
        if not search:
            return 0

        return int(search.group())

    if "?" in template_str:
        if run_number is not None:
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(run_number + 1)
        else:
            path_str_for_glob = template_str.replace("?", "*")
            dir_list = glob(path_str_for_glob)
            num_list: list[int] = sorted(get_number(d) for d in dir_list)
            if num_list:
                next_num = num_list[-1] + 1
            else:
                next_num = 1
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(next_num)

    output_path = Path(output_str)

    return output_path


def to_fits(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional["fits.Header"] = None,
) -> Path:
    """Write array to :term:`FITS` file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.fits"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.fits"

    full_filename: Path = filename.resolve()
    logging.info("Save to FITS - filename: '%s'", full_filename)

    from astropy.io import fits  # Late import to speed-up general import time

    if header is None:
        header = fits.Header()

    header["PYXEL_V"] = (version, "Pyxel version")

    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(full_filename, overwrite=False, output_verify="exception")

    return full_filename


def to_hdf(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write detector object to HDF5 file."""
    # Late import to speedup start-up time
    import h5py as h5

    from pyxel.detectors import Detector

    if not isinstance(data, Detector):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.h5"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.h5"

    full_filename: Path = filename.resolve()

    with h5.File(full_filename, "w") as h5file:
        h5file.attrs["pyxel-version"] = version
        if name == "detector":
            detector_grp = h5file.create_group("detector")
            for array, name in zip(
                [
                    data.signal.array,
                    data.image.array,
                    data.photon.array,
                    data.pixel.array,
                    data.charge.frame,
                ],
                ["Signal", "Image", "Photon", "Pixel", "Charge"],
            ):
                dataset = detector_grp.create_dataset(name, shape=np.shape(array))
                dataset[:] = array
        else:
            raise NotImplementedError
            # detector_grp = h5file.create_group("data")
            # dataset = detector_grp.create_dataset(name, shape=np.shape(data))
            # dataset[:] = data
    return filename


def to_npy(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write Numpy array to Numpy binary npy file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.npy"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.npy"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    np.save(file=full_filename, arr=data)
    return full_filename


def to_txt(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write data to txt file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.txt"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.txt"

    full_filename: Path = filename.resolve()
    np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

    return full_filename


def to_csv(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write Pandas Dataframe or Numpy array to a CSV file."""
    # Late import
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.csv"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.csv"

    full_filename = filename.resolve()
    try:
        data.to_csv(full_filename, float_format="%g")
    except AttributeError:
        np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

    return full_filename


def to_png(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write Numpy array to a PNG image file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    # Late import to speedup start-up time
    from PIL import Image

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.png"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.png"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    im = Image.fromarray(data)
    im.save(full_filename)

    return full_filename


def to_jpg(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: Optional[int] = None,
    header: Optional[Mapping] = None,
) -> Path:
    """Write Numpy array to a JPG image file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    # Late import to speedup start-up time
    from PIL import Image

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.jpg"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.jpg"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    im = Image.fromarray(data)
    im.save(full_filename)

    return full_filename


def to_netcdf(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = False,
    run_number: Optional[int] = None,
) -> Path:
    """Write Xarray dataset to NetCDF file.

    Parameters
    ----------
    data: Dataset
    name: str

    Returns
    -------
    filename: Path
    """
    # Late import
    import xarray as xr

    try:
        from xarray.core.datatree import DataTree
    except ImportError:
        from datatree import DataTree  # type: ignore[assignment]

    if not isinstance(data, (xr.Dataset, DataTree)):
        raise TypeError

    name = name.replace(".", "_")
    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )
    filename = full_output_folder.joinpath(name + ".nc")
    data.to_netcdf(filename, engine="h5netcdf")
    return filename


def to_file(
    out_format: ValidFormat,
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = False,
    run_number: Optional[int] = None,
) -> Path:
    save_methods: Mapping[ValidFormat, SaveToFileProtocol] = {
        "fits": to_fits,
        "hdf": to_hdf,
        "npy": to_npy,
        "txt": to_txt,
        "csv": to_csv,
        "png": to_png,
        "jpg": to_jpg,
        "jpeg": to_jpg,
    }

    func: SaveToFileProtocol = save_methods[out_format]

    filename = func(
        current_output_folder=current_output_folder,
        data=data,
        name=name,
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
        # header=header,
    )

    return filename
