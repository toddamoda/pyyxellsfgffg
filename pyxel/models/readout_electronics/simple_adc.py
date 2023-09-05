#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Simple ADC model functions."""

from typing import Literal

import numpy as np
from numpy.typing import DTypeLike

from pyxel.detectors import Detector


def apply_simple_adc(
    signal: np.ndarray,
    bit_resolution: int,
    voltage_min: float,
    voltage_max: float,
    dtype: DTypeLike,
) -> np.ndarray:
    """Apply digitization.

    Parameters
    ----------
    signal : array
        Input signal.
    bit_resolution : int
        ADC bit resolution.
    voltage_min : float
    voltage_max : float
    dtype : DTypeLike

    Returns
    -------
    array

    Examples
    --------
    >>> apply_simple_adc(
    ...     signal=np.array([-0.1, 0.0, 3.0, 6.0, 6.1]),
    ...     bit_resolution=8,
    ...     voltage_min=0.0,
    ...     voltage_max=6.0,
    ...     dtype=np.uint8,
    ... )
    array([0, 0, 127, 255, 255], dtype=np.uint8
    """
    output = (
        (np.clip(signal, a_min=voltage_min, a_max=voltage_max) - voltage_min)
        * (2**bit_resolution - 1)
        / (voltage_max - voltage_min)
    )

    return np.trunc(output).astype(dtype)


def simple_adc(
    detector: Detector,
    data_type: Literal["uint16", "uint32", "uint64", "uint"] = "uint32",
) -> None:
    """Apply simple Analog to Digital conversion.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    data_type : str
        The desired data-type for the Image array. The data-type must be an unsigned integer.
        Valid values: 'uint16', 'uint32', 'uint64', 'uint'
        Invalid values: 'int16', 'int32', 'int64', 'int', 'float'...
    """

    bit_resolution = detector.characteristics.adc_bit_resolution
    voltage_min, voltage_max = detector.characteristics.adc_voltage_range

    try:
        d_type: np.dtype = np.dtype(data_type)
    except TypeError as ex:
        raise TypeError(
            "Can not locate the type defined as `data_type` argument in yaml file."
        ) from ex

    if not issubclass(d_type.type, np.integer):
        raise TypeError("Expecting a signed/unsigned integer.")

    detector.image.array = apply_simple_adc(
        signal=detector.signal.array,
        bit_resolution=bit_resolution,
        voltage_min=voltage_min,
        voltage_max=voltage_max,
        dtype=d_type,
    )
