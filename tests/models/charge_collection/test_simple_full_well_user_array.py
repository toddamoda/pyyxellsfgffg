#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import numpy as np
import pytest

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.charge_collection import simple_full_well_user_array

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

