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
"""Tools to calculate coordinates of each pixel."""
from typing import Optional

import numpy as np
from astropy import wcs
from astropy.coordinates import SkyCoord
from scipy import interpolate
from scipy.interpolate import griddata


def flux2phot(flux: np.ndarray, t_exp: float, aperture: float) -> np.ndarray:
    """Convert flux (photon/s/cm2) to photon/s/pixel.

    Parameters
    ----------
    flux : np.ndarray
        Scene object. Unit: photon/pixel/s/cm2.
    t_exp : float
        Exposure time. Unit: s.
    aperture : float
        Collecting area of the telescope. Unit: m.

    Returns
    -------
    np.ndarray
        Converted flux in photon/s/pixel.
    """

    col_area = np.pi * (aperture * 1e2 / 2) ** 2
    flux_converted = flux * t_exp * col_area

    return flux_converted


def index_coords(data: np.ndarray, origin: Optional[tuple] = None):
    """Create a map of the numbered pixels from an origin selected.

    Parameters
    ----------
    data: 2-d numpy array.
        The map that you want to number.
    origin: optional, [x0, y0].
        Origin selected.

    Returns
    -------
    tuple(np.ndarray,np.ndarray)
        Y and X pixel indexes.
    """

    ny, nx = data.shape[:2]
    if origin is None:
        origin_x, origin_y = nx // 2, ny // 2
    else:
        origin_y, origin_x = origin
        if origin_y < 0:
            origin_y += ny
        if origin_x < 0:
            origin_x += nx

    x, y = np.meshgrid(np.arange(float(nx)) - origin_x, origin_y - np.arange(float(ny)))
    return x, y


def detector_coordinates(
    coords_detector: SkyCoord, image: np.ndarray, pixel_scale: float
):
    """Provide a list of the coordinates of every pixel in the detector (ra, dec).

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    image: 2-d array.
            Image of the detector (just for the size)

    Returns
    -------
    np.ndarray(SkyCoord)
        Coordinates of the detector pixels.
    """

    n_grid_y = image.shape[0]
    n_grid_x = image.shape[1]

    data = np.zeros([n_grid_y, n_grid_x])

    xcenter = int(n_grid_x / 2)
    ycenter = int(n_grid_y / 2)

    x, y = index_coords(data, origin=(ycenter, xcenter))

    cdelt = np.array([-1.0, 1.0]) / 3600 * pixel_scale
    crpix = np.array([image.shape[0] / 2, image.shape[1] / 2])

    w = wcs.WCS(naxis=2)
    pa = 0

    w.wcs.crpix = crpix
    w.wcs.crval = [coords_detector.ra.deg, coords_detector.dec.deg]
    w.wcs.cdelt = cdelt
    w.wcs.crota = [0, -pa]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    rac_det, dec_det = w.all_pix2world(y, x, 1)

    list_detector = SkyCoord(ra=rac_det, dec=dec_det, unit="deg", frame="icrs")

    return list_detector


def num_photon_sky(
    wvs_all_sorted: np.ndarray, nphoton_all_sorted: np.ndarray, x: np.ndarray
) -> np.ndarray:
    """Interpolate the photons from the spectrum and the wavelengths.

    Parameters
    ----------
    wvs_all_sorted: list or array.
        Wavelengths.
    nphoton_all_sorted: list or array.
        Photons of the zodiacal light.
    x: value.
        Wavelength interpolated

    Returns
    -------
    np.array
        Interpolated value.
    """

    nphotonsky_interp = interpolate.interp1d(
        wvs_all_sorted, nphoton_all_sorted, kind="cubic"
    )
    n_photon_zodi1 = nphotonsky_interp(x)
    return n_photon_zodi1


def detector_interpolation(
    coords: SkyCoord,
    image_reduced: np.ndarray,
    pixel_scale_reduced: float,
    image: np.ndarray,
    pixel_scale: float,
    fluxes: np.ndarray,
):
    """Interpolate the values from a detector of larger pixels and lower number of pixels to the original image.

    Parameters
    ----------
    coords: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    image_reduced:: np.ndarray
            Image of the reduced image size.
    pixel_scale_reduced: float (in arcsec/pixel).
            Reduced plate scale of the telescope used.
    image: np.ndarray
            Image of the original image size to be interpolated.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope used.
    fluxes: np.ndarray
            Values to be integrated.

    Returns
    -------
    np.ndarray
        Interpolated values on the original detector.
    """
    list_detector_reduced = detector_coordinates(
        coords, image_reduced, pixel_scale_reduced
    )
    list_detector = detector_coordinates(coords, image, pixel_scale)

    points = np.array(
        [
            list_detector_reduced.ra.deg.flatten(),
            list_detector_reduced.dec.deg.flatten(),
        ]
    ).transpose()
    values = fluxes.flatten()

    new_grid = (list_detector.ra.deg, list_detector.dec.deg)
    grid = griddata(points, values, new_grid, method="linear")

    return grid


def mask_circle_in(
    image: np.ndarray, center: Optional[tuple] = None, radius: Optional[float] = None
) -> np.ndarray:
    """Mask an input image to the FOV of the telescope.

    Parameters
    ----------
    image: np.ndarray
            Image of the original image size to be interpolated.
    center: tuple.
            Center to mask the image.
    radius: float
            Radius to mask the image.

    Returns
    -------
    np.ndarray
        Masked image.
    """
    h, w = len(image), len(image)
    if center is None:  # use the middle of the image
        center = (int(w / 2), int(h / 2))
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w - center[0], h - center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    mask = dist_from_center <= radius

    masked_img = image.copy()
    masked_img = masked_img.astype("float")
    masked_img[~mask] = np.nan

    return masked_img
