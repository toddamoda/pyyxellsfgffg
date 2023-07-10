# Copyright (c) 2023 Alejandro Camazon Pinilla, University of Florida, ARRAKIHS Mission Consortium
#
# acamazon@ufl.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Load a Cosmological background selected."""


from pathlib import Path
from typing import Union

import pyxel.models.photon_collection.arrakihs_tools as tools
from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image


def load_cosmo_bckg(
    detector: Detector, filename: Union[str, Path], aperture: float
) -> None:
    """Load the cosmological background selected.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : Path or str
        Input filename of the cosmological background.
    aperture : float
        Telescope aperture in m.

    Returns
    -------
    np.ndarray
        Cosmological Background flux in photon/s/pixel.
    """
    cosmo_bckg = load_cropped_and_aligned_image(
        shape=detector.geometry.shape, filename=filename, align="center"
    )

    converted_photon = tools.flux2phot(
        flux=cosmo_bckg, t_exp=detector.absolute_time, aperture=aperture
    )
    detector.photon.array += converted_photon
