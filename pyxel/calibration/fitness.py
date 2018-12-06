import numpy as np


def sum_of_abs_residuals(simulated, target, obj=None):
    """TBW.

    :param simulated:
    :param target:
    :param obj:
    :return:
    """
    diff = target - simulated
    if obj and obj.weighting:       # todo change  obj.weighting to obj.weighting_function ???
        diff *= obj.weighting_function
    return np.sum(np.abs(diff))


def sum_of_squared_residuals(simulated, target, obj=None):
    """TBW.

    :param simulated:
    :param target:
    :param obj:
    :return:
    """
    diff = target - simulated
    diff_square = diff * diff
    if obj and obj.weighting:
        diff_square *= obj.weighting_function
    return np.sum(diff_square)
