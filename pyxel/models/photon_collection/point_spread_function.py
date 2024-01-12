#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Model for loading PSF from file."""

from pathlib import Path
from typing import Union

import numpy as np
import xarray as xr
from astropy import units as u
from astropy.convolution import convolve_fft

from pyxel.detectors import Detector
from pyxel.inputs import load_image
from pyxel.inputs.loader import load_image_v2, load_table_v2

# from astropy.units import Quantity


def apply_psf(
    array: np.ndarray, psf: np.ndarray, normalize_kernel: bool = True
) -> np.ndarray:
    """Convolve the input array with the point spread function kernel.

    Parameters
    ----------
    array : ndarray
        Input array.
    psf : ndarray
        Convolution kernel.
    normalize_kernel : bool
        Normalize kernel.

    Returns
    -------
    ndarray
    """

    mean = np.mean(array)

    array_2d = convolve_fft(
        array,
        kernel=psf,
        boundary="fill",
        fill_value=mean,
        normalize_kernel=normalize_kernel,
    )

    return array_2d


def load_psf(
    detector: Detector, filename: Union[str, Path], normalize_kernel: bool = True
) -> None:
    """Load a point spread function from file and convolve the photon array with the PSF.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : Path or str
        Input filename of the point spread function.
    normalize_kernel : bool
        Normalize kernel.
    """
    psf = load_image(filename)

    detector.photon.array = apply_psf(
        array=detector.photon.array, psf=psf, normalize_kernel=normalize_kernel
    )


def load_wavelength_psf(
    detector: Detector,
    filename: Union[str, Path],
    wavelength_col: str,
    y_col: str,
    x_col: str,
    wavelength_table_name: str,
    normalize_kernel: bool = True,
):
    """Read psf files depending on simulation and instrument parameters.

    Parameters
    ----------
    detector : Detector
            Pyxel Detector object.
    filename : Path or str
        Input filename of the point spread function.
    wavelength_col : str
        Dimension name in the file that contains the wavelength information.
    y_col : str
        Dimension name in the file that contains the y information.
    x_col : str
        Dimension name in the file that contains the x information.
    wavelength_table_name : str
        Column name in the file that contains the wavelength information.
    normalize_kernel : bool
            Normalize kernel.
    """

    data = load_image_v2(
        filename=filename,
        data_path=0,
        rename_dims={"wavelength": wavelength_col, "y": y_col, "x": x_col},
    )

    table = load_table_v2(
        filename=filename,
        data_path=1,
        rename_cols={"wavelength": wavelength_table_name},
    )

    wavelength_da = xr.DataArray(
        # to remove facotr 100, as soon as there is data in same wavelength range available!
        table.wavelength * 100,
        dims=["wavelength"],
        coords={"wavelength": (table.wavelength * 100)},
        attrs={"units": u.nm.to_string("unicode")},
    )

    da = xr.DataArray(
        np.asarray(data, dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": wavelength_da},
    )

    interpolated_array = da.interp_like(detector.photon3d.array)

    new_array = interpolated_array.dropna(dim="wavelength", how="any")

    # detector.photon3d.array = apply_psf(
    #     array=detector.photon3d.array,
    #     psf=psf_datacube,
    #     normalize_kernel=normalize_kernel,
    # )

    # mean = detector.photon3d.array.mean(dim=["y", "x"]) # list of values.
    array_3d = convolve_fft(
        detector.photon3d.array,
        kernel=new_array.values,
        boundary="fill",
        # fill_value=mean,
        normalize_kernel=normalize_kernel,
        # allow_huge=True, # not needed anymore with reduced kernel.
    )

    psf = xr.DataArray(
        array_3d,
        dims=["wavelength", "y", "x"],
        coords={"wavelength": interpolated_array.wavelength},
    )

    # integrated = psf.integrate(coord="wavelength")

    detector.photon3d.array = psf
