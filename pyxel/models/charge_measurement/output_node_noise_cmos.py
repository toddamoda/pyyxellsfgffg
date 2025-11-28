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


def create_noise_cmos(
    signal_2d: Quantity,
    readout_noise: Quantity,
    readout_noise_std: Quantity,
    sensitivity_2d: Quantity,
) -> Quantity:
    """Add noise to signal array for :term:`CMOS` detectors.

    Parameters
    ----------
    signal_2d : Quantity
        Input signal in V.
    readout_noise : Quantity
        The mean readout noise level per pixel.
    readout_noise_std : Quantity
        The standard deviation of the readout noise
    sensitivity_2d : Quantity
        Charge readout sensitivity could be a scalar or a 2D array.

    Returns
    -------
    Quantity
        The generated 2D noise array.
    """
    # Generate the noise based on the calculated sensitivities
    noise_mean_2d: Quantity = readout_noise * sensitivity_2d
    noise_std_2d: Quantity = readout_noise_std * sensitivity_2d

    # Generate the noise with Gaussian distribution
    sigma_2d = np.random.normal(
        loc=noise_mean_2d.to_value("V"),
        scale=noise_std_2d.to_value("V"),
        size=signal_2d.shape,
    )
    sigma_2d = sigma_2d.clip(min=0.0)  # Ensure noise values are non-negative

    noise_2d = np.random.normal(loc=signal_2d.to_value("V"), scale=sigma_2d)

    return Quantity(noise_2d, unit="V")


def create_noise_cmos_bychan(
    channels: Channels,
    detector_shape: tuple[int, int],
    readout_noise_bychan: dict[str, float],
    readout_noise_std_bychan: dict[str, float],
    sensitivity_2d: Quantity,
) -> np.ndarray:
    """Create noise to signal array for :term:`CMOS` detectors, with different parameters per-channel.

    Parameters
    ----------
    channels : Channels
        Channels of the detector
    detector_shape : tuple[int, int]
        The shape of the detector array (rows, columns).
    readout_noise_bychan : dict[str, float]
        The mean readout noise level per pixel, per-channel.
    readout_noise_std_bychan : dict[str, float]
        The standard deviation of the readout noise, per-channel.
    sensitivity_2d : float
        Charge readout sensitivity could be a scalar or a 2D array.

    Returns
    -------
    ndarray
        The generated 2D noise array.
    """
    noise_2d = np.zeros(detector_shape)
    for chan_label in list(channels):
        this_chan_view = noise_2d[
            channels.get_channel_slices(detector_shape, chan_label)
        ]
        this_chan_view[:, :] = create_noise_cmos(
            this_chan_view.shape,
            readout_noise_bychan[chan_label],
            readout_noise_std_bychan[chan_label],
            sensitivity_2d,
        )
    return Quantity(noise_2d, unit="V")


def output_node_noise_cmos(
    detector: CMOS,
    readout_noise: float | dict[str, float],
    readout_noise_std: float | dict[str, float],
    seed: int | None = None,
) -> None:
    """Apply an output-node readout noise model for :term:`CMOS` detectors where readout is statistically independent for each pixel.

    The noise can be provided either as scalar values (uniform across the entire detector) or as dictionaries mapping
    channel labels to per-channel values.

    Parameters
    ----------
    detector : CMOS
        Pyxel :term:`CMOS` object.
    readout_noise : float or dict of float
        Mean readout noise for the array in units of electrons in electron:
        - If as float is provided, the value is applied uniformly to all pixels.
        - If a dict is provided, each key must correspond to a channel label in ``detector.geometry.channels``.
    readout_noise_std : float
        Standard deviation of the readout noise in electron (must be non-negative):
        - If as float is provided, the value is applied uniformly to all pixels.
        - If a dict is provided, each key must correspond to a channel label in ``detector.geometry.channels``.
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

    charge_readout_sensitivity = Quantity(
        detector.characteristics.charge_to_volt_conversion,
        unit="V/electron",
    )

    if isinstance(readout_noise, (int, float)) and isinstance(
        readout_noise_std, (int, float)
    ):
        ##########################################
        # Uniform noise across the full detector #
        ##########################################
        if readout_noise_std < 0.0:
            raise ValueError("'readout_noise_std' must be positive.")

        with set_random_seed(seed):
            noise_2d: Quantity = create_noise_cmos(
                signal_2d=Quantity(detector.signal),
                readout_noise=Quantity(readout_noise, unit="electron"),
                readout_noise_std=Quantity(readout_noise_std, unit="electron"),
                sensitivity_2d=charge_readout_sensitivity,
            )
    else:
        ##########################################
        # Noise per-channel                      #
        ##########################################

        if not detector.geometry.channels:
            raise ValueError(
                "Per-channel readout noise was provided, but the detector "
                "does not define any geometry channels."
            )

        readout_noise_bychan = dict()
        readout_noise_std_bychan = dict()

        for chan_label in list(detector.geometry.channels):
            ro = (
                readout_noise
                if isinstance(readout_noise, (int, float))
                else readout_noise[chan_label]
            )
            ros = (
                readout_noise_std
                if isinstance(readout_noise_std, (int, float))
                else readout_noise_std[chan_label]
            )
            if ros < 0.0:
                raise ValueError("'readout_noise_std' must be positive.")

            readout_noise_bychan[chan_label] = Quantity(ro, unit="electron")
            readout_noise_std_bychan[chan_label] = Quantity(ros, unit="electron")

        with set_random_seed(seed):
            noise_2d = create_noise_cmos_bychan(
                channels=detector.geometry.channels,
                detector_shape=detector.geometry.shape,
                readout_noise_bychan=readout_noise_bychan,
                readout_noise_std_bychan=readout_noise_std_bychan,
                sensitivity_2d=charge_readout_sensitivity,
            )

    detector.signal += noise_2d
