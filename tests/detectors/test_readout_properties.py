#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from pyxel.detectors.readout_properties import ReadoutProperties


@pytest.mark.parametrize(
    "times, start_time, exp_times, exp_steps, exp_is_linear",
    [
        pytest.param(
            [0.1], None, np.array([0.1]), np.array([0.1]), True, id="One element"
        ),
        pytest.param(
            [1, 2, 3],
            None,
            np.array([1, 2, 3], dtype=float),
            np.array([1, 1, 1], dtype=float),
            True,
            id="Three elements",
        ),
    ],
)
def test_readout_properties(
    times, start_time: float | None, exp_times, exp_steps, exp_is_linear
):
    """Test class 'ReadoutProperties'."""
    if start_time is None:
        obj = ReadoutProperties(times=times)
    else:
        obj = ReadoutProperties(times=times, start_time=start_time)

    result_times = obj.times
    result_steps = obj.steps
    result_times_linear = obj.times_linear

    assert_array_equal(result_times, exp_times)
    assert_array_equal(result_steps, exp_steps)
    assert_array_equal(result_times_linear, exp_is_linear)


@pytest.mark.parametrize(
    "times, start_time, exp_error, exp_msg",
    [
        pytest.param(
            [[1, 2, 3]], 0.0, ValueError, r"Readout times must be 1D", id="Not 1D"
        ),
        pytest.param(
            [3, 2, 1],
            0.0,
            ValueError,
            r"Readout times must be strictly increasing",
            id="Not monotonic",
        ),
        pytest.param(
            [0],
            0.0,
            ValueError,
            r"Readout times should be non-zero values",
            id="Non-zero values",
        ),
        pytest.param(
            [1],
            1,
            ValueError,
            r"Readout times should be greater than start time",
            id="Time greater than start time 1",
        ),
        pytest.param(
            [1],
            2,
            ValueError,
            r"Readout times should be greater than start time",
            id="Time greater than start time 1",
        ),
    ],
)
def test_readout_properties_wrong(times, start_time, exp_error, exp_msg):
    """Test class 'ReadoutProperties' with wrong inputs."""
    with pytest.raises(exp_error, match=exp_msg):
        _ = ReadoutProperties(times=times, start_time=start_time)
