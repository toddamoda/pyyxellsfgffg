#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Thibaut Prodhomme <thibaut.prodhomme@esa.int>
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------
""" Utility routines for the analysis sub-package. """
import importlib
import inspect

import numpy as np
import pandas as pd


def convert_to_int(value):
    """
    Convert any type of numbers to integers
    :param value:
    :type value: ndarray
    :return value:
    :rtype: int ndarray
    """
    int_value = np.rint(value)
    int_value = int_value.astype(int)
    return int_value


def convert_date_to_string(date):
    """ Convert a string into a `Timestamp` object
    example: convert_date_to_string('2017-07-05T01_39_01.778000')
    Timestamp('2017-07-05 01:39:01.778000')
    """
    return pd.to_datetime(date.replace('_', ':'))


def rect_to_slice(rect):
    """ Convert a 4-tuple (x0, y0, x1, y1) region of interest to
    a 2-tuple y-x slices. Expected rect format is either
    a 4-d tuple/list of integers or a 2-d tuple/list of slices.
    """
    if not isinstance(rect, (list, tuple)):
        raise TypeError('rect: Expected tuple or list, got: %s' % repr(rect))

    if sum([isinstance(val, int) for val in rect]) == 4:
        # convert rect to 2-d slices
        return slice(rect[0], rect[1]), slice(rect[2], rect[3])

    if sum([isinstance(val, slice) for val in rect]) == 2:
        # pass through, it's already in the proper type format
        return rect

    raise TypeError('rect: Incorrect value type(s): %s' % repr(rect))


def get_binned_slice(y_x_slice, binned_rows):
    """

    :param tuple y_x_slice:
    :param int binned_rows:
    :return: new tuple(y, x)
    :rtype: tuple
    :raises ZeroDivisionError: if binned_rows is less than or equal to 0.
    :raises TypeError: if the y_x_slice is not a 2d tuple or list
    """

    if binned_rows <= 0:
        raise ValueError('binned_rows must be greater than 0. Got: %s' % repr(binned_rows))

    if not isinstance(y_x_slice, (list, tuple)):
        raise TypeError('y_x_slice: Expected tuple or list, got: %s' % repr(y_x_slice))

    if len(y_x_slice) != 2:
        raise TypeError('y_x_slice: Expected y_x_slice length of 2, got: %d' % len(y_x_slice))

    y_slice, x_slice = y_x_slice
    if binned_rows > 1:
        if isinstance(y_slice, slice):
            y_start = y_slice.start
            if y_start is not None:
                y_start /= binned_rows

            y_stop = y_slice.stop
            if y_stop is not None:
                y_stop /= binned_rows

            y_slice = slice(y_start, y_stop)

        elif isinstance(y_slice, int):
            y_slice /= binned_rows

    return y_slice, x_slice


def get_missing_arguments(func, func_kwargs):
    """ Test whether or not the function keyword arguments are
    all specified before calling the specified function.

    WARNING: this uses `inspect` which may be a performance hit if called
    excessively.

    :param callable func:
    :param dict func_kwargs: the dictionary to be passed to the func specified.
    :return: True if it is ok to make the call, else False
    :rtype: bool
    """
    missing = []
    argspec = inspect.getargspec(func)      # todo
    defaults = {}
    if argspec.defaults is not None:
        defaults = dict(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))

    for name in argspec.args:
        if name not in func_kwargs:
            if name not in defaults:
                if name != 'self':
                    missing.append(name)
    return missing


def evaluate_reference(reference_str):
    """ Evaluate a module's class, function, or constant.

    :param str reference_str: the python expression to
        evaluate or retrieve the module attribute reference to.
        This is usually a reference to a class or a function.
    :return: the module attribute or object.
    :rtype: object
    :raises ImportError: if reference_str cannot be evaulated to a callable.
    """
    if not reference_str:
        raise ImportError('Empty string cannot be evaluated')

    if '.' not in reference_str:
        raise ImportError('Missing module path')

    # reference to a module class, function, or constant
    module_str, function_str = reference_str.rsplit('.', 1)
    try:
        module = importlib.import_module(module_str)
    except ImportError as exc:
        raise ImportError('Cannot import module: %s. exc: %s' % (module_str, str(exc)))

    try:
        reference = getattr(module, function_str)
    except AttributeError:
        raise ImportError('Module: %s, does not contain %s' % (module_str, function_str))

    return reference
