#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model for replicating the gain register in an EMCCD."""

import numba
import numpy as np

from pyxel.detectors import CCD
from pyxel.models import Metadata, MetadataModel


def multiplication_register(
    detector: CCD,
    total_gain: int,
    gain_elements: int,
) -> None:
    """Calculate total gain of image with EMCCD multiplication register.

    Takes in CCD detector along with the gain and the total elements of the EMCCD
    multiplication register.

    Parameters
    ----------
    detector : CCD
    total_gain : int
    gain_elements : int
        Amount of single stage gain elements in the EMCCD register.
    """

    if total_gain < 0 or gain_elements < 0:
        raise ValueError("Wrong input parameter")

    detector.pixel.array = multiplication_register_poisson(
        image_cube=detector.pixel.array,
        total_gain=total_gain,
        gain_elements=gain_elements,
    ).astype(float)


multiplication_register.meta = Metadata(
    name="multiplication_register",
    model_group="Charge Measurement",
    detector="CCD",
    status=None,
    model=MetadataModel(
        description="""The Electron Multiplying CCD (EMCCD) model for the :term:`CCD` detector includes
a ``multiplication_register``.
This register takes each pixel, and applies a Poisson distribution, centered around the ``total_gain``.
Each pixel is inputted and iterated through the number of ``gain_elements`` with probability of
multiplication :math:`P`:

:math:`P = {G}^(\frac{1}{N_E}) - 1`

:math:`G` is the total gain, and :math:`N_E` is the number of gain elements.

The output is a :py:class:`~pyxel.data_structure.Pixel` array, with
each pixel having gone through a multiplication register.""",
        config="""
- name: multiplication_register
  func: pyxel.models.charge_transfer.multiplication_register
  enabled: true
  arguments:
    gain_elements: 100
    total_gain: 1000
""",
    ),
)


@numba.njit
def poisson_register(lam, image_cube_pix, gain_elements):
    """Calculate the total gain of a single pixel from EMCCD register elements.

    A single pixel is
    inputted and is iterated through the total number of gain elements provided with the result being the resultant
    signal from the pixel going through the multiplication process.
    """

    new_image_cube_pix = image_cube_pix

    for _ in range(gain_elements):
        electron_gain = np.random.poisson(lam, size=int(new_image_cube_pix))
        new_image_cube_pix = np.round(image_cube_pix + np.sum(electron_gain))

    return new_image_cube_pix


@numba.njit
def multiplication_register_poisson(
    image_cube: np.ndarray,
    total_gain: int,
    gain_elements: int,
) -> np.ndarray:
    """Calculate total gain of image from EMCCD register.

    Cycles through each pixel within the image provided. Returns a final image with signal added.
    """

    new_image_cube = np.zeros_like(image_cube, dtype=np.int32)

    lam = total_gain ** (1 / gain_elements) - 1
    yshape, xshape = image_cube.shape

    for j in range(0, yshape):
        for i in range(0, xshape):
            if image_cube[j, i] < 0:
                new_image_cube[j, i] = poisson_register(
                    lam=lam, image_cube_pix=0, gain_elements=gain_elements
                )
            else:
                new_image_cube[j, i] = poisson_register(
                    lam=lam,
                    image_cube_pix=image_cube[j, i],
                    gain_elements=gain_elements,
                )

    return new_image_cube
