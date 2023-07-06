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


def index_coords(data: np.ndarray, origin: Optional[tuple] = None):
    """Create a map of the numbered pixels from an origin selected.

    Parameters
    ----------
    data: 2-d numpy array.
        The map that you want to number.
    origin: optional, [x0, y0].
        Origin selected.
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
    coords_detector: SkyCoord, image: np.ndarray, plate_scale: float
):
    """Provide a list of the coordinates of every pixel in the detector (ra, dec).

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    plate_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    image: 2-d array.
            Image of the detector (just for the size)
    """

    n_grid_y = image.shape[0]
    n_grid_x = image.shape[1]

    data = np.zeros([n_grid_y, n_grid_x])

    xcenter = int(n_grid_x / 2)
    ycenter = int(n_grid_y / 2)

    x, y = index_coords(data, origin=(ycenter, xcenter))

    cdelt = np.array([-1.0, 1.0]) / 3600 * plate_scale
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
    wvs_all_sorted: np.array, nphoton_all_sorted: np.array, x: np.array
) -> np.array:
    """Interpolate the photons from the spectrum and the wave lengths

    Parameters
    ----------
    wvs_all_sorted: list or array.
        Wavelengths.
    nphoton_all_sorted: list or array.
        Photons of the zodiacal light.
    x: value.
        Wavelength interpolated
    """

    nphotonsky_interp = interpolate.interp1d(
        wvs_all_sorted, nphoton_all_sorted, kind="cubic"
    )
    n_photon_zodi1 = nphotonsky_interp(x)
    return n_photon_zodi1
