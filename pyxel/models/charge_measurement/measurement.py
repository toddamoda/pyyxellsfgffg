#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Charge readout model."""

from typing import Literal

from astropy.units import Quantity
import numpy as np

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image


def apply_gain(pixel_2d: Quantity, gain: Quantity) -> Quantity:
    """Apply an electronic gain (in V/e-) to convert Pixel charges (in e-) into Signal (in V).

    Parameters
    ----------
    pixel_2d : ndarray
        2D array of pixels. Unit: e-
    gain : float
        Gain factor to apply. Unit: V/e-

    Returns
    -------
    Quantity
        2D array of signals. Unit: V
    """
    new_data_2d = pixel_2d * gain
    return new_data_2d.to("V")


def simple_measurement(detector: Detector, gain: float | None = None) -> None:
    """Convert detector Pixel charge values (in electron) into Signal values (in Volt) using a specified gain.

    Notes
    -----
    If no gain is provided, the detector's internal ``detector.characteristics.charge_to_volt_conversion`` parameter is used.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    gain : float, optional
        Gain factor to apply. If not provided, the default is ``detector.characteristics.charge_to_volt_conversion``. Unit: V/e-
    """

    if gain is None:
        gain_to_apply = Quantity(
            detector.characteristics.charge_to_volt_conversion,
            unit="V/electron",
        )

    else:
        gain_to_apply = Quantity(gain, unit="V/electron")

    detector.signal = apply_gain(pixel_2d=Quantity(detector.pixel), gain=gain_to_apply)
    # Apply a gain (in V/e-) to a pixel array (in e-)

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
