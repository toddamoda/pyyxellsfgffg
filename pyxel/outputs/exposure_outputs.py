#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Single outputs."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol, Union

from pyxel.outputs import Outputs, ValidFormat, ValidName

if TYPE_CHECKING:
    import xarray as xr

    # Import 'DataTree'
    try:
        from xarray.core.datatree import DataTree
    except ImportError:
        from datatree import DataTree  # type: ignore[assignment]

    class SaveToFile(Protocol):
        """TBW."""

        def __call__(self, data: Any, name: str, with_auto_suffix: bool = True) -> Path:
            """TBW."""
            ...


class ExposureOutputs(Outputs):
    """Collection of methods to save the data buckets from a Detector for an Exposure pipeline.

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
    """

    def __init__(
        self,
        output_folder: Union[str, Path],
        custom_dir_name: str = "",
        save_data_to_file: Optional[
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]]
        ] = None,
        save_exposure_data: Optional[Sequence[Mapping[str, Sequence[str]]]] = None,
    ):
        super().__init__(
            output_folder=output_folder,
            custom_dir_name=custom_dir_name,
            save_data_to_file=save_data_to_file,
        )

        self.save_exposure_data: Optional[Sequence[Mapping[str, Sequence[str]]]] = (
            save_exposure_data
        )

    def save_exposure_outputs(self, dataset: Union["xr.Dataset", "DataTree"]) -> None:
        """Save the observation outputs such as the dataset.

        Parameters
        ----------
        dataset: Dataset
        """

        save_methods: dict[str, SaveToFile] = {"nc": self.save_to_netcdf}

        if self.save_exposure_data is None:
            return

        dct: Mapping[str, Sequence[str]]
        for dct in self.save_exposure_data:
            first_item, *_ = dct.items()
            obj, format_list = first_item

            if obj != "dataset":
                raise NotImplementedError(f"Object {obj} unknown.")

            out_format: str
            for out_format in format_list:
                if out_format not in save_methods:
                    raise ValueError(f"Format {out_format} not a valid save method!")

                func = save_methods[out_format]
                func(data=dataset, name=obj)
