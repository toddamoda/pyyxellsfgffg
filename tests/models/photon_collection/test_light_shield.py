#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

import numpy as np
from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Environment,
    Characteristics,
    ReadoutProperties
)

from pyxel.models.photon_collection import shield

@pytest.fixture
def ccd_100x100() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=100,
            col=100,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(
            quantum_efficiency=1.0,
            charge_to_volt_conversion=1.0e-6,
            pre_amplification=1.0,
            adc_bit_resolution=16,
            adc_voltage_range=(0.0, 10.0),
        ),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector

def test_light_shield_border_applied(
        ccd_100x100: CCD
):
    ccd_100x100.photon.array = np.ones((100,100))
    total = ccd_100x100.photon.array.size
    width = 10

    shield.shield_border(ccd_100x100, width)

    ones = np.count_nonzero(ccd_100x100.photon.array)
    zeros = total - ones

    # for this shape of detector and shield width, there should be 3600 zeros
    assert zeros == 3600

    # let's check the shape is correct also
    zero_locations = [
        [ 0, 0],
        [10, 9],
        [20, 6],
        [70, 2],
        [91, 8],
        [ 6, 27],
        [ 2, 55],
        [98, 24],
        [93, 68],
        [ 3, 92],
        [45, 95],
        [98, 99]
    ]
    for index in zero_locations:
        assert ccd_100x100.photon.array[index[0],index[1]] == 0

    one_locations = [
        [10, 10],
        [89, 10],
        [10, 89],
        [89, 89],
        [30, 56],
        [80, 22],
        [76, 41],
        [50, 50]
    ]
    for index in one_locations:
        assert ccd_100x100.photon.array[index[0],index[1]] == 1

def test_light_shield_box_applied(
        ccd_100x100: CCD
):
    ccd_100x100.photon.array = np.ones((100,100))
    total = ccd_100x100.photon.array.size
    shield_start = (20, 24)
    shield_end = (51, 32)

    shield.shield_box(ccd_100x100, shield_start, shield_end)

    ones = np.count_nonzero(ccd_100x100.photon.array)
    zeros = total - ones

    # for this shape of detector and shield width, there should be 288 zeros
    assert zeros == 288

    # let's check the shape is correct also
    zero_locations = [
        [20,24],
        [35,29],
        [51,32],
        [20,32],
        [51,24],
        # [ 6, 27],
        # [ 2, 55],
        # [98, 24],
        # [93, 68],
        # [ 3, 92],
        # [45, 95],
        # [98, 99]
    ]
    for index in zero_locations:
        assert ccd_100x100.photon.array[index[0],index[1]] == 0

    one_locations = [
        [10, 10],
        [19, 33],
        [52, 28],
        [28, 79],
        # [30, 56],
        # [80, 22],
        # [76, 41],
        # [50, 50]
    ]
    for index in one_locations:
        assert ccd_100x100.photon.array[index[0],index[1]] == 1
