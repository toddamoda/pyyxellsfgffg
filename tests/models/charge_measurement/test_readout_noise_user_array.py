#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
from pathlib import Path

from pyxel.detectors import CMOS
from pyxel.detectors.apd import AvalancheSettings, ConverterFunction, ConverterValues
from pyxel.detectors.channels import Matrix, ReadoutPosition
from pyxel.models.charge_measurement import (
    readout_noise_user_array,
    output_node_noise_cmos_user_array
)

@pytest.fixture
def valid_noise_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file in a temporary folder."""
    data_2d = np.array(
        [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ]
    )

    final_path = f"{tmp_path}/readout_noise.npy"
    np.save(final_path, arr=data_2d)

    return final_path

@pytest.fixture
def invalid_noise_path(
    tmp_path: Path,
) -> str:
    """Return bogus filename."""
   
    return "invalid_path.npy"

def test_readout_noise_user_array(cmos_2x3: CMOS, valid_noise_path: str):
    """Test 'readout_noise_user_array' with a 2x3 'CMOS' and a valid noise file"""

    cmos_2x3.signal.array = np.ones((cmos_2x3.geometry.row, cmos_2x3.geometry.col))

    # This is the predictable signal array modified by the noise array that we would expect
    exp_signal = np.array([
        [2.0, 3.0, 4.0],
        [5.0, 6.0, 7.0]
    ])

    # Test func
    readout_noise_user_array(
        detector=cmos_2x3,
        filename=valid_noise_path
    )

    assert (cmos_2x3.signal.array == exp_signal).all()

@pytest.fixture
def valid_ones_path_2x3(
    tmp_path: Path,
) -> str:
    """Create valid 2D file in a temporary folder."""
    data_2d = np.ones((2,3))

    final_path = f"{tmp_path}/readout_noise_2x3.npy"
    np.save(final_path, arr=data_2d)

    return final_path
@pytest.fixture
def valid_ones_path_3x3(
    tmp_path: Path,
) -> str:
    """Create valid 2D file in a temporary folder."""
    data_2d = np.ones((3,3))

    final_path = f"{tmp_path}/readout_noise_3x3.npy"
    np.save(final_path, arr=data_2d)

    return final_path

def test_output_node_noise_cmos_user_array(cmos_2x3: CMOS, valid_ones_path_2x3: str):
    cmos_2x3.signal.array = np.ones(cmos_2x3.geometry.shape)

    rng = np.random.default_rng(seed=12345)

    output_node_noise_cmos_user_array(cmos_2x3, valid_ones_path_2x3, valid_ones_path_2x3, rng)

    expected = np.array([
        [0.99576175, 1.02263728, 1.00129338],
        [1.00740827, 1.00924657, 1.00259115]
    ])

    # We get floating point issues here, so use pytest.approx()
    for i in range(0, len(cmos_2x3.signal.array)):
        for j in range(0, len(cmos_2x3.signal.array[i])):
            assert cmos_2x3.signal.array[i][j] == pytest.approx(expected[i][j])

def test_output_node_noise_cmos_user_array_invalid(
        cmos_2x3: CMOS, 
        invalid_noise_path: str, 
        valid_ones_path_2x3: str,
        valid_ones_path_3x3: str):
    cmos_2x3.signal.array = np.ones(cmos_2x3.geometry.shape)

    seed = 12345
    rng = np.random.default_rng(seed=seed)

    with pytest.raises(ValueError, match="Sigma array is invalid."):
        output_node_noise_cmos_user_array(cmos_2x3, invalid_noise_path, valid_ones_path_2x3, rng)
    with pytest.raises(ValueError, match="Offset array is invalid."):
        output_node_noise_cmos_user_array(cmos_2x3, valid_ones_path_2x3, invalid_noise_path, rng)
    with pytest.raises(ValueError, match="Sigma and Offset arrays are different shapes."):
        output_node_noise_cmos_user_array(cmos_2x3, valid_ones_path_2x3, valid_ones_path_3x3, rng)
    with pytest.raises(ValueError, match="Sigma array shape does not match detector geometry."):
        output_node_noise_cmos_user_array(cmos_2x3, valid_ones_path_3x3, valid_ones_path_3x3, rng)