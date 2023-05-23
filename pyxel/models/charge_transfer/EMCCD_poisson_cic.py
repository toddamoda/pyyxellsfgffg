#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model for replicating the gain register in an EMCCD, including clock-induced-charge."""

import numba
import numpy as np

from pyxel.detectors import CCD

def multiplication_register(
    detector: CCD,
    total_gain: int,
    gain_elements: int,
    pCIC_rate: float,
    sCIC_rate: float
) -> None:
    """Calculate total gain of image with EMCCD multiplication register.

    Takes in CCD detector along with the gain and the total elements of the EMCCD
    multiplication register.
    """

    if total_gain < 0 or gain_elements < 0:
        raise ValueError("Wrong input parameter")

    detector.pixel.array = multiplication_register_poisson(
        image_cube=detector.pixel.array,
        total_gain=total_gain,
        gain_elements=gain_elements,
        pCIC_rate=pCIC_rate,
        sCIC_rate=sCIC_rate
    ).astype(float)



@numba.njit
def poisson_register(lam, new_image_cube_pix, gain_elements, sCIC_rate):
    """Calculate the total gain of a single pixel from EMCCD register elements.

    A single pixel is inputted and is iterated through the total number of gain
    elements provided with the result being the resultant signal from the pixel
    going through the multiplication process.
    
    Each register step is considered individual. Each electron entering a register
    stage has probability cause electron avalance with a Poisson rate lambda. Each
    stage has possibilty to introduce a serial CIC event. Serial CIC is assumed to
    be Poisson distributed.
    """

    new_image_cube_pix = new_image_cube_pix
        
    for _ in range(gain_elements):
        # Add possibilty for a CIC event at each register stage
        new_image_cube_pix += np.random.poisson( sCIC_rate )
    
        # Each electron increase has chance for impact ionization, so one needs
        # to loop over all electrons at each gain stage.
        gain_electrons = 0
        for _ in range( np.floor(new_image_cube_pix) ):
            gain_electrons += np.random.poisson(lam)
        new_image_cube_pix += gain_electrons

    return new_image_cube_pix


@numba.njit(parallel=True)
def multiplication_register_poisson(
    image_cube: np.ndarray,
    total_gain: int,
    gain_elements: int,
    pCIC_rate: float,
    sCIC_rate: float
) -> np.ndarray:
    """Calculate total gain of image from EMCCD register.

    Cycles through each pixel within the image provided. Returns a final image with signal added.
    """

    new_image_cube = np.zeros_like(image_cube, dtype=np.int32)
    
    # Generate and add pCIC to the frame
    pCIC = np.random.poisson( pCIC_rate, image_cube.shape )
    new_image_cube += pCIC

    lam = total_gain ** (1 / gain_elements) - 1
    yshape, xshape = image_cube.shape

    for j in numba.prange(0, yshape):
        for i in numba.prange(0, xshape):
            new_image_cube[j, i] = poisson_register(
                lam=lam,
                new_image_cube_pix=image_cube[j, i],
                gain_elements=gain_elements,
                sCIC_rate=sCIC_rate
            )

    return new_image_cube
