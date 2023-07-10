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
"""Calculation of the zodiacal light as a function of the position and the date."""

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
from scipy.integrate import quad
from scipy.interpolate import griddata
from tqdm import tqdm

import pyxel.models.photon_collection.arrakihs_tools as tools
from gunagala.sky import ZodiacalLight
from pyxel.detectors import Detector
from pyxel.util import fit_into_array


def zod_map(
    coords_detector: SkyCoord,
    image: np.ndarray,
    pixel_scale: float,
    wave_begin: float,
    wave_end: float,
    obs_date: Time,
    method: str = "cubic",
) -> np.ndarray:
    """Create a map of the zodiacal map on the detector.

    Parameters
    ----------
    image: 2-d array
        image of the detector (just for the size)
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
        Coordinates of the pointing of the telescope.
    pixel_scale: float (in arcsec/pixel).
        Pixel scale of the telescope.
    wave_begin: value.
        Lower limit of wavelength the detector.
    wave_end: value.
        Upper limit of wavelength the detector.
    obs_date: Time object: scale='utc' format='iso'.
            Time of the observation.
    method: string (optional).
        interpolation method: 'linear', 'nearest', 'cubic'. Default values: 'cubic'.

    Returns
    -------
    np.ndarray
        A zodiacal light map in ph/s/cm2.

    """
    # we increase the size of the image to avoid border effects
    image_ampl = np.zeros([image.shape[0] + 500, image.shape[1] + 500])
    list_detector = tools.detector_coordinates(
        coords_detector=coords_detector, image=image_ampl, pixel_scale=pixel_scale
    )

    # we reduce the size of the image and the pixel scale to decrease the computational time
    image_reduced = np.zeros(
        [int((image_ampl.shape[0]) / 100), int((image_ampl.shape[1]) / 100)]
    )
    pixel_scale_reduced = pixel_scale * 100

    list_detector_reduced = tools.detector_coordinates(
        coords_detector=coords_detector,
        image=image_reduced,
        pixel_scale=pixel_scale_reduced,
    )

    zod = ZodiacalLight()  # Object that creates the zodiacal light
    zod_relat = np.zeros(
        [list_detector_reduced.shape[0], list_detector_reduced.shape[1]]
    )
    for i in tqdm(range(list_detector_reduced.shape[0])):
        for j in range(list_detector_reduced.shape[1]):
            zod_relat[i][j] = zod.relative_brightness(
                list_detector_reduced[i][j], obs_date
            )

    function_zod = zod.surface_brightness()

    wvs = np.array([0.28, 0.3, 0.36, 0.44, 0.55, 0.7, 0.9, 1.25, 1.5, 2, 2.5]) * 10000
    phot = function_zod(wvs * u.AA).to(
        u.photon / (u.s * u.AA * u.arcsec**2 * u.cm**2)
    )  # units [photons/s/cm^2/arcsec^2/AA^-1]

    wv_beg = wave_begin * 10  # from nm to um
    wv_end = wave_end * 10

    n_photon_sky_tot, err_n_photon_sky_tot = quad(
        lambda x: tools.num_photon_sky(wvs, phot, x), wv_beg, wv_end
    )  # units [photons/s/cm^2/arcsec^2]

    zod_light_image = n_photon_sky_tot * zod_relat

    points = np.array(
        [
            list_detector_reduced.ra.deg.flatten(),
            list_detector_reduced.dec.deg.flatten(),
        ]
    ).transpose()
    values = zod_light_image.flatten()

    new_grid = (list_detector.ra.deg, list_detector.dec.deg)

    if method == "linear":
        grid = griddata(points, values, new_grid, method="linear")
    elif method == "nearest":
        grid = griddata(points, values, new_grid, method="nearest")
    elif method == "cubic":
        grid = griddata(points, values, new_grid, method="cubic")
    else:
        raise NotImplementedError

    zodi_light_flux = grid * pixel_scale**2  # units [photons/s/cm^2]

    return zodi_light_flux


def zodiacal_light(
    detector: Detector,
    coords_detector: dict,
    pixel_scale: float,
    aperture: float,
    wave_begin: float,
    wave_end: float,
    obs_date: dict,
    method: str = "cubic",
) -> None:
    """Calculate the Zodiacal light in the detector.

    Parameters
    ----------
    detector:
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
        Coordinates of the pointing of the telescope.
    pixel_scale: float (in arcsec/pixel).
        Pixel scale of the telescope.
    aperture: float (in m).
        Aperture of the telescope.
    wave_begin: value.
        Lower limit of wavelength the detector.
    wave_end: value.
        Upper limit of wavelength the detector.
    obs_date: Time object: scale='utc' format='iso'.
        Time of the observation.
    method: string (optional).
        Interpolation method: 'linear', 'nearest', 'cubic'. Default values: 'cubic'.
    """

    zodi: np.ndarray = zod_map(
        coords_detector=SkyCoord(**coords_detector),
        image=detector.photon.array,
        pixel_scale=pixel_scale,
        wave_begin=wave_begin,
        wave_end=wave_end,
        obs_date=Time(**obs_date),
        method=method,
    )

    zodi_cropped = fit_into_array(
        array=zodi, output_shape=detector.photon.shape, align="center"
    )

    converted_photon = tools.flux2phot(
        flux=zodi_cropped, t_exp=detector.absolute_time, aperture=aperture
    )
    detector.photon.array += converted_photon
