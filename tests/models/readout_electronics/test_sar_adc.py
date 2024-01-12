#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.readout_electronics import sar_adc


@pytest.fixture
def ccd_10x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=10,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(
            adc_bit_resolution=16, adc_voltage_range=(0.0, 10.0)
        ),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector


def test_sar_adc(ccd_10x3: CCD):
    """Test model 'sar_adc' with valid inputs."""
    sar_adc(detector=ccd_10x3)
