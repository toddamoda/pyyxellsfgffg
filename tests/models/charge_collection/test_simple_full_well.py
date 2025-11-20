#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tests for full well models."""

from pathlib import Path

import numpy as np
import pytest

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.charge_collection import simple_full_well, simple_full_well_user_array


@pytest.fixture
def ccd_10x10() -> CCD:
    """Create a valid 10x10 CCD detector."""
    return CCD(
        geometry=CCDGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )

@pytest.fixture
def ccd_3x3() -> CCD:
    """Create a valid 3x3 CCD detector."""
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
    return detector


@pytest.mark.parametrize(
    "fwc",
    [
        pytest.param(
            10,
        ),
        pytest.param(
            None,
        ),
    ],
)
def test_full_well(
    ccd_10x10: CCD,
    fwc: int,
):
    """Test model 'simple_full_well' with valid inputs."""

    detector = ccd_10x10
    detector.characteristics.full_well_capacity = 10
    detector.pixel.array = np.ones((detector.geometry.row, detector.geometry.col)) * 50

    simple_full_well(detector=ccd_10x10, fwc=fwc)

    assert np.max(detector.pixel.array <= 10)


@pytest.mark.parametrize(
    "fwc, exp_exc, exp_error",
    [
        pytest.param(
            -5,
            ValueError,
            "Full well capacity should be a positive number.",
        ),
    ],
)
def test_full_well_bad_inputs(
    ccd_10x10: CCD,
    fwc: int,
    exp_exc,
    exp_error,
):
    """Test model 'simple_full_well' with bad inputs."""
    with pytest.raises(exp_exc, match=exp_error):
        simple_full_well(detector=ccd_10x10, fwc=fwc)

@pytest.fixture
def valid_fwc_path(
    tmp_path: Path,
) -> str:
    """Create valid 2D file in a temporary folder."""
    data_2d = (
        np.array(
            [
                [21400, 21300, 21200],
                [20000, 20100, 20200],
                [22000, 22100, 22200]
            ]
        )
    )

    final_path = f"{tmp_path}/fwc.npy"
    np.save(final_path, arr=data_2d)

    return final_path

def test_simple_full_well_user_array(
    ccd_3x3: CCD,
    valid_fwc_path: str
):
    """Test model `simple_full_well_user_array` with a valid file."""

    ccd_3x3.pixel.array = np.array(
        [
            [23400, 20300, 21100],
            [20000, 23100, 21210],
            [21000, 22140, 22000]
        ],
    dtype=float)

    expected = np.array(
            [
            [21400, 20300, 21100],
            [20000, 20100, 20200],
            [21000, 22100, 22000]
        ],
    dtype=float)
    simple_full_well_user_array(ccd_3x3, valid_fwc_path)

    assert (ccd_3x3.pixel.array == expected).all()

