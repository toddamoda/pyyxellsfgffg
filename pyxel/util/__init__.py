"""Utility functions."""
import logging
# import functools
import glob
import importlib
from ast import literal_eval

from pyxel.util.fitsfile import FitsFile


def update_fits_header(header, key, value):
    """TBW.

    :param header:
    :param key:
    :param value:
    :return:
    """
    if not isinstance(value, (str, int, float)):
        value = '%r' % value

    if isinstance(value, str):
        value = value[0:24]

    if isinstance(key, (list, tuple)):
        key = '/'.join(key)

    key = key.replace('.', '/')[0:36]

    header[key] = value


def get_obj_att(obj, key):
    """TBW.

    :param obj:
    :param key:
    :return:
    """
    obj_props = key.split('.')
    att = obj_props[-1]
    for part in obj_props[:-1]:
        try:
            obj = getattr(obj, part)
        except AttributeError:
            # logging.error('Cannot find attribute %r in key %r', part, key)
            obj = None
            break
    return obj, att


def get_value(obj, key):
    """TBW.

    :param obj:
    :param key:
    :return:
    """
    obj, att = get_obj_att(obj, key)

    if isinstance(obj, dict) and att in obj:
        value = obj[att]
    else:
        value = getattr(obj, att)

    return value


def eval_range(values):
    """Evaluate a string representation of a list or numpy array.

    :param values:
    :return: list
    """
    if values:
        if isinstance(values, str):
            if 'numpy' in values:
                locals_dict = {'numpy': importlib.import_module('numpy')}
                globals_dict = None
                values = eval(values, globals_dict, locals_dict)
                # NOTE: the following casting is to ensure JSON serialization works
                # JSON does not accept numpy.int* or numpy.float* types.
                if values.dtype == float:
                    values = [float(value) for value in values]
                elif values.dtype == int:
                    values = [int(value) for value in values]
                else:
                    logging.warning('numpy data type is not a float or int: %r', values)
            else:
                values = eval(values)

        if not isinstance(values, (list, tuple)):
            values = list(values)
    else:
        values = []
    return values


def eval_entry(value):
    """TBW.

    :param value:
    :return:
    """
    if isinstance(value, str):
        try:
            literal_eval(value)
        except (SyntaxError, ValueError, NameError):
            # ensure quotes in case of string literal value
            if value[0] == "'" and value[-1] == "'":
                pass
            elif value[0] == '"' and value[-1] == '"':
                pass
            else:
                value = '"' + value + '"'

        value = literal_eval(value)
    return value


def apply_run_number(path):
    """Convert the file name numeric placeholder to a unique number.

    :param path:
    :return:
    """
    path_str = str(path)
    if '?' in path_str:
        dir_list = sorted(glob.glob(path_str))
        p_0 = path_str.find('?')
        p_1 = path_str.rfind('?')
        template = path_str[p_0: p_1 + 1]
        path_str = path_str.replace(template, '{:0%dd}' % len(template))
        last_num = 0
        if len(dir_list):
            path_last = dir_list[-1]
            last_num = int(path_last[p_0: p_1 + 1])
        last_num += 1
        path_str = path_str.format(last_num)
    return type(path)(path_str)


def copy_processor(obj):
    """TBW.

    :param obj:
    :return:
    """
    cls = type(obj)
    if hasattr(obj, '__getstate__'):
        cpy_kwargs = {}
        for key, value in obj.__getstate__().items():
            cpy_kwargs[key] = copy_processor(value)
        obj = cls(**cpy_kwargs)

    elif isinstance(obj, dict):
        cpy_obj = cls()
        for key, value in obj.items():
            cpy_obj[key] = copy_processor(value)
        obj = cpy_obj

    elif isinstance(obj, list):
        cpy_obj = cls()
        for value in obj:
            cpy_obj.append(copy_processor(value))
        obj = cpy_obj

    return obj


__all__ = ['FitsFile', 'update_fits_header', 'get_obj_att',
           'eval_range', 'eval_entry', 'apply_run_number',
           'copy_processor']
