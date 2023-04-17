#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to compute basic statistics."""
from collections.abc import Sequence
from typing import Literal, Optional, Union

import xarray as xr
from datatree import DataTree

from pyxel.data_structure import Image, Photon, Pixel, Signal
from pyxel.detectors import Detector


def compute_statistics(
    data_array: xr.DataArray,
    dimensions: Union[str, Sequence[str]] = ("x", "y"),
) -> xr.DataArray:
    """Compute basic statistics.= into a Dataarray.

    Parameters
    ----------
    data_array : DataArray

    Returns
    -------
    DataArray
    """

    var = data_array.var(dim=dimensions)
    mean = data_array.mean(dim=dimensions)
    min_array = data_array.min(dim=dimensions)
    max_array = data_array.max(dim=dimensions)
    count = data_array.count(dim=dimensions)

    statistics: xr.DataArray = count.expand_dims(
        var=[var], mean=[mean], min_array=[min_array], max_array=[max_array]
    )  # ,count=[count])
    #
    # dataset = xr.Dataset().assign_coords(time=absolute_time)
    # dataset["var"] = var
    # dataset["mean"] = mean
    # dataset["min"] = min_array
    # dataset["max"] = max_array
    # dataset["count"] = count

    return statistics

    # detector.processed_data.append(dataset)
    # detector.data["/statistics"] = DataTree(dataset)


def statistics(
    detector: Detector,
    data_structure: Literal["pixel", "photon", "image", "signal"] = "pixel",
    name: Optional[str] = None,
) -> None:
    """Compute basic statistics.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    data_structure : Literal
        Keyword to choose data structure. Can be any from:
        ("pixel", "photon", "image", "signal")
    dimensions : str or Sequence of str
        Dimensions.
    """
    if name is None:
        name = data_structure

    # Extract data from 'detector'
    data_bucket: Union[Pixel, Photon, Image, Signal] = getattr(detector, data_structure)
    data_array: xr.DataArray = data_bucket.to_xarray()

    # Get statistics data
    statistics: xr.DataArray = compute_statistics(data_array)

    parent: str = "/statistics"
    parent_partial: str = f"{parent}/partial"
    key: str = f"{parent}/{name}"
    key_partial: str = f"{parent_partial}/{name}"

    try:
        _ = detector.data[key_partial]
    except KeyError:
        has_key_partial = False
    else:
        has_key_partial = True

    if not has_key_partial:
        data_tree: DataTree = DataTree(statistics)
    else:
        # Concatenate data
        data_tree = detector.data[key_partial].combine_first(statistics)  # type: ignore

    if detector.pipeline_count == (detector.num_steps - 1):
        detector.data[parent_partial].orphan()
        detector.data[key] = data_tree.sortby("mean")
    else:
        detector.data[key_partial] = data_tree
