#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest
import numpy as np

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.data_processing import apply_gain

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
        environment=Environment(),
        characteristics=Characteristics(
            adc_bit_resolution=14,
            adc_voltage_range=[0.,2.],
            gain_array_path="tests/data/test_gain_array.data"
        ),
    )

    detector.characteristics.initialize(detector.geometry)

    return detector

def test_gain_array(
        ccd_3x3 : CCD
) :
    ccd_3x3.image.array = np.array([
        [10, 10, 20],
        [5, 5, 5],
        [13, 12, 18]
    ], dtype=np.uint8)        
    apply_gain(ccd_3x3)

    expected = np.array([
        [11, 12, 26],
        [4.5, 5, 5.5],
        [13, 12, 18]
    ])

    assert (ccd_3x3.data["n_array"] == expected).all()