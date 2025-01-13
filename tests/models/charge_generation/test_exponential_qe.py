#   Copyright (c) European Space Agency, 2020.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.


import random
import re
from pathlib import Path

import numpy as np
import pytest

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.charge_generation import exponential_qe


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
        environment=Environment(
            temperature=150,
        ),
        characteristics=Characteristics(),
    )

    detector.photon.array = np.zeros(shape=(5, 5), dtype=float)

    return detector


@pytest.fixture
def ccd_5x5_noenv() -> CCD:
    """Create a valid CCD detector without temperature."""
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

    detector.photon.array = np.zeros(shape=(5, 5), dtype=float)

    return detector


@pytest.fixture
def valid_qe_csv(tmp_path: Path) -> str:
    import pandas as pd

    """Create a valid QE CSV file."""
    valid_qe = pd.DataFrame(
        {
            "wavelength": [400.0, 420.0, 440.0, 460.0, 480.0, 500.0],
            "reflectivity": [0.42, 0.52, 0.61, 0.69, 0.76, 0.82],
            "absorptivity": [1.5e-3, 1.8e-3, 2.1e-3, 2.4e-3, 2.7e-3, 3.0e-3],
        }
    )
    csv_path = tmp_path / "valid_qe.csv"
    valid_qe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def negative_qe_csv(tmp_path: Path) -> str:
    import pandas as pd

    """Create an invalid QE CSV file with out-of-range values."""
    negative_qe = pd.DataFrame(
        {
            "wavelength": [400.0, 420.0, 440.0, 460.0, 480.0, 500.0],
            "reflectivity": [0.42, 0.52, 0.61, 0.69, 0.76, 0.82],
            "absorptivity": [-1.5e-3, 1.8e-3, 2.1e-3, -2.4e-3, 2.7e-3, -3.0e-3],
        }
    )
    csv_path = tmp_path / "negative_qe.csv"
    negative_qe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def missing_qe_csv(tmp_path: Path) -> str:
    import pandas as pd

    """Create an invalid QE CSV file with missing values."""
    missing_qe = pd.DataFrame(
        {
            "wavelength": [400.0, 420.0, 440.0, 460.0, 480.0, 500.0],
            "reflectivity": [0.42, 0.52, 0.61, 0.69, 0.76, 0.82],
            # No "absorptivity" column
        }
    )
    csv_path = tmp_path / "missing_qe.csv"
    missing_qe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def nan_qe_csv(tmp_path: Path) -> str:
    import pandas as pd

    """Create a QE CSV file with NaN values in required columns."""
    nan_qe = pd.DataFrame(
        {
            "wavelength": [400.0, 420.0, 440.0, None, 480.0, 500.0],
            "reflectivity": [0.42, 0.52, None, 0.69, 0.76, 0.82],
            "absorptivity": [1.5e-3, 1.8e-3, 2.1e-3, 2.4e-3, None, 3.0e-3],
        }
    )
    csv_path = tmp_path / "nan_qe.csv"
    nan_qe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def nan_c_column_csv(tmp_path: Path) -> str:
    """Create a QE CSV file with NaN values in the 'c' column."""
    import pandas as pd

    qe_data = pd.DataFrame(
        {
            "wavelength": [400.0, 420.0, 440.0, 460.0, 480.0, 500.0],
            "reflectivity": [0.42, 0.52, 0.61, 0.69, 0.76, 0.82],
            "absorptivity": [1.5e-3, 1.8e-3, 2.1e-3, 2.4e-3, 2.7e-3, 3.0e-3],
            "c": [
                1.0e-4,
                None,
                1.2e-4,
                1.3e-4,
                1.4e-4,
                None,
            ],  # NaN values in the 'c' column
        }
    )
    csv_path = tmp_path / "nan_c_column.csv"
    qe_data.to_csv(csv_path, index=False)
    return str(csv_path)


def test_exponential_qe_negative(ccd_5x5: CCD, negative_qe_csv: str):
    """Test that exponential_qe raises an error when negative values are present in the csv file."""
    with pytest.raises(
        ValueError,
        match="Negative values found in the following columns: absorptivity. All values for 'wavelength', 'reflectivity', and 'absorptivity' must be non-negative.",
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=negative_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=450.0,
        )


def test_exponential_qe_missing(ccd_5x5: CCD, missing_qe_csv: str):
    """Test that exponential_qe raises an error when one of the required columns is missing."""
    with pytest.raises(
        ValueError,
        match="CSV file must contain the columns: reflectivity, absorptivity, wavelength",
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=missing_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=450.0,
        )


def test_exponential_qe_nan_values(ccd_5x5, nan_qe_csv):
    """Test that exponential_qe raises an error for NaN values in the CSV file."""
    with pytest.raises(
        ValueError,
        match=re.escape(
            "NaN values found in the file. All values for 'wavelength', 'reflectivity', and 'absorptivity' must be present."
        ),
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=nan_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=1.0,
            default_wavelength=450.0,
        )


def test_exponential_qe_nan_in_c_column(ccd_5x5, nan_c_column_csv):
    """Test that exponential_qe raises an error for NaN values in the 'c' column."""
    with pytest.raises(
        ValueError,
        match="NaN values found in the 'c' column. All values must be present.",
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=nan_c_column_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=1.0,
            default_wavelength=450.0,
        )


def test_exponential_qe_invalid_wavelength(ccd_5x5: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when there is no wavelength specified by the user."""
    with pytest.raises(
        ValueError,
        match="You must specify a `default_wavelength` value in nm or use 'multi' for multiple wavelengths.",
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=None,  # Invalid input
        )


def test_exponential_qe_invalid_wavelength_range(ccd_5x5: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when the provided wavelength is lower than the acceptable range."""
    detector = ccd_5x5

    # Use a wavelength outside the valid range (e.g., 200 nm or 1600 nm for a valid range of 250-1400 nm)
    invalid_wavelength = 200.0
    with pytest.raises(
        ValueError, match="Wavelength is out of the valid range for the equation."
    ):
        exponential_qe(
            detector=detector,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=invalid_wavelength,
        )


def test_exponential_qe_invalid_wavelength_range2(ccd_5x5: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when the provided wavelength is higher than the acceptable range."""
    detector = ccd_5x5

    # Check for another invalid wavelength above the upper limit
    invalid_wavelength_high = 1600.0

    with pytest.raises(
        ValueError, match="Wavelength is out of the valid range for the equation."
    ):
        exponential_qe(
            detector=detector,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=invalid_wavelength_high,
        )


# def test_exponential_qe_invalid_temperature(ccd_5x5: CCD, valid_qe_csv: str):
#     """Test that ValueError is raised when the model temperature is not matching with the environment."""
#     detector = ccd_5x5
#
#     with pytest.raises(
#         ValueError,
#         match="The temperature provided does not match with the environment.",
#     ):
#         exponential_qe(
#             detector=detector,
#             filename=valid_qe_csv,
#             x_epi=0.0002,
#             detector_type="BI",
#             temperature=280,
#             cce=0.9,
#             default_wavelength=1200.0,
#         )


def test_exponential_qe_missing_temperature(ccd_5x5_noenv: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when the temperature is not defined in the environment."""
    detector = ccd_5x5_noenv

    with pytest.raises(
        ValueError,
        match="Missing temperature information. This model cannot be used.",
    ):
        exponential_qe(
            detector=detector,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=0.9,
            default_wavelength=1200.0,
        )


def test_exponential_qe_invalid_detector_type(ccd_5x5: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when the detector type is not BI or FI."""
    detector = ccd_5x5

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid detector type. Choose 'BI' (Back-Illuminated) or 'FI' (Front-Illuminated)."
        ),
    ):
        exponential_qe(
            detector=detector,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="TI",
            cce=0.9,
            default_wavelength=1200.0,
        )


def test_exponential_qe_invalid_x_epi(ccd_5x5: CCD, valid_qe_csv: str):
    """Test that ValueError is raised when x_epi is thicker than the entire detector."""
    detector = ccd_5x5

    with pytest.raises(
        ValueError,
        match=re.escape("x_epi cannot be greater than the total detector thickness."),
    ):
        exponential_qe(
            detector=detector,
            filename=valid_qe_csv,
            x_epi=0.02,
            detector_type="BI",
            cce=0.9,
            default_wavelength=1200.0,
        )


def test_exponential_qe_random_x_epi_x_poly(ccd_5x5, valid_qe_csv):
    """Test that ValueError is raised when x_epi or x_poly values are negative."""
    # Define the two values
    values = [0.0002, -0.0002]

    # Shuffle the values randomly
    random.shuffle(values)

    # Assign the values
    x_epi, x_poly = values

    # Check if the function raises a ValueError for invalid inputs
    if x_epi < 0 or x_poly < 0:
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Epitaxial thickness (x_epi) and poly layer thickness (x_poly) must be non-negative."
            ),
        ):
            exponential_qe(
                detector=ccd_5x5,
                filename=valid_qe_csv,
                x_epi=x_epi,
                x_poly=x_poly,
                detector_type="FI",
                cce=1.0,
                default_wavelength=450.0,
            )
    else:
        # Ensure no exception for valid inputs
        exponential_qe(
            detector=ccd_5x5,
            filename=valid_qe_csv,
            x_epi=x_epi,
            x_poly=x_poly,
            detector_type="FI",
            cce=1.0,
            default_wavelength=450.0,
        )


def test_photon_array_2d_with_multi(ccd_5x5, valid_qe_csv):
    """Test that ValueError is raised when photon array is 2D but `default_wavelength` is set to 'multi'."""
    # Simulate a 2D photon array for the detector
    ccd_5x5.photon.array = np.zeros((5, 5))  # 2D array

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Photon array is 2D, but you specified 'multi' for `default_wavelength`."
        ),
    ):
        exponential_qe(
            detector=ccd_5x5,
            filename=valid_qe_csv,
            x_epi=0.0002,
            detector_type="BI",
            cce=1.0,
            default_wavelength="multi",  # Invalid for a 2D array
        )
