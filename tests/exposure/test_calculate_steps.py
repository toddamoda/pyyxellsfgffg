#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from pyxel.exposure.readout import calculate_steps


@pytest.mark.parametrize(
    "times, start_time, exp_steps",
    [
        (np.array([1, 2, 4, 7, 10]), 0.0, np.array([1.0, 1.0, 2.0, 3.0, 3.0])),
        (np.array([1, 2, 4, 7, 10]), 0.5, np.array([0.5, 1.0, 2.0, 3.0, 3.0])),
    ],
)
def test_calculate_steps(times, start_time, exp_steps):
    """Test function 'calculate_steps'."""
    steps = calculate_steps(times=times, start_time=start_time)

    assert_array_equal(steps, exp_steps)
