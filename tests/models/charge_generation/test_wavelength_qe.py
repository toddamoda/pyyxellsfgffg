#   Copyright (c) European Space Agency, 2020.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path
from typing import TYPE_CHECKING, Union

import numpy as np
import pytest
import xarray as xr

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.inputs.loader import load_table_v2
from pyxel.models.charge_generation.wavelength_qe import apply_qe_curve

if TYPE_CHECKING:
    import pandas as pd


# Fixture for creating a sample detector object
@pytest.fixture
def ccd_5x5() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=5,
            col=5,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )

    detector.photon.array_3d = xr.DataArray(
        np.zeros(shape=(6, 5, 5), dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [400.0, 420, 440, 460, 480, 500]},
    )

    return detector


@pytest.fixture
def valid_qe_dataframe(
    tmp_path: Path,
) -> str:
    """Create valid 2D file on a temporary folder."""
    valid_qe = np.array(
        [
            [4.00000e02, 4.19078e-01],
            [4.20000e02, 5.25519e-01],
            [4.40000e02, 6.16757e-01],
            [4.60000e02, 6.96008e-01],
            [4.80000e02, 7.65085e-01],
            [5.00000e02, 8.21701e-01],
        ]
    )

    final_path = f"{tmp_path}/qe.npy"
    np.save(final_path, arr=valid_qe)

    return final_path


@pytest.fixture
def invalid_qe_dataframe(
    tmp_path: Path,
) -> str:
    """Create invalid 2D file on a temporary folder."""
    invalid_qe = np.array(
        [
            [4.00000e02, 4.19078],
            [4.20000e02, 5.25519e-01],
            [4.40000e02, 6.16757e-01],
            [4.60000e02, 6.96008e-01],
            [4.80000e02, -7.65085e-01],
            [5.00000e02, 8.21701e-01],
        ]
    )

    final_path = f"{tmp_path}/qe.npy"
    np.save(final_path, arr=invalid_qe)

    return final_path


def test_conversion_with_qe_valid(ccd_5x5: CCD, valid_qe_dataframe: Union[str, Path]):
    detector = ccd_5x5

    apply_qe_curve(
        detector=detector,
        filename=valid_qe_dataframe,
        wavelength_col_name=0,
        qe_col_name=1,
    )


def test_simple_conversion_invalid(
    ccd_5x5: CCD, invalid_qe_dataframe: Union[str, Path]
):
    with pytest.raises(
        ValueError, match="Quantum efficiency values not between 0 and 1."
    ):
        apply_qe_curve(
            detector=ccd_5x5,
            filename=invalid_qe_dataframe,
            wavelength_col_name=0,
            qe_col_name=1,
        )


@pytest.fixture
def valid_qe_dataset(valid_qe_dataframe):
    valid_qe_dataframe: pd.DataFrame = load_table_v2(
        filename=valid_qe_dataframe,
        rename_cols={"wavelength": 0, "QE": 1},
        header=False,
    )
    qe_dataset: xr.Dataset = valid_qe_dataframe.set_index("wavelength").to_xarray()

    return qe_dataset


# TODO: add more tests.
# # Test for interpolate_dataset function
# def test_interpolate_dataset(ccd_5x5: CCD, valid_qe_dataset):
#     input_dataset = valid_qe_dataset
#     detector = ccd_5x5
#     input_array = detector.photon3d.array
#     # xr.DataArray(np.random.rand(15), dims=["wavelength"])
#
#     interpolate_dataset(input_dataset, input_array)
#
#     # assert isinstance(result, xr.Dataset)
#     # assert set(result.coords) == {"wavelength"}
#
#
# # Test for apply_wavelength_qe function
# def test_apply_wavelength_qe(ccd_5x5: CCD, valid_qe_dataset):
#     detector = ccd_5x5
#     result = apply_wavelength_qe(detector.photon3d.array, valid_qe_dataset["QE"])
#
#     assert isinstance(result, xr.DataArray)
#     assert result.shape == detector.photon3d.array.shape
#
#
# # Test for integrate_charge function
# def test_integrate_charge(ccd_5x5: CCD):
#     detector = ccd_5x5
#     input_array = detector.photon3d.array
#     result = integrate_charge(input_array)
#
#     assert isinstance(result, xr.DataArray)
#     assert result.shape == (detector.photon3d.array.shape[1], detector.photon3d.array.shape[2])
#
#
# # Test for load_qe_curve function
# def test_load_qe_curve(ccd_5x5: CCD, tmp_path):
#     detector = ccd_5x5
#     # Create a sample CSV file for testing
#     csv_path = tmp_path / "qe_curve.csv"
#     wavelengths = np.linspace(400, 700, 3)
#     qe_values = np.array([0.8, 0.9, 0.95])
#     import pandas as pd
#     pd.DataFrame({"wavelength": wavelengths, "QE": qe_values}).to_csv(csv_path, index=False)
#
#     load_qe_curve(detector, csv_path, "wavelength", "QE")
#
#     # Assert that charge array is added to the detector
#     assert isinstance(detector.charge.array, np.ndarray)
