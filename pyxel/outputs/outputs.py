#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Classes for creating outputs."""

import logging
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol, Union

import numpy as np

from pyxel import __version__ as version
from pyxel.options import global_options
from pyxel.util import complete_path

if TYPE_CHECKING:
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

    class SaveToFile(Protocol):
        """TBW."""

        def __call__(
            self,
            data: Any,
            name: str,
            with_auto_suffix: bool = True,
            run_number: Optional[int] = None,
        ) -> Path:
            """TBW."""
            ...


ValidName = Literal[
    "detector.photon.array",
    "detector.charge.array",
    "detector.pixel.array",
    "detector.signal.array",
    "detector.image.array",
]
ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png", "jpg", "jpeg"]


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
            return f"{cls_name}<NO OUTPUT DIR>"
        else:
            return f"{cls_name}<output_dir='{self.current_output_folder!s}'>"

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
    ) -> Sequence[Path]:
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
        save_methods: Mapping[ValidFormat, SaveToFile] = {
            "fits": self.save_to_fits,
            "hdf": self.save_to_hdf,
            "npy": self.save_to_npy,
            "txt": self.save_to_txt,
            "csv": self.save_to_csv,
            "png": self.save_to_png,
            "jpg": self.save_to_jpg,
            "jpeg": self.save_to_jpeg,
        }

        filenames: list[Path] = []

        dct: Mapping[ValidName, Sequence[ValidFormat]]
        if self.save_data_to_file:
            for dct in self.save_data_to_file:
                # TODO: Why looking at first entry ? Check this !
                # Get first entry of `dict` 'item'
                first_item: tuple[ValidName, Sequence[ValidFormat]]
                first_item, *_ = dct.items()

                obj: ValidName
                format_list: Sequence[ValidFormat]
                obj, format_list = first_item

                data: np.ndarray = np.array(processor.get(obj))

                if prefix:
                    name: str = f"{prefix}_{obj}"
                else:
                    name = obj

                out_format: ValidFormat
                for out_format in format_list:
                    func: SaveToFile = save_methods[out_format]

                    if out_format in ("png", "jpg", "jpeg"):
                        if obj != "detector.image.array":
                            raise ValueError(
                                "Cannot save non-digitized data into image formats."
                            )
                        maximum = (
                            2**processor.detector.characteristics.adc_bit_resolution - 1
                        )
                        rescaled_data = (255.0 / maximum * data).astype(np.uint8)

                        image_filename: Path = func(
                            data=rescaled_data,
                            name=name,
                            with_auto_suffix=with_auto_suffix,
                            run_number=run_number,
                        )

                        full_image_filename: Path = complete_path(
                            filename=image_filename,
                            working_dir=global_options.working_directory,
                        )
                        filenames.append(full_image_filename)

                    elif out_format == "fits":
                        # Create FITS header
                        from astropy.io import fits

                        header = fits.Header()

                        line: str
                        for line in processor.pipeline.describe():
                            header.add_history(line)

                        previous_header: Optional[fits.Header] = (
                            processor.detector._headers.get(obj)
                        )
                        if previous_header is not None:
                            for card in previous_header.cards:
                                key, *_ = card

                                if key in ("SIMPLE", "BITPIX") or key.startswith(
                                    "NAXIS"
                                ):
                                    continue

                                header.append(card)

                        filename: Path = self.save_to_fits(
                            data=data,
                            name=name,
                            with_auto_suffix=with_auto_suffix,
                            run_number=run_number,
                            header=header,
                        )

                        filenames.append(filename)

                    else:
                        filename = func(
                            data=data,
                            name=name,
                            with_auto_suffix=with_auto_suffix,
                            run_number=run_number,
                        )

                        full_filename: Path = complete_path(
                            filename, global_options.working_directory
                        )
                        filenames.append(full_filename)

        return filenames

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
        name = name.replace(".", "_")
        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )
        filename = current_output_folder.joinpath(name + ".nc")
        data.to_netcdf(filename, engine="h5netcdf")
        return filename


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
