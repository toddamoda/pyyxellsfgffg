#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Readout noise model."""

import numpy as np
from astropy.units import Quantity

from pyxel.detectors import CMOS
from pyxel.detectors.channels import Channels
from pyxel.util import set_random_seed
from collections.abc import Sequence

def create_noise_cmos(
    shape: tuple[int, int],
    readout_noise: Quantity,
    readout_noise_std: Quantity,
    sensitivity_2d: Quantity,
) -> np.ndarray:
    """Create noise to signal array for :term:`CMOS` detectors.

    Parameters
    ----------
    shape : tuple[int, int]
        The shape of the detector array (rows, columns).
    readout_noise : float
        The mean readout noise level per pixel.
    readout_noise_std : float
        The standard deviation of the readout noise
    sensitivity_2d : float
        Charge readout sensitivity could be a scalar or a 2D array.

    Returns
    -------
    ndarray
        The generated 2D noise array.
    """
    # Generate the noise based on the calculated sensitivities
    noise_mean_2d: Quantity = readout_noise * sensitivity_2d
    noise_std_2d: Quantity = readout_noise_std * sensitivity_2d

    # Generate the noise with Gaussian distribution
    sigma_2d = np.random.normal(
        loc=noise_mean_2d.to("V").value,
        scale=noise_std_2d.to("V").value,
        size=shape,
    )
    sigma_2d = sigma_2d.clip(min=0.0)  # Ensure noise values are non-negative

    # TODO: Is it correct ?
    noise_2d = np.random.normal(scale=sigma_2d)

    return Quantity(noise_2d, unit="V")

def create_noise_cmos_bychan(
    shape: tuple[int, int],
    readout_noise_bychan: np.ndarray[Quantity],
    readout_noise_std: Quantity,
    sensitivity_2d: Quantity,
) -> np.ndarray:
    noise_2d = np.zeros(shape)
    for x in range(readout_noise_bychan.shape[0]):
        for y in range(readout_noise_bychan.shape[1]):
            (slice_x, slice_y) = Channels.get_channel_slices(
                shape, readout_noise_bychan.shape, x, y)
            view_chan = noise_2d[slice_x, slice_y]
            view_chan[:,:] = create_noise_cmos(
                view_chan.shape, readout_noise_bychan[x,y],
                readout_noise_std, sensitivity_2d)
    return noise_2d

def output_node_noise_cmos(
    detector: CMOS,
    readout_noise: float | Sequence[Sequence[float]],
    readout_noise_std: float | Sequence[Sequence[float]],
    seed: int | None = None,
) -> None:
    """Output node noise model for :term:`CMOS` detectors where readout is statistically independent for each pixel.

    Parameters
    ----------
    detector : CMOS
        Pyxel :term:`CMOS` object.
    readout_noise : float
        Mean readout noise for the array in units of electrons. Unit: electron
    readout_noise_std : float
        Readout noise standard deviation in units of electrons. Unit: electron
    seed : int, optional
        Random seed.

    Raises
    ------
    TypeError
        Raised if the 'detector' is not a :term:`CMOS` object.
    ValueError
        Raised if 'readout_noise_std' is negative.
    """
    if not isinstance(detector, CMOS):
        raise TypeError("Expecting a 'CMOS' detector object.")

    if isinstance(readout_noise, float):
        readout_noise_bychan = np.ndarray(detector.geometry.channels.matrix.shape)
        readout_noise_bychan.fill(readout_noise)
    else:
        readout_noise_bychan = np.array(readout_noise)

    readout_noise_bychan = Quantity(readout_noise_bychan, unit="electron")

    if readout_noise_std < 0.0:
        raise ValueError("'readout_noise_std' must be positive.")

    charge_readout_sensitivity = Quantity(
        detector.characteristics.charge_to_volt_conversion,
        unit="V/electron",
    )

    with set_random_seed(seed):
        noise_2d: Quantity = create_noise_cmos_bychan(
            shape=detector.signal.shape,
            readout_noise_bychan=readout_noise_bychan,
            readout_noise_std=Quantity(readout_noise_std, unit="electron"),
            sensitivity_2d=charge_readout_sensitivity,
        )

    detector.signal += noise_2d
