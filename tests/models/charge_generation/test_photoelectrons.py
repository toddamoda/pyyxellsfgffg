#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    WavelengthHandling,
)
from pyxel.models.charge_generation import conversion_with_qe_map, simple_conversion
from pyxel.models.charge_generation.photoelectrons import apply_qe, integrate_photon


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
def ccd_5x5x5() -> CCD:
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
            wavelength=WavelengthHandling(cut_on=450.0, cut_off=490.0, resolution=10)
        ),
        characteristics=Characteristics(),
    )

    return detector


@pytest.fixture
def ccd_2d(ccd_5x5: CCD):
    ccd_5x5.photon.array_2d = np.zeros(ccd_5x5.geometry.shape, dtype=float)
    return ccd_5x5


@pytest.fixture
def ccd_3d(ccd_5x5x5: CCD):
    wavelengths = ccd_5x5x5.environment.wavelength.get_wavelengths()
    wavelengths_dim = len(wavelengths)
    num_rows, num_cols = ccd_5x5x5.geometry.shape

    ccd_5x5x5.photon.array_3d = xr.DataArray(
        np.zeros((wavelengths_dim, num_rows, num_cols), dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": wavelengths},
    )
    return ccd_5x5x5


def test_integrate_photon(ccd_3d):
    """Test for integrate_photon function."""
    input_array = ccd_3d.photon.array_3d
    result = integrate_photon(input_array).to_numpy()

    assert isinstance(result, np.ndarray)
    assert result.shape == (input_array.shape[1], input_array.shape[2])


def test_apply_qe():
    """Test for apply_qe function."""

    input_array = np.random.rand(10, 10)
    qe_value = 0.8
    result = apply_qe(input_array, qe_value)

    assert isinstance(result, np.ndarray)
    assert result.shape == input_array.shape


def test_simple_conversion(ccd_2d):
    """Test for simple_conversion function."""
    quantum_efficiency = 0.8
    seed = 42
    binomial_sampling = False

    simple_conversion(ccd_2d, quantum_efficiency, seed, binomial_sampling)

    assert isinstance(ccd_2d.charge.array, np.ndarray)


@pytest.fixture
def valid_qe_map_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file on a temporary folder."""
    data_2d = (
        np.array(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        * 0.5
    )

    final_path = f"{tmp_path}/qe.npy"
    np.save(final_path, arr=data_2d)

    return final_path


@pytest.fixture
def invalid_qe_map_path(
    tmp_path: Path,
) -> str:
    """Create invalid 2D file on a temporary folder."""

    data_2d = np.array(
        [
            [1.0, 1.0, 0.5, 1.0, 1.0],
            [1.0, 2.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0, 2.0, 1.0],
            [0.5, 1.0, 1.0, 1.0, 1.0],
        ]
    )

    final_path = f"{tmp_path}/qe.npy"
    np.save(final_path, arr=data_2d)

    return final_path


@pytest.mark.parametrize(
    "qe",
    [
        pytest.param(0.5, id="valid"),
        pytest.param(None, id="valid_none"),
    ],
)
def test_simple_conversion_photon_2d(ccd_5x5: CCD, qe: float):
    """Test model 'simple_conversion' with a 2D photon input."""
    detector = ccd_5x5
    detector.characteristics.quantum_efficiency = 0.5

    array = np.ones((5, 5))
    detector.photon.array = array
    target = array * 0.5

    simple_conversion(detector=detector, quantum_efficiency=qe, binomial_sampling=False)

    np.testing.assert_array_almost_equal(detector.charge.array, target)


def test_simple_conversion_photon_3d(ccd_5x5: CCD):
    """Test model 'simple_conversion' with a 3D photon input."""
    detector = ccd_5x5
    detector.photon.array_3d = xr.DataArray(
        np.zeros(shape=(6, 5, 5), dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [400.0, 420, 440, 460, 480, 500]},
    )

    simple_conversion(detector=detector, quantum_efficiency=0.8)


def test_simple_conversion_no_photon(ccd_5x5: CCD):
    """Test model 'simple_conversion' with no photons."""
    detector = ccd_5x5

    with pytest.raises(ValueError, match="container is not initialized"):
        simple_conversion(detector=detector, quantum_efficiency=0.8)


@pytest.mark.parametrize(
    "qe, exp_exc, exp_error",
    [
        pytest.param(1.5, ValueError, "Quantum efficiency not between 0 and 1."),
        pytest.param(None, ValueError, "Quantum efficiency is not defined."),
    ],
)
def test_simple_conversion_invalid_qe(
    ccd_5x5: CCD,
    qe: float,
    exp_exc,
    exp_error,
):
    with pytest.raises(exp_exc, match=exp_error):
        simple_conversion(detector=ccd_5x5, quantum_efficiency=qe)


def test_conversion_with_qe_valid(ccd_2d: CCD, valid_qe_map_path: str | Path):
    detector = ccd_2d

    conversion_with_qe_map(detector=detector, filename=valid_qe_map_path)


def test_convertsion_with_qe_invalid(ccd_5x5: CCD, invalid_qe_map_path: str | Path):
    with pytest.raises(
        ValueError, match="Quantum efficiency values not between 0 and 1."
    ):
        conversion_with_qe_map(detector=ccd_5x5, filename=invalid_qe_map_path)
