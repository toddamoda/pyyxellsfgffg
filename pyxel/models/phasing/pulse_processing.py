#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase-pulse processing model."""

import astropy.constants as const
import numpy as np

from pyxel.detectors import MKID


def convert_to_phase(
    array: np.ndarray,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> np.ndarray:
    """Convert an array of charges into an array of phase pulses.

    Parameters
    ----------
    array: ndarray
    responsivity: float
    scaling_factor: float

    Returns
    -------
    ndarray
    """
    if not scaling_factor > 0.0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0.0:
        raise ValueError("Only positive values accepted for responsivity.")

    output = array * responsivity * scaling_factor

    return output.astype("float64")


def pulse_processing(
    detector: MKID,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
    t_c: float = 1.26,
    eta_pb: float = 0.59,
    f: float = 0.2,
) -> None:
    """Phase-pulse processor.

    This model is derived from :cite:p:`Dodkins`; more information can be found on the website :cite:p:`Mazin`.

    Parameters
    ----------
    detector: MKID
        Pyxel :term:`MKID` detector object.
    wavelength: float
        Wavelength. Unit: um
    responsivity: float
        Responsivity of the pixel.
    scaling_factor: float
        Scaling factor taking into account the missing pieces of superconducting physics,
        as well as the resonator quality factor, the bias power,
        the quasi-particle losses, etc.
    t_c : float [used also in /pyxel/models/readout_electronics/dead_time.py]
        Material dependent critical temperature. Unit: K
    eta_pb: float
        Superconducting pair-breaking efficiency.
    f: float
        Fano's factor.
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting an MKID object for the detector.")
    if not wavelength > 0.0:
        raise ValueError("Only positive values accepted for wavelength.")

    detector.phase.array = convert_to_phase(
        array=detector.charge.array,
        responsivity=responsivity,
        scaling_factor=scaling_factor,
    )

    # IN FIERI:

    # Boltzmann's constant [J K^-1]
    boltzmann_cst: float = const.k_B.value

    # Planck's constant [J s]
    planck_cst: float = const.h.value

    # Speed of light in vacuum [m s^-1]
    c_cst: float = const.c.value

    delta = (
        1.76 * boltzmann_cst * t_c
    )  # [used also in /pyxel/models/readout_electronics/dead_time.py]

    r = np.sqrt(eta_pb * planck_cst * c_cst / (wavelength * 1.0e-6 * f * delta)) / (
        2.0 * np.sqrt(2.0 * np.log(2.0))
    )

    sigma_lambda = wavelength / (r * (2 * np.sqrt(2 * np.log(2))))

    mu, sigma = wavelength, sigma_lambda

    np.random.seed(42)

    gaussian_samples = np.random.normal(
        mu, sigma, detector.phase.array[0][0]
    )  # To be continued...
