#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tests for simple_dark_current model."""
from pathlib import Path

import pytest
import numpy as np

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.charge_generation import simple_dark_current, simple_dark_current_user_array


@pytest.fixture
def ccd_10x10() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(temperature=200.0),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector

@pytest.fixture
def ccd_3x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=3,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=3.0,
            pixel_horz_size=3.0,
        ),
        environment=Environment(temperature=200.0),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


def test_simple_dark_current_valid(ccd_10x10: CCD):
    """Test model 'simple_dark_current' with valid inputs."""
    simple_dark_current(detector=ccd_10x10, dark_rate=1.0)

@pytest.fixture
def valid_noise_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file in a temporary folder."""
    data_2d = (
        np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0]
            ]
        )
    )

    final_path = f"{tmp_path}/noise.npy"
    np.save(final_path, arr=data_2d)

    return final_path

def test_simple_dark_current_user_array(ccd_3x3: CCD, valid_noise_path: str):
    """Test dark current with fixed array input"""

    ccd_3x3.charge.add_charge_array(np.ones(shape=(3,3)))
    simple_dark_current_user_array(ccd_3x3, valid_noise_path, seed=1)

    expected = [
        [ 2.,  1.,  2.],
        [ 2.,  6.,  6.],
        [ 9., 11., 11.]
    ]

    # we'll need to cast the array to a list for this to work
    assert ccd_3x3.charge.array.tolist() == expected
