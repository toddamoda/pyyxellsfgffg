#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to generate charges due to simple dark current process with a user array."""

from typing import Literal

from pyxel.detectors import Detector
from pyxel.util import (
    load_cropped_and_aligned_image,
    set_random_seed
)
from pyxel.models.charge_generation.simple_dark_current import calculate_simple_dark_current

def simple_dark_current_user_array(
        detector: Detector,
        filename: str,
        position: tuple[int, int] = (0, 0),
        align: (
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
        ) = None,
        seed = None
) -> None:
    """Add dark current to the detector charge using a fixed array.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    filename : str
        Path to the array or image.
    position: tuple[int, int]
        Starting row and column of the fixed dark current.
    align: Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    
    """

    dr_2d = load_cropped_and_aligned_image(
        shape=(detector.geometry.row,detector.geometry.col),
        filename=filename,
        position_x=position[0],
        position_y=position[1],
        align=align,
    )

    with set_random_seed(seed):
        dark_current_array = calculate_simple_dark_current(
            detector.geometry.row,
            num_cols=detector.geometry.col,
            current=dr_2d,
            exposure_time=detector.time_step
        ).astype(float)

    detector.charge.add_charge_array(dark_current_array)
