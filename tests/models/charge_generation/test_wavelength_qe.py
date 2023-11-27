#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path
from typing import Union

import numpy as np
import pytest
import xarray as xr

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.charge_generation.wavelength_qe import (  # interpolate_dataset,; apply_wavelength_qe,; integrate_charge,
    load_qe_curve,
)


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
    return detector


@pytest.fixture
def valid_qe_dataset(
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
def invalid_qe_dataset(
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


def test_conversion_with_qe_valid(ccd_5x5: CCD, valid_qe_dataset: Union[str, Path]):
    detector = ccd_5x5

    load_qe_curve(
        detector=detector,
        filename=valid_qe_dataset,
        wavelength_col_name=0,
        qe_col_name=1,
    )


def test_simple_conversion_invalid(ccd_5x5: CCD, invalid_qe_dataset: Union[str, Path]):
    with pytest.raises(
        ValueError, match="Quantum efficiency values not between 0 and 1."
    ):
        load_qe_curve(
            detector=ccd_5x5,
            filename=invalid_qe_dataset,
            wavelength_col_name=0,
            qe_col_name=1,
        )


# # Fixture for creating a sample detector object
# @pytest.fixture
# def sample_detector():
#     # Replace with actual detector parameters
#     return Detector(photon3d=xr.DataArray(np.random.rand(3, 100, 100), dims=["wavelength", "y", "x"]))


# Fixture for creating a sample wavelength-QE dataset
@pytest.fixture
def sample_qe_dataset():
    # Replace with actual QE dataset parameters
    wavelengths = np.linspace(400, 700, 3)
    qe_values = np.array([0.8, 0.9, 0.95])
    return xr.Dataset(
        {"QE": ("wavelength", qe_values)}, coords={"wavelength": wavelengths}
    )


# # Test for interpolate_dataset function
# def test_interpolate_dataset():
#     input_dataset = xr.Dataset({"data": ("wavelength", np.random.rand(3))})
#     input_array = xr.DataArray(np.random.rand(5), dims=["wavelength"])
#
#     result = interpolate_dataset(input_dataset, input_array)
#
#     assert isinstance(result, xr.Dataset)
#     assert set(result.coords) == {"wavelength"}
#
#
# # Test for apply_wavelength_qe function
# def test_apply_wavelength_qe(sample_detector, sample_qe_dataset):
#     result = apply_wavelength_qe(sample_detector.photon3d.array, sample_qe_dataset["QE"])
#
#     assert isinstance(result, xr.DataArray)
#     assert result.shape == sample_detector.photon3d.array.shape
#
#
# # Test for integrate_charge function
# def test_integrate_charge(sample_detector):
#     input_array = sample_detector.photon3d.array
#     result = integrate_charge(input_array)
#
#     assert isinstance(result, np.ndarray)
#     assert result.shape == (sample_detector.photon3d.array.shape[1], sample_detector.photon3d.array.shape[2])
#
#
# # Test for load_qe_curve function
# def test_load_qe_curve(ccd_5x5, tmp_path):
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
#     assert "charge" in detector.__dict__
#     assert isinstance(detector.charge.array, np.ndarray)
