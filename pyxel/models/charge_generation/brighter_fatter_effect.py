#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Model for brighter-fatter-effect."""

import numpy as np
from astropy.convolution import convolve_fft

from pyxel.detectors import Detector


def get_bfe(array: np.ndarray) -> np.ndarray:
    """Get bfe array from polynominal function.

    Parameters
    ----------
    array : ndarray
        Input array.

    Returns
    -------
    ndarray
    """

    polynomial_function = np.polynomial.polynomial.Polynomial((0.0, 1.0, 0.0874))
    bfe = polynomial_function(array)

    return bfe


def apply_bfe(
    array: np.ndarray, kernel: np.ndarray, normalize_kernel: bool = True
) -> np.ndarray:
    """Convolve the input array with the brighter-fatter kernel.

    Parameters
    ----------
    kernel
    array : ndarray
        Input array.
    normalize_kernel : bool
        Normalize kernel.

    Returns
    -------
    ndarray
    """

    mean = np.mean(array)

    array_2d = convolve_fft(
        array,
        kernel=kernel,
        boundary="fill",
        fill_value=mean,
        normalize_kernel=normalize_kernel,
    )

    return array_2d


def brighter_fatter(detector: Detector, normalize_kernel: bool = True) -> None:
    """Get BFE for photon array and convolve the photon array with the BFE.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    normalize_kernel : bool
        Normalize kernel.
    """
    bfe = get_bfe(detector.photon.array)

    detector.photon.array = apply_bfe(
        array=detector.photon.array, kernel=bfe, normalize_kernel=normalize_kernel
    )
