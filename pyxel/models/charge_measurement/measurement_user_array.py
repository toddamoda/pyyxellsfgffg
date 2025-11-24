#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from typing import Literal
import numpy as np

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image

def simple_measurement_user_array(
        detector: Detector,
        filename: str,
        position: tuple[int, int] = (0, 0),
        align: (
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
        ) = None,
) -> None:
    """Convert the pixel array into a signal array using a fixed pattern of gain.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    filename : str
        Path to the array or image.
    # figure_of_merit : float
    #     Gain figure of merit.
    position: tuple[int, int]
        Starting row and column of the fixed pattern.
    align: Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    
    """

    gain_2d = load_cropped_and_aligned_image(
        shape=(detector.geometry.row,detector.geometry.col),
        filename=filename,
        position_x=position[0],
        position_y=position[1],
        align=align,
    )

    detector.signal.array = np.asarray(detector.pixel.array * gain_2d, dtype=float)
