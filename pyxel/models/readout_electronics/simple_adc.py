#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Simple ADC model functions."""

from typing import Literal, Optional

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
    """Apply a simple Analog-to-Digital Converted (ADC) digitization.

    This functions simulates the behaviour of an ADC by quantizing a continous signal
    to a discrete digital representation based on the provided bit resolution and voltage range.

    Parameters
    ----------
    signal : array
        Continous input signal to be quantized.
    bit_resolution : int
        ADC bit resolution used for quantization.
    voltage_min : float
        The minimum voltage level in the input signal's range.
    voltage_max : float
        The maximum voltage level in the input signal's range.
    dtype : DTypeLike
        Desired data type of the output signal.

    Returns
    -------
    array
        The quantized digital representation.

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

    Notes
    -----
    This function performs the following steps:
    1. Clips the input signal to the specified voltage range [voltage_min, voltage_max].
    1. Normalizes the clipped signal to the range [0, 2^bit_resolution - 1].
    1. Rounds the normalized values to the nearest integer using truncation.
    1. Converts the resulting array to the specified data type (dtype).
    """
    output = (
        (np.clip(signal, a_min=voltage_min, a_max=voltage_max) - voltage_min)
        * (2**bit_resolution - 1)
        / (voltage_max - voltage_min)
    )

    return np.trunc(output).astype(dtype)


def _get_dtype(bit_resolution: int) -> np.dtype:
    """Get NumPy data type based on a given bit resolution.

    Parameters
    ----------
    bit_resolution : int
        Number of bits representing the data.

    Returns
    -------
    np.dtype
        Numpy data type corresponding to the provided bit resolution.

    Raises
    ------
    ValueError
        Raised if the bit resolution does not fall within the supported range [1, 64]

    Examples
    --------
    >>> _get_dtype(8)
    dtype('uint8')
    >>> _get_dtype(12)
    dtype('uint16')
    """
    if 1 <= bit_resolution <= 8:
        return np.dtype(np.uint8)
    elif 9 <= bit_resolution <= 16:
        return np.dtype(np.uint16)
    elif 17 <= bit_resolution <= 32:
        return np.dtype(np.uint32)
    elif 33 <= bit_resolution <= 64:
        return np.dtype(np.uint64)
    else:
        raise ValueError(
            "Bit resolution does not fall within the supported range [1, 64]"
        )


def simple_adc(
    detector: Detector,
    data_type: Optional[Literal["uint8", "uint16", "uint32", "uint64"]] = None,
) -> None:
    """Apply simple Analog-to-Digital Converter (ADC) to the `signal` bucket from `Detector`.

    This model simulates the behaviour of an ADC based on `detector.characteristics.adc_bit_resolution`.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    data_type : str
        The desired data-type for the Image array. The data-type must be an unsigned integer.
        If not provided, the data type is determined based on `detector.characteristics.adc_bit_resolution`.
        Valid values: 'uint8', 'uint16', 'uint32', 'uint64'
        Invalid values: 'int16', 'int32', 'int64', 'int', 'float'...
    """

    bit_resolution = detector.characteristics.adc_bit_resolution
    voltage_min, voltage_max = detector.characteristics.adc_voltage_range

    if data_type:
        try:
            d_type: np.dtype = np.dtype(data_type)
        except TypeError as ex:
            raise TypeError(
                "Can not locate the type defined as `data_type` argument in yaml file."
            ) from ex

        if not issubclass(d_type.type, np.integer):
            raise TypeError("Expecting a signed/unsigned integer.")
    else:
        d_type = _get_dtype(bit_resolution)

    detector.image.array = apply_simple_adc(
        signal=detector.signal.array,
        bit_resolution=bit_resolution,
        voltage_min=voltage_min,
        voltage_max=voltage_max,
        dtype=d_type,
    )
