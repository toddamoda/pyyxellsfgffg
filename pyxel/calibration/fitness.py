#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fitness functions for model fitting."""

import numba
import numpy as np


@numba.njit
def sum_of_abs_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    diff = target - simulated
    diff *= weighting

    result = float(np.nansum(np.abs(diff)))
    return result


@numba.njit
def sum_of_squared_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    diff = target - simulated
    diff_square = diff * diff
    diff_square *= weighting

    result = float(np.nansum(diff_square))
    return result


@numba.njit
def reduced_chi_squared(

    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
    free_parameters: int,
) -> float:
    r"""Compute the reduced chi-square error statistic.

    Notes
    -----
    You can find more information at this link
    https://en.wikipedia.org/wiki/Goodness_of_fit

    Parameters
    ----------
    simulated
    target
    weighting
    free_parameters : int
        Number of free parameters in the model

    Returns
    -------
    float
        The reduced :math:`\chi^{2}`.
    """
    # assert target.ndim == 2
    # assert simulated.ndim == 3
    # assert simulated.shape[0] == 1
    # assert target.shape == weighting.shape

    simulated_2d = simulated[0]
    # assert simulated_2d.ndim == 2

    # assert target.size == simulated_2d.size
    # assert target.size >= 1
    diff = target - simulated_2d
    deviation2 = np.square(diff / weighting)

    # print(f'target length={len(target)}')
    # print(f'simulated length={len(simulated)}')

    # size = np.isfinite(diff).sum()
    size = diff.size

    degrees_of_freedom = size - free_parameters

    # assert free_parameters >= 1
    # assert degrees_of_freedom >= 1

    # reduced_chi2 = float(np.nansum(deviation2)) / degrees_of_freedom
    reduced_chi2 = float(np.sum(deviation2)) / degrees_of_freedom
    # if nan does size have to be decreased?
    return reduced_chi2
