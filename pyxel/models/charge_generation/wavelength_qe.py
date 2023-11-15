#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Simple model to convert photon into photo-electrons inside detector."""

from pathlib import Path
from typing import TYPE_CHECKING, Union

from pyxel.detectors import Detector
from pyxel.inputs.loader import load_dataarray
from pyxel.models.charge_generation.photoelectrons import apply_qe

if TYPE_CHECKING:
    import xarray as xr

# def apply_wavelength_qe(
#     filename: Union[str, Path],
#     wavelength_col_name: str,
#     qe_col_name: str,
# ) -> xr.DataArray:
#
#     # load QE curve data
#     qe_curve: xr.DataArray = load_dataarray(filename=filename)
#
#     # rename column to wavelength and turn into xr.Dataset
#     qe_curve_ds = qe_curve.rename(
#         columns={wavelength_col_name: "wavelength", qe_col_name: "QE"}
#     ).to_xarray()
#
#     # interpolate the qe_curve wavelength data to the resolution of the photon3D data.
#     qe_interpolated = qe_curve_ds.interp_like(detector.photon3d.array)
#
#     detector_charge = apply_qe(
#         array=detector.photon3d.array,
#         qe=qe_interpolated["QE"],
#         binomial_sampling=False,
#     )
#     # TODO: add option for binominal_sampling.
#
#     # integrate charge along coordinate wavelength
#     integrated_charge: xr.DataArray = detector_charge.integrate(coord="wavelength")


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
        File path.
    wavelength_col_name : str
        Column name of wavelength in loaded file.
    qe_col_name : str
        Column name of quantum efficiency in loaded file.
    """

    # load QE curve data
    qe_curve: xr.DataArray = load_dataarray(filename=filename)

    # rename column to wavelength and turn into xr.Dataset
    qe_curve_ds = qe_curve.rename(
        columns={wavelength_col_name: "wavelength", qe_col_name: "QE"}
    ).to_xarray()

    # interpolate the qe_curve wavelength data to the resolution of the photon3D data.
    qe_interpolated = qe_curve_ds.interp_like(detector.photon3d.array)

    detector_charge = apply_qe(
        array=detector.photon3d.array,
        qe=qe_interpolated["QE"],
        binomial_sampling=False,
    )
    # TODO: add option for binominal_sampling.

    # integrate charge along coordinate wavelength
    integrated_charge: xr.DataArray = detector_charge.integrate(coord="wavelength")

    detector.charge.array = integrated_charge.values
