#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models: photon shot noise."""
from typing import Literal, Optional

import numpy as np

from pyxel.detectors import Detector
from pyxel.util import deprecated, set_random_seed


def compute_poisson_noise(array: np.ndarray) -> np.ndarray:
    """Compute Poisson noise using the input array.

    Parameters
    ----------
    array : ndarray
        Input array.

    Returns
    -------
    ndarray
        Output array.
    """
    output = np.random.poisson(lam=array).astype(array.dtype)
    return output


def compute_gaussian_noise(array: np.ndarray) -> np.ndarray:
    """Compute Gaussian noise using the input array. Standard deviation is square root of the values.

    Parameters
    ----------
    array : ndarray
        Input array.

    Returns
    -------
    output: ndarray
        Output array.
    """
    output = np.random.normal(loc=array, scale=np.sqrt(array))
    return output


def compute_noise(
    array: np.ndarray,
    type: str = "poisson",  # noqa: A002
) -> np.ndarray:
    """Compute shot noise for an input array. It can be either Poisson noise or Gaussian.

    Parameters
    ----------
    array : ndarray
        Input array.
    type : str, optional
        Choose either 'poisson' or 'normal'. Default is Poisson noise.

    Returns
    -------
    output: ndarray
        Output array.
    """
    if type == "poisson":
        output = compute_poisson_noise(array)
        return output
    elif type == "normal":
        output = compute_gaussian_noise(array)
        return output
    else:
        raise ValueError("Invalid noise type!")


@deprecated(
    "Model 'pyxel.models.photon_generation.shot_noise' is deprecated and will be"
    " removed in version 2. Use model 'pyxel.models.photon_collection.shot_noise'"
    " instead."
)
def shot_noise(
    detector: Detector,
    type: Literal["poisson", "normal"] = "poisson",  # noqa: A002
    seed: Optional[int] = None,
) -> None:
    """Add shot noise to the flux of photon per pixel. It can be either Poisson noise or Gaussian.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    type : str, optional
        Choose either 'poisson' or 'normal'. Default is Poisson noise.
    seed : int, optional
        Random seed.
    """
    with set_random_seed(seed):
        noise_array = compute_noise(array=detector.photon.array, type=type)

    detector.photon.array = noise_array
