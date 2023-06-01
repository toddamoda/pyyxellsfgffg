#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest

from pyxel.calibration.fitness import (
    reduced_chi_squared,
    sum_of_abs_residuals,
    sum_of_squared_residuals,
)


@pytest.mark.parametrize(
    "simulated, target, weight, exp_result",
    [
        pytest.param(
            np.array([1, 2, 3, 4], dtype=float),
            np.array([1.1, 1.8, 3.3, 4], dtype=float),
            1,
            0.6,
            id="normal",
        ),
        pytest.param(
            np.array([1, 2, 3, 4, np.nan], dtype=float),
            np.array([1.1, 1.8, 3.3, 4, 5], dtype=float),
            1,
            0.6,
            id="with NaN",
        ),
    ],
)
def test_sum_of_abs_residuals(simulated, target, weight, exp_result):
    """Test function 'sum_of_abs_residuals."""
    result = sum_of_abs_residuals(simulated=simulated, target=target, weighting=weight)

    assert result == pytest.approx(exp_result)


@pytest.mark.parametrize(
    "simulated, target, weight, exp_result",
    [
        pytest.param(
            np.array([1, 2, 3, 4], dtype=float),
            np.array([1.1, 1.8, 3.3, 4.0], dtype=float),
            1,
            0.14,
            id="normal",
        ),
        pytest.param(
            np.array([1, 2, 3, 4, np.nan], dtype=float),
            np.array([1.1, 1.8, 3.3, 4.0, 5], dtype=float),
            1,
            0.14,
            id="with NaN",
        ),
    ],
)
def test_sum_of_squared_residuals(simulated, target, weight, exp_result):
    """Test function 'sum_of_squared_residuals'."""
    result = sum_of_squared_residuals(
        simulated=simulated, target=target, weighting=weight
    )

    assert result == pytest.approx(exp_result)


@pytest.mark.parametrize(
    "simulated, target, weight, free_parameters, exp_result",
    [
        pytest.param(
            np.array([1, 2, 3, 4], dtype=float),
            np.array([1.1, 1.8, 3.3, 4.0], dtype=float),
            1,
            2,
            0.07,
            id="normal",
        ),
        pytest.param(
            np.array([1, 2, 3, 4, np.nan], dtype=float),
            np.array([1.1, 1.8, 3.3, 4.0, 5], dtype=float),
            1,
            2,
            0.07,
            id="with NaN",
        ),
    ],
)
def test_reduced_chi_squared(simulated, target, weight, free_parameters, exp_result):
    """Test function 'reduced_chi_squared'."""
    result = reduced_chi_squared(
        simulated=simulated,
        target=target,
        free_parameters=free_parameters,
        weighting=weight,
    )

    assert result == pytest.approx(exp_result)
