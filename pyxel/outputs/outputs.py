#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Classes for creating outputs."""

import logging
import warnings
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import numpy as np

from pyxel import __version__ as version
from pyxel.options import global_options
from pyxel.outputs import SaveToFileProtocol, ValidFormat, apply_run_number
from pyxel.outputs.utils import to_csv, to_fits, to_hdf, to_jpg, to_npy, to_png, to_txt
from pyxel.util import complete_path

if TYPE_CHECKING:
    import dask.dataframe as dd
    import pandas as pd
    import xarray as xr

    # Import 'DataTree'
    try:
        from xarray.core.datatree import DataTree
    except ImportError:
        from datatree import DataTree  # type: ignore[assignment]

    from astropy.io import fits

    from pyxel.detectors import Detector
    from pyxel.pipelines import Processor


ValidName = Literal[
    "detector.photon.array",
    "detector.charge.array",
    "detector.pixel.array",
    "detector.signal.array",
    "detector.image.array",
]


def _save_data_2d(
    data_2d: "np.ndarray",
    run_number,
    data_formats: Sequence[ValidFormat],
    current_output_folder: Path,
    name: str,
    prefix: Optional[str] = None,
) -> np.ndarray[Any, np.dtype[np.object_]]:
    save_methods: Mapping[ValidFormat, "SaveToFileProtocol"] = {
        "fits": to_fits,
        "hdf": to_hdf,
        "npy": to_npy,
        "txt": to_txt,
        "csv": to_csv,
        "png": to_png,
        "jpg": to_jpg,
        "jpeg": to_jpg,
    }

    if prefix:
        full_name: str = f"{prefix}_{name}"
    else:
        full_name = name

    filenames: list[str] = []
    for output_format in data_formats:
        func = save_methods[output_format]

        filename = func(
            current_output_folder=current_output_folder,
            data=data_2d,
            name=full_name,
            # with_auto_suffix=with_auto_suffix,
            run_number=run_number,
            # header=header,
        )

        filenames.append(str(filename.relative_to(current_output_folder)))

    return np.array(filenames, dtype=np.object_)


def save_dataarray(
    data_array: "xr.DataArray",
    name: str,
    full_name: str,
    data_formats: Sequence["ValidFormat"],
    current_output_folder: Path,
) -> "dd.DataFrame":
    # Late import
    import numpy as np
    import xarray as xr

    num_elements = int(data_array.isel(y=0, x=0).size)

    if (
        "data_format" in data_array.dims
        or "bucket_name" in data_array.dims
        or "filename" in data_array.dims
    ):
        raise NotImplementedError

    output_data_array: xr.DataArray = xr.apply_ufunc(
        _save_data_2d,
        data_array.reset_coords(drop=True).rename("filename"),  # parameter 'data_2d'
        np.arange(num_elements, dtype=int),  # parameter 'run_number'
        kwargs={
            "data_formats": data_formats,
            "current_output_folder": current_output_folder,
            "name": full_name,
        },
        input_core_dims=[
            ["y", "x"],  # for parameter 'data_2d'
            [],  # for parameter 'run_number'
        ],
        output_core_dims=[["data_format"]],
        vectorize=True,  # loop over non-core dims
        dask="parallelized",
        dask_gufunc_kwargs={"output_sizes": {"data_format": len(data_formats)}},
        output_dtypes=[np.object_],  # TODO: Move this to 'dask_gufunc_kwargs'
    )

    output_dataframe: "dd.DataFrame" = (
        output_data_array.expand_dims("bucket_name")
        .assign_coords(bucket_name=[name], data_format=data_formats)
        .to_dask_dataframe()
    )
    return output_dataframe


def save_datatree(
    data_tree: "DataTree",
    outputs: Sequence[Mapping[ValidName, Sequence[ValidFormat]]],
    current_output_folder: Path,
    with_inherited_coords: bool,
) -> "dd.DataFrame":
    # Late import
    import dask.dataframe as dd
    import xarray as xr

    if not outputs:
        raise NotImplementedError

    lst: list[dd.DataFrame] = []

    dct: Mapping["ValidName", Sequence["ValidFormat"]]
    for dct in outputs:
        full_name: "ValidName"
        data_formats: Sequence["ValidFormat"]
        for full_name, data_formats in dct.items():
            name: str = full_name.removeprefix("detector.").removesuffix(".array")

            # Get a node name
            if with_inherited_coords:
                node_name: str = f"/bucket/{name}"
            else:
                node_name = name

            data_array: Union[xr.DataArray, DataTree] = data_tree[node_name]
            if not isinstance(data_array, xr.DataArray):
                raise TypeError

            output_dataframe: dd.DataFrame = save_dataarray(
                data_array=data_array,
                name=name,
                full_name=full_name,
                data_formats=data_formats,
                current_output_folder=current_output_folder,
            )

            lst.append(output_dataframe)

    if len(lst) == 1:
        return lst[0]
    else:
        return dd.concat(lst)


# TODO: Create a new class that will contain the parameter 'save_data_to_file'
# TODO: Refactor 'Outputs' with a new class 'ExportData'. See #566
class Outputs:
    """Collection of methods to save the data buckets from a Detector.

    Parameters
    ----------
    output_folder : str or Path
        Folder where sub-folder(s) that will be created to save data buckets.
    custom_dir_name : str, optional
        Prefix of the sub-folder name that will be created in the 'output_folder' folder.
        The default prefix is `run_`.
    save_data_to_file : Dict
        Dictionary where key is a 'data bucket' name (e.g. 'detector.photon.array') and value
        is the data format (e.g. 'fits').

        Example:
        {'detector.photon.array': 'fits', 'detector.charge.array': 'hdf', 'detector.image.array':'png'}

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.load("my_config.yaml")
    >>> mode = config.running_mode
    >>> detector = config.detector
    >>> pipeline = config.pipeline

    Run and get 'output_dir'

    >>> result = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)
    >>> result.mode.outputs.current_output_folder
    Path('./output/run_20231219_0920000')

    Change 'output_dir'

    >>> result.mode.outputs.output_folder = "folder1/folder2"
    >>> result.mode.outputs.custom_dir_name = "foo_"
    >>> result = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)
    >>> result.mode.outputs.current_output_folder
    Path('./folder1/folder2/foo_20231219_0922000')
    """

    def __init__(
        self,
        output_folder: Union[str, Path],
        custom_dir_name: str = "",
        save_data_to_file: Optional[
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]]
        ] = None,
    ):
        self._log = logging.getLogger(__name__)

        self._current_output_folder: Optional[Path] = None

        self._output_folder: Path = Path(output_folder)
        self._custom_dir_name: str = custom_dir_name

        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        self.save_data_to_file: Optional[
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]]
        ] = save_data_to_file

    def __repr__(self):
        cls_name: str = self.__class__.__name__

        if self._current_output_folder is None:
            return (
                f"{cls_name}<NO OUTPUT DIR, num_files={self.count_files_to_save()!r}>"
            )
        else:
            return f"{cls_name}<output_dir='{self.current_output_folder!s}', num_files={self.count_files_to_save()!r}>"

    def count_files_to_save(self) -> int:
        """Count number of file(s) to be saved."""
        if self.save_data_to_file is None:
            return 0

        num_files = 0
        for dct in self.save_data_to_file:
            for value in dct.values():
                num_files += len(value)

        return num_files

    @property
    def current_output_folder(self) -> Path:
        """Get directory where all outputs are saved."""
        if self._current_output_folder is None:
            raise RuntimeError("'current_output_folder' is not defined.")

        return self._current_output_folder

    @property
    def output_folder(self) -> Path:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, folder: Union[str, Path]) -> None:
        if not isinstance(folder, (str, Path)):
            raise TypeError(
                "Wrong type for parameter 'folder'. Expecting 'str' or 'Path'."
            )

        self._output_folder = Path(folder)

    @property
    def custom_dir_name(self) -> str:
        return self._custom_dir_name

    @custom_dir_name.setter
    def custom_dir_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Wrong type for parameter 'name'. Expecting 'str'.")

        self._custom_dir_name = name

    def create_output_folder(self) -> None:
        """Create the output folder."""
        output_folder: Path = complete_path(
            filename=self._output_folder,
            working_dir=global_options.working_directory,
        ).expanduser()

        self._current_output_folder = create_output_directory(
            output_folder=output_folder,
            custom_dir_name=self._custom_dir_name,
        )

    def save_to_fits(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
        header: Optional["fits.Header"] = None,
    ) -> Path:
        """Write array to :term:`FITS` file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_fits'.",
            DeprecationWarning,
            stacklevel=1,
        )

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.fits"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.fits"

        full_filename: Path = filename.resolve()
        self._log.info("Save to FITS - filename: '%s'", full_filename)

        from astropy.io import fits  # Late import to speed-up general import time

        if header is None:
            header = fits.Header()

        header["PYXEL_V"] = (version, "Pyxel version")

        hdu = fits.PrimaryHDU(data, header=header)
        hdu.writeto(full_filename, overwrite=False, output_verify="exception")

        return full_filename

    def save_to_hdf(
        self,
        data: "Detector",
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write detector object to HDF5 file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_hdf'.",
            DeprecationWarning,
            stacklevel=1,
        )

        # Late import to speedup start-up time
        import h5py as h5

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.h5"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.h5"

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

    def save_to_txt(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write data to txt file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_txt'.",
            DeprecationWarning,
            stacklevel=1,
        )

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.txt"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.txt"

        full_filename: Path = filename.resolve()
        np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

        return full_filename

    def save_to_csv(
        self,
        data: "pd.DataFrame",
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_csv'.",
            DeprecationWarning,
            stacklevel=1,
        )

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.csv"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.csv"

        full_filename = filename.resolve()
        try:
            data.to_csv(full_filename, float_format="%g")
        except AttributeError:
            np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

        return full_filename

    def save_to_npy(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write Numpy array to Numpy binary npy file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_npy'.",
            DeprecationWarning,
            stacklevel=1,
        )

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.npy"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.npy"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        np.save(file=full_filename, arr=data)
        return full_filename

    def save_to_png(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write Numpy array to a PNG image file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_png'.",
            DeprecationWarning,
            stacklevel=1,
        )

        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.png"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.png"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    def save_to_jpeg(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write Numpy array to a JPEG image file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_jpg'.",
            DeprecationWarning,
            stacklevel=1,
        )

        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.jpeg"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.jpeg"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    def save_to_jpg(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Path:
        """Write Numpy array to a JPG image file."""
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_jpg'.",
            DeprecationWarning,
            stacklevel=1,
        )

        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.jpg"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.jpg"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    def save_to_file(
        self,
        processor: "Processor",
        prefix: Optional[str] = None,
        with_auto_suffix: bool = True,
        run_number: Optional[int] = None,
    ) -> Mapping[str, Mapping[str, str]]:
        """Save outputs into file(s).

        Parameters
        ----------
        run_number
        prefix
        with_auto_suffix
        processor : Processor

        Returns
        -------
        list of Path
            TBW.
        """
        if not self.save_data_to_file:
            return {}

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

        all_filenames: dict[str, dict[str, str]] = {}

        dct: Mapping[ValidName, Sequence[ValidFormat]]
        for dct in self.save_data_to_file:
            # TODO: Why looking at first entry ? Check this !
            # Get first entry of `dict` 'item'
            first_item: tuple[ValidName, Sequence[ValidFormat]]
            first_item, *_ = dct.items()

            valid_name: ValidName
            format_list: Sequence[ValidFormat]
            valid_name, format_list = first_item

            data: np.ndarray = np.array(processor.get(valid_name))

            if prefix:
                name: str = f"{prefix}_{valid_name}"
            else:
                name = valid_name

            partial_filenames: dict[str, str] = {}
            out_format: ValidFormat
            for out_format in format_list:
                func: SaveToFileProtocol = save_methods[out_format]

                if out_format in ("png", "jpg", "jpeg"):
                    if valid_name != "detector.image.array":
                        raise ValueError(
                            "Cannot save non-digitized data into image formats."
                        )
                    maximum = (
                        2**processor.detector.characteristics.adc_bit_resolution - 1
                    )
                    rescaled_data = (255.0 / maximum * data).astype(np.uint8)

                    filename: Path = func(
                        current_output_folder=self.current_output_folder,
                        data=rescaled_data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                    )

                elif out_format == "fits":
                    # Create FITS header
                    from astropy.io import fits

                    header = fits.Header()

                    line: str
                    for line in processor.pipeline.describe():
                        header.add_history(line)

                    previous_header: Optional[fits.Header] = (
                        processor.detector._headers.get(valid_name)
                    )
                    if previous_header is not None:
                        for card in previous_header.cards:
                            key, *_ = card

                            if key in ("SIMPLE", "BITPIX") or key.startswith("NAXIS"):
                                continue

                            header.append(card)

                    filename = func(
                        current_output_folder=self.current_output_folder,
                        data=data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                        header=header,
                    )

                else:
                    filename = func(
                        current_output_folder=self.current_output_folder,
                        data=data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                    )

                partial_filenames[out_format] = filename.name

            all_filenames[valid_name] = partial_filenames

        return all_filenames

    def save_to_netcdf(
        self,
        data: Union["xr.Dataset", "DataTree"],
        name: str,
        with_auto_suffix: bool = False,
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
        warnings.warn(
            "Deprecated. This will be removed in a future version of Pyxel. "
            "Please use function 'to_netcdf'.",
            DeprecationWarning,
            stacklevel=1,
        )

        name = name.replace(".", "_")
        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )
        filename = current_output_folder.joinpath(name + ".nc")
        data.to_netcdf(filename, engine="h5netcdf")
        return filename


# TODO: the log file should directly write in 'output_dir'
def save_log_file(output_dir: Path) -> None:
    """Move log file to the outputs directory of the simulation."""
    log_file: Path = Path("pyxel.log").resolve()
    if log_file.exists():
        new_log_filename = output_dir.joinpath("pyxel.log")
        log_file.rename(new_log_filename)


def create_output_directory(
    output_folder: Union[str, Path], custom_dir_name: Optional[str] = None
) -> Path:
    """Create output directory in the output folder.

    Parameters
    ----------
    output_folder: str or Path
    custom_dir_name

    Returns
    -------
    Path
        Output dir.
    """

    add = ""
    count = 0

    date_str: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not custom_dir_name:
        prefix_dir: str = "run_"
    else:
        prefix_dir = custom_dir_name

    while True:
        try:
            output_dir: Path = (
                Path(output_folder).joinpath(f"{prefix_dir}{date_str}{add}").resolve()
            )

            output_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            count += 1
            add = "_" + str(count)
            continue

        else:
            return output_dir
