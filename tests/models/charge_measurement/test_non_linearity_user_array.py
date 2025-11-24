#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import numpy as np
import pytest

from pyxel.detectors import (
    CCD,
    CMOS
)
from pyxel.models.charge_measurement import output_node_linearity_poly_user_array

@pytest.fixture
def valid_5x5x2_non_linearity_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file on a temporary folder."""
    array = [
        [
            [1.1, 1.2],
            [0.9, 1.0],
            [1.0, 0.85],
            [0.95, 1.02],
            [1.08, 1.09]
        ],
        [
            [1.1, 1.2],
            [0.7, 0.9],
            [1.0, 1.0],
            [0.95, 1.02],
            [1.21, 1.09]
        ],
        [
            [1.1, 1.2],
            [0.9, 1.0],
            [1.0, 1.0],
            [0.95, 1.02],
            [0.96, 1.02]
        ],
        [
            [1.1, 1.2],
            [0.7, 0.9],
            [1.0, 0.96],
            [0.95, 1.02],
            [1.04, 1.01]
        ],
        [
            [1.1, 1.2],
            [0.9, 1.0],
            [1.0, 1.0],
            [0.95, 1.02],
            [0.98, 1.16]
        ]
    ]

    final_path = f"{tmp_path}/non_linearity.npy"
    np.save(final_path, arr=array)

    return final_path

@pytest.fixture
def valid_5x5x3_non_linearity_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file on a temporary folder."""
    array = [
        [
            [1.1, 1.2, 1.0],
            [0.9, 1.0, 1.0],
            [1.0, 0.85, 1.0],
            [0.95, 1.02, 1.0],
            [1.08, 1.09, 1.0]
        ],
        [
            [1.1, 1.2, 1.0],
            [0.7, 0.9, 1.0],
            [1.0, 1.0, 1.0],
            [0.95, 1.02, 1.0],
            [1.21, 1.09, 1.0]
        ],
        [
            [1.1, 1.2, 1.0],
            [0.9, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.95, 1.02, 1.0],
            [0.96, 1.02, 1.0]
        ],
        [
            [1.1, 1.2, 1.0],
            [0.7, 0.9, 1.0],
            [1.0, 0.96, 1.0],
            [0.95, 1.02, 1.0],
            [1.04, 1.01, 1.0]
        ],
        [
            [1.1, 1.2, 1.0],
            [0.9, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.95, 1.02, 1.0],
            [0.98, 1.16, 1.0]
        ]
    ]

    final_path = f"{tmp_path}/non_linearity.npy"
    np.save(final_path, arr=array)

    return final_path

def test_output_node_linearity_poly_user_array_valid_5x5x2(cmos_5x5: CCD, valid_5x5x2_non_linearity_path: str):
    ## so we have a valid npy file, we want to send this in
    # do we need to initialise the signal array at all?

    cmos_5x5.characteristics.adc_voltage_range = [0,2]
    cmos_5x5.signal.array = np.ones((cmos_5x5.geometry.row, cmos_5x5.geometry.col))
    output_node_linearity_poly_user_array(cmos_5x5, valid_5x5x2_non_linearity_path)

    expected = np.array(
        [
            np.array([2.3e-5 , 1.9e-5 , 1.85e-5, 1.97e-5, 2.17e-5], np.float64),
            np.array([2.3e-5 , 1.6e-5 , 2.e-5, 1.97e-5, 2.3e-5 ], np.float64),
            np.array([2.3e-5 , 1.9e-5 , 2.e-5, 1.97e-5, 1.98e-5], np.float64),
            np.array([2.3e-5 , 1.6e-5 , 1.96e-5, 1.97e-5, 2.05e-5], np.float64),
            np.array([2.3e-5 , 1.9e-5 , 2.e-5, 1.97e-5, 2.14e-5], np.float64)
        ]
    )

    # We gt floating point issues here, so use pytest.approx()
    for i in range(0, len(cmos_5x5.signal.array)):
        for j in range(0, len(cmos_5x5.signal.array[i])):
            assert cmos_5x5.signal.array[i][j] == pytest.approx(expected[i][j])

def test_output_node_linearity_poly_user_array_valid_5x5x3(cmos_5x5: CCD, valid_5x5x3_non_linearity_path: str):
    # We have a valid npy file thanks to the test above
    # This test is to see if it acknowledges the third coefficient
    # Notice that the expected values are larger here than above.

    cmos_5x5.characteristics.adc_voltage_range = [0,2]
    cmos_5x5.signal.array = np.ones((cmos_5x5.geometry.row, cmos_5x5.geometry.col))
    output_node_linearity_poly_user_array(cmos_5x5, valid_5x5x3_non_linearity_path)

    expected = np.array(
        [
            np.array([3.3e-5 , 2.9e-5 , 2.85e-5, 2.97e-5, 3.17e-5], np.float64),
            np.array([3.3e-5 , 2.6e-5 , 3.e-5, 2.97e-5, 3.3e-5 ], np.float64),
            np.array([3.3e-5 , 2.9e-5 , 3.e-5, 2.97e-5, 2.98e-5], np.float64),
            np.array([3.3e-5 , 2.6e-5 , 2.96e-5, 2.97e-5, 3.05e-5], np.float64),
            np.array([3.3e-5 , 2.9e-5 , 3.e-5, 2.97e-5, 3.14e-5], np.float64)
        ]
    )

    # We gt floating point issues here, so use pytest.approx()
    for i in range(0, len(cmos_5x5.signal.array)):
        for j in range(0, len(cmos_5x5.signal.array[i])):
            assert cmos_5x5.signal.array[i][j] == pytest.approx(expected[i][j])

def test_output_node_linearity_poly_user_array_invalid(cmos_5x5: CMOS):
    path = "invalid_nonlinearity_path.npy"

    with pytest.raises(ValueError):
        output_node_linearity_poly_user_array(cmos_5x5, path)