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
    wavelength: float,
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
    if not scaling_factor > 0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0:
        raise ValueError("Only positive values accepted for responsivity.")

    output = array * responsivity * scaling_factor

    return output.astype("float64")


def pulse_processing(
    detector: MKID,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> None:
    """Phase-pulse processor.

    This model is derived from :cite:p:`Dodkins`; more information can be found on the website :cite:p:`Mazin`.

    Parameters
    ----------
    detector: MKID
        Pyxel :term:`MKID` detector object.
    wavelength: float
        Wavelength [μm].
    responsivity: float
        Responsivity of the pixel.
    scaling_factor: float
        Scaling factor taking into account the missing pieces of superconducting physics,
        as well as the resonator quality factor, the bias power,
        the quasi-particle losses, etc.
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting an MKID object for the detector.")
    if not wavelength > 0:
        raise ValueError("Only positive values accepted for wavelength.")

    detector.phase.array = convert_to_phase(
        array=detector.charge.array,
        wavelength=wavelength,
        responsivity=responsivity,
        scaling_factor=scaling_factor,
    )

    ## IN FIERI, for a single pixel:

    # Boltzmann's constant [J K^-1]
    boltzmann_cst: float = const.k_B.value

    t_c = 1.26 # Hardcoded; used also in /pyxel/models/readout_electronics/dead_time.py
    delta = 1.76 * boltzmann_cst * t_c # Used also in /pyxel/models/readout_electronics/dead_time.py

    R = np.sqrt(0.57 * 6.62607004 * 1.e-34 * 299792458. / (wavelength * 1.e-6 * 0.2 * delta)) / (2. * np.sqrt(2. * np.log(2.)))

    sigma_lambda = wavelength / R / (2 * np.sqrt(2 * np.log(2)))

    mu, sigma = wavelength, sigma_lambda

    np.random.seed(42)

    Gaussian_samples = np.random.normal(mu, sigma, detector.phase.array) 
