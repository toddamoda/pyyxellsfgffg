#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel!
util funcs for TARS charge generation model."""

import bisect
import numpy as np
from scipy import interpolate


def sampling_distribution(distribution):
    """TBW.
    
    :param distribution: 
    :return: 
    """
    u = np.random.random()
    # random_value_from_dist = distribution[bisect.bisect(distribution[:, 1], u) - 1, 0]
    random_value_from_dist = get_xvalue_with_interpolation(distribution, u)

    return random_value_from_dist


def get_xvalue_with_interpolation(function_array, y_value):
    """TBW.
    
    :param function_array: 
    :param y_value: 
    :return: 
    """
    y_index_bot = bisect.bisect(function_array[:, 1], y_value) - 1
    y_index_top = y_index_bot + 1
    y_value_bot = function_array[y_index_bot, 1]
    y_value_top = function_array[y_index_top, 1]
    x_value_bot = function_array[y_index_bot, 0]
    x_value_top = function_array[y_index_top, 0]

    intpol_x_value = x_value_bot + (y_value - y_value_bot) * (x_value_top - x_value_bot) / (y_value_top - y_value_bot)

    return intpol_x_value


# def get_yvalue_with_interpolation(function_array, x_value):
#
#     x_index_bot = bisect.bisect(function_array[:, 0], x_value) - 1
#     x_index_top = x_index_bot + 1
#     x_value_bot = function_array[x_index_bot, 0]
#     x_value_top = function_array[x_index_top, 0]
#     y_value_bot = function_array[x_index_bot, 1]
#     y_value_top = function_array[x_index_top, 1]
#
#     intpol_y_value = y_value_bot + (x_value - x_value_bot) * (y_value_top - y_value_bot) / (x_value_top - x_value_bot)
#
#     return intpol_y_value


def read_data(file_name):
    """TBW.
    
    :param file_name: 
    :return: 
    """
    data = np.loadtxt(file_name, 'float', '#')
    return data


def interpolate_data(data):
    """TBW.
    
    :param data: 
    :return: 
    """
    data_function = interpolate.interp1d(data[:, 0], data[:, 1], kind='linear')
    return data_function
