#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Simple model to convert photon into photo-electrons using QE(-map) inside detector."""

from pathlib import Path
from typing import TYPE_CHECKING, Union

import xarray as xr

from pyxel.detectors import Detector
from pyxel.inputs.loader import load_table_v2

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

# from pyxel.models.charge_generation.photoelectrons import apply_qe


def interpolate_dataset(
    input_dataset: xr.Dataset,
    input_array: xr.DataArray,
) -> xr.Dataset:
    """Interpolate xr.Dataset to the resolution of xr.DataArray.

    Parameters
    ----------
    input_dataset : xr.Dataset
        Input dataset to interpolate.
    input_array : xr.DataArray
        Input array on which the dataset is interpolated to.

    Returns
    -------
    xr.Dataset
    """
    interpolated_ds = input_dataset.interp_like(input_array)

    return interpolated_ds


def apply_wavelength_qe(
    photon_array: xr.DataArray,
    qe_array: xr.DataArray
    # binomial_sampling = False,
    # TODO: add option for binominal_sampling. See pyxel.models.charge_generation.photoelectrons.apply_qe()
) -> xr.DataArray:
    """Apply wavelength dependent QE to photon array to convert to charge array.

    Parameters
    ----------
    photon_array : xr.DataArray
    qe_array : xr.DataArray

    Returns
    -------
    xr.DataArray
    """

    charge_array = photon_array * qe_array

    return charge_array


def integrate_charge(input_array: xr.DataArray) -> xr.DataArray:
    """Convert 3D charge to 2D charge with integration along coordinate wavelength.

    Parameters
    ----------
    input_array: xr.DataArray
        Input 3D charge array with dimensions wavelength, y, x.

    Returns
    -------
    xr.DataArray
    """
    integrated_charge = input_array.integrate(coord="wavelength")

    return integrated_charge.data


def load_qe_curve(
    detector: Detector,
    filename: Union[str, Path],
    wavelength_col_name: str,
    qe_col_name: str,
) -> None:
    """Apply wavelength dependent QE with loading a file.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        CSV File path.
    wavelength_col_name : str
        Column name of wavelength in loaded file.
    qe_col_name : str
        Column name of quantum efficiency in loaded file.
    """

    df: pd.DataFrame = load_table_v2(
        filename=filename,
        rename_cols={wavelength_col_name: "wavelength", qe_col_name: "QE"},
        header=True,
    )

    qe_curve_ds: xr.Dataset = df.set_index("wavelength").to_xarray()

    # interpolate the qe_curve wavelength data to the resolution of the photon3D data.
    qe_interpolated: xr.Dataset = interpolate_dataset(
        input_dataset=qe_curve_ds,
        input_array=detector.photon3d.array,
    )

    if not 0 <= qe_interpolated["QE"].any() <= 1:
        raise ValueError("Quantum efficiency not between 0 and 1.")

    # apply QE
    detector_charge: xr.DataArray = apply_wavelength_qe(
        photon_array=detector.photon3d.array,
        qe_array=qe_interpolated["QE"],
    )

    # integrate charge along coordinate wavelength
    integrated_charge: xr.DataArray = integrate_charge(input_array=detector_charge)

    # get data from xr.DataArray
    new_charge: np.ndarray = integrated_charge.data

    detector.charge.add_charge_array(new_charge)
