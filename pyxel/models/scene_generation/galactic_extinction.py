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
"""Calculates the galactic extinction based on Cardelli et al. (1989) and Planck Collab., 2016."""

import dustmaps.planck
import numpy as np
from astropy.coordinates import SkyCoord
from dustmaps.planck import PlanckGNILCQuery

import pyxel.models.scene_generation.arrakihs_tools as tools
from pyxel.detectors import Detector


def cardelli_IR(x: float, R_v: float = 3.1) -> float:
    """Cardelli's function in the IR (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float (in 1/nm by default).
       1/wavelength value
    R_v: float, optional. (Default: 3.1).
       R_v = A_v/E(B-V) from reddening law
    """
    a = 0.574 * x**1.61
    b = -0.527 * x**1.61
    return a + b / R_v


def cardelli_opt(x: float, R_v: float = 3.1) -> float:
    """Cardelli's function in the optical (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float (in 1/nm by default).
       1/wavelength value
    R_v: float, optional. (Default: 3.1).
       R_v = A_v/E(B-V) from reddening law
    """
    y = x - 1.82
    a = (
        1
        + 0.17699 * y
        - 0.50447 * y**2
        - 0.02427 * y**3
        + 0.72085 * y**4
        + 0.01979 * y**5
        - 0.77530 * y**6
        + 0.32999 * y**7
    )
    b = (
        1.41338 * y
        + 2.28305 * y**2
        + 1.07233 * y**3
        - 5.38434 * y**4
        - 0.62251 * y**5
        + 5.30260 * y**6
        - 2.09002 * y**7
    )
    return a + b / R_v


def cardelli_UV_1(x: float, R_v: float = 3.1) -> float:
    """Cardelli's function in the UV (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float (in 1/nm by default).
       1/wavelength value
    R_v: float, optional. (Default: 3.1).
       R_v = A_v/E(B-V) from reddening law
    """
    a = 1.752 - 0.316 * x - 0.104 / ((x - 4.67) ** 2 + 0.341)
    b = -3.090 + 1.825 * x + 1.206 / ((x - 4.62) ** 2 + 0.263)
    return a + b / R_v


def cardelli_UV_2(x: float, R_v: float = 3.1) -> float:
    """Cardelli's function in the UV (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float (in 1/nm by default).
       1/wavelength value
    R_v: float, optional. (Default: 3.1).
       R_v = A_v/E(B-V) from reddening law
    """
    Fa = -0.04473 * (x - 5.9) ** 2 - 0.009779 * (x - 5.9) ** 3
    Fb = 0.2130 * (x - 5.9) ** 2 + 0.1207 * (x - 5.9) ** 3

    a = 1.752 - 0.316 * x - 0.104 / ((x - 4.67) ** 2 + 0.341) + Fa
    b = -3.090 + 1.825 * x + 1.206 / ((x - 4.62) ** 2 + 0.263) + Fb
    return a + b / R_v


def cardelli_far_UV(x: float, R_v: float = 3.1) -> float:
    """Cardelli's function in the far UV (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float (in 1/nm by default).
       1/wavelength value
    R_v: float, optional. (Default: 3.1).
       R_v = A_v/E(B-V) from reddening law
    """
    a = -1.073 - 0.628 * (x - 8) + 0.137 * (x - 8) ** 2 - 0.070 * (x - 8) ** 3
    b = 13.670 + 4.257 * (x - 8) - 0.420 * (x - 8) ** 2 + 0.374 * (x - 8) ** 3
    return a + b / R_v


def cardelli(x: float, R_v: float = 3.1) -> float:
    """Cardelli function (Cardelli et al., 1989).

    Parameters
    ----------
    x: 1/lambda, float.
        Inverse wavelength.
    R_v: float, optional. (Default: 3.1).
        R_v = A_v/E(B-V) from reddening law
    """

    return np.piecewise(
        x,
        [
            (x < 1.1),
            (x >= 1.1) & (x < 3.3),
            (x >= 3.3) & (x < 5.9),
            (x >= 5.9) & (x < 8),
            (x >= 8),
        ],
        [
            lambda x: cardelli_IR(x, R_v),
            lambda x: cardelli_opt(x, R_v),
            lambda x: cardelli_UV_1(x, R_v),
            lambda x: cardelli_UV_2(x, R_v),
            lambda x: cardelli_far_UV(x, R_v),
        ],
    )


def extintion_cardelli(wave: float, A_v: float, R_v: float = 3.1, units="nm"):
    """Application of Cardelli's extinction at a given wavelength (Cardelli et al., 1989).

    Parameters
    ----------
     wave: lambda, float (in nm by default).
        Wavelength value
     A_v: float (in magnitudes).
        Extinction at V band.
     R_v: float, optional. (Default: 3.1).
        R_v = A_v/E(B-V) from reddening law
    """
    if units == "nm":
        wave_num = wave * 1e-3
    if units == "microns":
        wave_num = wave

    x = 1 / wave_num
    return A_v * cardelli(x, R_v)


def extinction_map(
    coords_detector: SkyCoord, image, plate_scale, central_wv
) -> np.ndarray:
    """Calculate of the extinction map on the detector (pixel-to-pixel) using Planck Collab. 2016.

    Parameters
    ----------
     coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
         Coordinates of the pointing of the telescope.
     image: 2-d array.
         Image example to take the characteristics from.
     plate_scale: float (in arcsec/pixel).
         Plate scale of the telescope used.
     central_wv: float, optional.
         Wavelength at the center of the filter.
    """
    dustmaps.planck.fetch(which="GNILC")

    planckGNIL = PlanckGNILCQuery()
    list_detector = tools.detector_coordinates(
        coords_detector=coords_detector, image=image, plate_scale=plate_scale
    )
    ebv = planckGNIL(list_detector)
    R_v = 3.1
    avrg_ext = R_v * ebv
    wave = np.array([central_wv])
    ext = extintion_cardelli(wave, avrg_ext, R_v, units="nm")
    percent_pass = 10.0 ** (-ext / 2.5)

    return percent_pass


def load_extinction(
    detector: Detector, coords_detector: dict, plate_scale:float, central_wv:float
) -> None:
    extinction: np.ndarray = extinction_map(
        coords_detector=SkyCoord(**coords_detector),
        image=np.asarray(detector.data["/scene"]),
        plate_scale=plate_scale,
        central_wv=central_wv,
    )

    detector.data["/scene"] = detector.data["/scene"] * extinction
