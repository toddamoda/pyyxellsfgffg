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
"""Convertion from photons/s/cm2/pixel to photons/pixel."""

import numpy as np

from pyxel.detectors import Detector


def flux2phot(scene: np.ndarray, t_exp: float, aperture: float) -> np.ndarray:
    """Convert flux (phontons/s/cm2) to photon units

    Parameters
    ----------
    scene
    t_exp
    aperture

    Returns
    -------
    """
    col_area = np.pi * (aperture / 2) ** 2
    scene_photons = scene * t_exp * col_area
    return scene_photons


def flux_convert(detector: Detector, aperture: float) -> np.ndarray:
    """Convert flux (phontons/s/cm2) to photon units

    Parameters
    ----------
    aperture

    Returns
    -------
    """
    scene = detector.data["/scene"]

    print(f"{detector.time=}, {detector.absolute_time}")
    scene_photons = flux2phot(scene=scene, t_exp=detector.time, aperture=aperture)
    detector.photon.array = np.asarray(scene_photons)
