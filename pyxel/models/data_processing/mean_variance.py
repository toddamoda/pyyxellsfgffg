#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to compute Mean-Variance."""
from typing import Literal, Optional, Union

import xarray as xr
from datatree import DataTree

from pyxel.data_structure import Image, Photon, Pixel, Signal
from pyxel.detectors import Detector


def compute_mean_variance(data_array: xr.DataArray) -> xr.DataArray:
    """Compute mean-variance into a DataArray.

    Parameters
    ----------
    data_array : DataArray

    Returns
    -------
    DataArray

    Examples
    --------
    >>> data_array
    <xarray.DataArray 'image' (y: 100, x: 100)>
    array([[10406, 10409, 10472, ..., 10394, 10302, 10400],
           [10430, 10473, 10443, ..., 10427, 10446, 10452],
           [10456, 10524, 10479, ..., 10502, 10435, 10499],
           ...,
           [10381, 10385, 10552, ..., 10471, 10443, 10468],
           [10381, 10396, 10381, ..., 10472, 10380, 10509],
           [10455, 10431, 10382, ..., 10405, 10429, 10491]], dtype=uint32)
    Coordinates:
      * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
      * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    Attributes:
        units:      adu
        long_name:  Image

    >>> mean_variance = compute_mean_variance(data_array)
    >>> mean_variance
    <xarray.DataArray 'variance' (mean: 1)>
    array([2130.03464796])
    Coordinates:
      * mean     (mean) float64 1.043e+04
    Attributes:
        units:    adu^2
    """
    mean = data_array.mean(dim=["y", "x"])
    variance = data_array.var(dim=["y", "x"])

    mean_variance: xr.DataArray = variance.expand_dims(mean=[mean])
    mean_variance.name = "variance"

    if unit := data_array.attrs.get("units"):
        mean_variance["mean"].attrs["units"] = unit
        mean_variance.attrs["units"] = f"{unit}^2"

    return mean_variance


def mean_variance(
    detector: Detector,
    data_structure: Literal["pixel", "photon", "image", "signal"] = "image",
    name: Optional[str] = None,
) -> None:
    """Compute mean-variance and store it in '.data' bucket.

    Parameters
    ----------
    detector : Detector
    data_structure : 'pixel', 'photon', 'image' or 'signal'
        Data bucket to use for the linear regression.
    name : str, optional
        Name to use for the result.

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.load("exposure_mode.yaml")

    Run exposure mode with 'data_processing/mean_variance' model

    >>> data_tree = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    Get results

    >>> data_tree["/data/mean_variance"]
    DataTree('mean_variance', parent="data")
    └── DataTree('image')
            Dimensions:   (mean: 19)
            Coordinates:
              * mean      (mean) float64 5.723e+03 1.144e+04 ... 5.238e+04 5.238e+04
            Data variables:
                variance  (mean) float64 3.238e+06 1.294e+07 2.91e+07 ... 4.03e+05 3.778e+05

    >>> mean_variance = data_tree["/data/mean_variance/image/variance"]
    >>> mean_variance
    <xarray.DataArray 'variance' (mean: 19)>
    array([ 3238372.98476575, 12940428.69349581, 29101219.32832065,
           51711636.17586413, 68442386.58453502, 73522594.46113221,
           70591532.43505114, 54799694.83319437, 36351341.15700997,
           19577907.89405003,  7877859.3907925 ,  2284048.60403896,
             839388.11541348,   605169.50892288,   527554.54598688,
             474694.21759011,   434408.74359875,   402970.36722454,
             377784.5672024 ])
    Coordinates:
      * mean     (mean) float64 5.723e+03 1.144e+04 ... 5.238e+04 5.238e+04
    Attributes:
        units:    adu^2

    Display mean-variance plot

    >>> mean_variance.plot()

    .. figure:: _static/mean_variance_plot.png
        :scale: 70%
        :alt: Mean-Variance plot
        :align: center
    """
    if name is None:
        name = data_structure

    # Extract data from 'detector'
    data_bucket: Union[Pixel, Photon, Image, Signal] = getattr(detector, data_structure)
    data_array: xr.DataArray = data_bucket.to_xarray(dtype=float)

    # Get Mean-Variance data
    mean_variance: xr.DataArray = compute_mean_variance(data_array)

    parent: str = "/mean_variance"
    parent_partial: str = f"{parent}/partial"
    key: str = f"{parent}/{name}"
    key_partial: str = f"{parent_partial}/{name}"

    # TODO: Use 'detector.data.get(...)'
    try:
        _ = detector.data[key_partial]
    except KeyError:
        has_key_partial = False
    else:
        has_key_partial = True

    if not has_key_partial:
        data_tree: DataTree = DataTree(mean_variance)
    else:
        # Concatenate data
        data_tree = detector.data[key_partial].combine_first(mean_variance)  # type: ignore

    if detector.pipeline_count == (detector.num_steps - 1):
        detector.data[parent_partial].orphan()
        detector.data[key] = data_tree.sortby("mean")
    else:
        detector.data[key_partial] = data_tree
