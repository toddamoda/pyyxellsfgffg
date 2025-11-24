#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
from pathlib import Path

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.charge_measurement import simple_measurement_user_array

@pytest.fixture
def ccd_2x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=2,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector

@pytest.fixture
def valid_gain_path(
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

def test_simple_measurement_user_array(ccd_2x3: CCD, valid_gain_path: str):
    """Test gain with user array for simple measurement."""

    ccd_2x3.pixel.array = np.ones((ccd_2x3.geometry.row, ccd_2x3.geometry.col)) + 1 #array of 2s

    simple_measurement_user_array(ccd_2x3, valid_gain_path)

    expected = np.array(
        [
            [2.0, 4.0, 6.0],
            [8.0, 10.0, 12.0]
        ]
    )

    assert (ccd_2x3.signal.array == expected).all()