#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model for replicating the gain register in an EMCCD, including clock-induced-charge (CIC)."""
import numba
import numpy as np

from pyxel.detectors import CCD


def multiplication_register(
    detector: CCD,
    total_gain: int,
    gain_elements: int,
    pcic_rate: float,
    scic_rate: float
) -> None:
    """Calculate total gain of image with EMCCD multiplication register.

    Parameters
    ----------
    detector : CCD
    total_gain : int
    gain_elements : int
        Amount of single stage gain elements in the EMCCD register.
    pCIC_rate : float
        Parallel CIC rate
    sCIC_rate : float
        Serial CIC rate
    """

    if total_gain < 0 or gain_elements < 0:
        raise ValueError("Wrong input parameter")

    detector.pixel.array = multiplication_register_poisson(
        image_cube=detector.pixel.array,
        total_gain=total_gain,
        gain_elements=gain_elements,
        pcic_rate=pcic_rate,
        scic_rate=scic_rate
    ).astype(float)


@numba.njit
def poisson_register(lam, new_image_cube_pix, gain_elements, scic_rate):
    """Calculate the total gain of a single pixel from EMCCD register elements.

    Parameters
    ----------
    lam : float
    new_image_cube_pix : int
    gain_elements : int
    sCIC_rate : float

    Returns
    -------
    new_image_cube_pix : int
    """

    new_image_cube_pix = new_image_cube_pix

    for _ in range(gain_elements):
        # Add possibility for a CIC event at each register stage
        new_image_cube_pix += np.random.poisson(scic_rate)

        # Each electron increase has chance for impact ionization, so one needs
        # to loop over all electrons at each gain stage.
        gain_electrons = 0
        for _ in range(np.floor(new_image_cube_pix)):
            gain_electrons += np.random.poisson(lam)
        new_image_cube_pix += gain_electrons

    return new_image_cube_pix


@numba.njit(parallel=True)
def multiplication_register_poisson(
    image_cube: np.ndarray,
    total_gain: int,
    gain_elements: int,
    pcic_rate: float,
    scic_rate: float
) -> np.ndarray:
    """Calculate total gain of image from EMCCD register.

    Parameters
    ----------
    image_cube : np.ndarray
    total_gain : int
    gain_elements : int
        Amount of single stage gain elements in the EMCCD register.
    pcic_rate : float
        Parallel CIC rate.
    scic_rate : float
        Serial CIC rate.

    Returns
    -------
    new_image_cube : np.ndarray
    """

    new_image_cube = np.zeros_like(image_cube, dtype=np.int32)

    # Generate and add pCIC to the frame
    pcic = np.random.poisson(pcic_rate, image_cube.shape)
    new_image_cube += pcic

    lam = total_gain ** (1 / gain_elements) - 1
    yshape, xshape = image_cube.shape

    for j in numba.prange(0, yshape):
        for i in numba.prange(0, xshape):
            new_image_cube[j, i] = poisson_register(
                lam=lam,
                new_image_cube_pix=image_cube[j, i],
                gain_elements=gain_elements,
                scic_rate=scic_rate
            )

    return new_image_cube
