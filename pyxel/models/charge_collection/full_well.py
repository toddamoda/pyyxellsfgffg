#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel full well models."""

from typing import Literal

import numpy as np

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image


def apply_simple_full_well_capacity(array: np.ndarray, fwc: int) -> np.ndarray:
    """Apply full well capacity to an array.

    Parameters
    ----------
    array : ndarray
    fwc:  int

    Returns
    -------
    ndarray
    """
    array[array > fwc] = fwc
    return array


def simple_full_well(detector: Detector, fwc: int | None = None) -> None:
    """Limit the amount of charge in pixel due to full well capacity.

    Uses full well capacity in the characteristics of the detector object if not overridden by the function argument.

    Parameters
    ----------
    detector : Detector
    fwc : int
    """
    if fwc is None:
        fwc_input = detector.characteristics.full_well_capacity
    else:
        fwc_input = fwc

    if fwc_input < 0:
        raise ValueError("Full well capacity should be a positive number.")

    charge_array = apply_simple_full_well_capacity(
        array=detector.pixel.array, fwc=fwc_input
    )

    detector.pixel.array = charge_array

def apply_simple_full_well_capacity_user_array(
        data: np.array,
        fwc: np.array
) -> np.array:
    """Apply full well capacity to an array.

    Parameters
    ----------
    data : ndarray
    fwc:  int

    Returns
    -------
    ndarray
    """

    return np.minimum(data, fwc)


def simple_full_well_user_array(
        detector: Detector,
        filename: str,
        position: tuple[int, int] = (0, 0),
        align: (
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
        ) = None,
) -> None:
    """Limit the amount of charge in pixel due to full well capacity with a
    user-supplied per-pixel limit.

    Parameters
    ----------
    detector : Detector
    filename : str
    position : tuple[int, int] = (0, 0),
    align    : (
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
        ) = None
    """

    fwc = load_cropped_and_aligned_image(
        shape=(detector.geometry.row,detector.geometry.col),
        filename=filename,
        position_x=position[0],
        position_y=position[1],
        align=align,
    )

    charge_array = apply_simple_full_well_capacity_user_array(detector.pixel.array, fwc)

    detector.pixel.array = charge_array


