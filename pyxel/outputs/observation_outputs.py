#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""TBW."""

import operator
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol, Union

from pyxel.outputs import Outputs, ValidFormat, ValidName

if TYPE_CHECKING:
    from pyxel.observation import CustomMode, ProductMode, SequentialMode
    from pyxel.observation.deprecated import ObservationResult

    class SaveToFile(Protocol):
        """TBW."""

        def __call__(self, data: Any, name: str, with_auto_suffix: bool = True) -> Path:
            """TBW."""
            ...


class ObservationOutputs(Outputs):
    """Collection of methods to save the data buckets from a Detector for an Observation pipeline.

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
        save_observation_data: Optional[Sequence[Mapping[str, Sequence[str]]]] = None,
    ):
        super().__init__(
            output_folder=output_folder,
            save_data_to_file=save_data_to_file,
            custom_dir_name=custom_dir_name,
        )

        self.save_observation_data: Optional[Sequence[Mapping[str, Sequence[str]]]] = (
            save_observation_data
        )

    def _save_observation_datasets_deprecated(
        self,
        result: "ObservationResult",
        mode: Union["ProductMode", "SequentialMode", "CustomMode"],
    ) -> None:
        """Save the result datasets from parametric mode on disk.

        Parameters
        ----------
        result: Result
        mode: ParameterMode
        """
        warnings.warn(
            "Deprecated. Will be removed in Pyxel 2.0", DeprecationWarning, stacklevel=1
        )

        from pyxel.observation import SequentialMode

        dataset_names = ("dataset", "parameters", "logs")

        save_methods: dict[str, SaveToFile] = {"nc": self.save_to_netcdf}

        if self.save_observation_data is not None:
            dct: Mapping[str, Sequence[str]]
            for dct in self.save_observation_data:
                first_item, *_ = dct.items()
                obj, format_list = first_item

                if obj not in dataset_names:
                    raise ValueError(
                        "Please specify a valid result dataset names ('dataset',"
                        " 'parameters', 'logs')."
                    )

                if isinstance(mode, SequentialMode) and obj == "dataset":
                    dct = operator.attrgetter(obj)(result)
                    for key, value in dct.items():
                        if format_list is not None:
                            for out_format in format_list:
                                if out_format not in save_methods:
                                    raise ValueError(
                                        "Format "
                                        + out_format
                                        + " not a valid save method!"
                                    )

                                func = save_methods[out_format]
                                func(data=value, name=obj + "_" + key)

                else:
                    ds = operator.attrgetter(obj)(result)

                    if format_list is not None:
                        for out_format in format_list:
                            if out_format not in save_methods:
                                raise ValueError(
                                    "Format " + out_format + " not a valid save method!"
                                )

                            func = save_methods[out_format]
                            func(data=ds, name=obj)
