#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel full well user array models."""

from typing import Literal

import numpy as np

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image

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