#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from typing import Literal

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.readout_electronics import simple_adc
from pyxel.models.readout_electronics.simple_adc import _get_dtype, apply_simple_adc


@pytest.fixture
def ccd_3x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=3,
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
    return detector


@pytest.mark.parametrize("data_type", ["uint16", "uint32", "uint64", "uint"])
def test_simple_adc(
    ccd_3x3: CCD, data_type: Literal["uint16", "uint32", "uint64", "uint"]
):
    """Test model 'simple_adc'."""
    simple_adc(detector=ccd_3x3, data_type=data_type)


@pytest.mark.parametrize(
    "data_type, exp_exc, exp_error",
    [
        ("float", TypeError, "Expecting a signed/unsigned integer"),
        ("float32", TypeError, "Expecting a signed/unsigned integer"),
        ("float64", TypeError, "Expecting a signed/unsigned integer"),
        ("uint8", TypeError, "Expected type of Image array is uint64"),
        ("int32", TypeError, "Expected type of Image array is uint64"),
        ("int64", TypeError, "Expected type of Image array is uint64"),
        ("int", TypeError, "Expected type of Image array is uint64"),
    ],
)
def test_simple_adc_wrong_data_type(
    ccd_3x3: CCD,
    data_type: str,
    exp_exc,
    exp_error,
):
    """Test model 'simple_adc' with wrong 'data_type'."""
    with pytest.raises(exp_exc, match=exp_error):
        simple_adc(
            detector=ccd_3x3,
            data_type=data_type,
        )


@pytest.mark.parametrize(
    "signal, bit_resolution, voltage_range, dtype, exp_output",
    [
        pytest.param(
            np.array([0.0, 0.4, 0.5, 0.6, 1.0, 7.0, 8.0, 14.0, 15.0]),
            4,
            (0.0, 15.0),
            np.uint8,
            np.array([0, 0, 0, 0, 1, 7, 8, 14, 15], dtype=np.uint8),
            id="4 bit - Range: [0.0, 15.0]",
        ),
        pytest.param(
            np.array([-0.1, 0.0, 3.0, 6.0, 6.1]),
            8,
            (0.0, 6.0),
            np.uint8,
            np.array([0, 0, 127, 255, 255], dtype=np.uint8),
            id="8 bit - Range: [0.0, 6.0]",
        ),
        pytest.param(
            np.array([0.9, 1.0, 4.0, 7.0, 7.1]),
            8,
            (1.0, 7.0),
            np.uint8,
            np.array([0, 0, 127, 255, 255], dtype=np.uint8),
            id="8 bit - Range: [1.0, 7.0]",
        ),
        pytest.param(
            np.array([-1.1, -1.0, 2.0, 5.0, 5.1]),
            8,
            (-1.0, 5.0),
            np.uint8,
            np.array([0, 0, 127, 255, 255], dtype=np.uint8),
            id="8 bit - Range: [-1.0, 5.0]",
        ),
        pytest.param(
            np.array([-0.1, 0.0, 6.0, 6.1]),
            16,
            (0.0, 6.0),
            np.uint16,
            np.array([0, 0, 65535, 65535], dtype=np.uint16),
            id="16 bit - Range: [0.0, 6.0]",
        ),
        pytest.param(
            np.array([-0.1, 0.0, 6.0, 6.1]),
            32,
            (0.0, 6.0),
            np.uint32,
            np.array([0, 0, 2**32 - 1, 2**32 - 1], dtype=np.uint32),
            id="32 bit - Range: [0.0, 6.0]",
        ),
    ],
)
def test_apply_simple_adc(signal, bit_resolution, voltage_range, dtype, exp_output):
    """Test function 'apply_simple_adc'."""
    voltage_min, voltage_max = voltage_range
    output = apply_simple_adc(
        signal=signal,
        bit_resolution=bit_resolution,
        voltage_min=voltage_min,
        voltage_max=voltage_max,
        dtype=dtype,
    )

    assert_array_equal(output, exp_output)

    # TODO: Use param 'strict' in 'assert_array_equal' (available in Numpy 1.24)
    assert output.dtype == exp_output.dtype


@pytest.mark.parametrize(
    "bit_resolution, exp_dtype",
    [
        (1, np.dtype(np.uint8)),
        (8, np.dtype(np.uint8)),
        (9, np.dtype(np.uint16)),
        (16, np.dtype(np.uint16)),
        (17, np.dtype(np.uint32)),
        (32, np.dtype(np.uint32)),
        (33, np.dtype(np.uint64)),
        (64, np.dtype(np.uint64)),
    ],
)
def test_get_dtype(bit_resolution, exp_dtype):
    """Test function '_get_dtype'."""
    result = _get_dtype(bit_resolution)
    assert result == exp_dtype
