"""Utility functions."""
import logging
# import functools
import glob
import importlib
from ast import literal_eval

from pyxel.util.fitsfile import FitsFile


def load(yaml_filename):
    """TBW.

    :param yaml_filename:
    :return:
    """
    from pyxel.io.yaml_processor import load_config
    cfg = load_config(yaml_filename)
    if 'parametric' in cfg:
        parametric = cfg.pop('parametric')  # type: pyxel.pipelines.parametric.ParametricConfig
    else:
        parametric = None

    processor = cfg[next(iter(cfg))]  # type: pyxel.pipelines.processor.Processor
    return parametric, processor


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
        # TODO: consider using this instead:
        # result = eval(value, {}, np.__dict__)
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


def copy_state(obj):
    """TBW.

    :param obj:
    :return:
    """
    kwargs = {}
    for key, value in obj.__getstate__().items():
        obj_att = getattr(obj, key)
        if obj_att is None:
            cpy_obj = None
        elif hasattr(obj_att, 'copy'):
            cpy_obj = obj_att.copy()
        else:
            cpy_obj = type(obj_att)(obj_att)
        kwargs[key] = cpy_obj
    # kwargs = {key: getattr(obj, key).copy() if value else None for key, value in obj.__getstate__().items()}
    return kwargs


def copy_processor(obj):
    """TBW.

    :param obj:
    :return:
    """
    # if isinstance(obj, dict):
    #     cpy_obj = {}
    #     for key, value in obj.items():
    #         cpy_obj[key] = value.copy()
    #     return cpy_obj
    # else:
    #     return obj.copy()

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


def get_state_dict(obj):
    """TBW."""
    def get_state_helper(val):
        """TBW."""
        if hasattr(val, 'get_state_json'):
            return val.get_state_json()
        elif hasattr(val, '__getstate__'):
            return val.__getstate__()
        else:
            return val

    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            result[key] = get_state_dict(value)
    else:
        for key, value in obj.__getstate__().items():
            if isinstance(value, list):
                result[key] = [get_state_helper(val) for val in value]

            elif isinstance(value, dict):
                result[key] = {key2: get_state_helper(val) for key2, val in value.items()}

            else:
                result[key] = get_state_helper(value)
    return result


def get_state(obj):
    """Convert the config object to a embedded dict object.

    The returned value will be a dictionary tree that is JSON
    compatible. Only dict, list, str, numbers will be contained
    in the returned dictionary.

    :param obj: a top level dict object or a object that defines
        the __getstate__ method.

    :return: the dictionary representation of the passed object.
    """
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            result[key] = value.__getstate__()

    elif hasattr(obj, '__getstate__'):
        result = obj.__getstate__()

    return result


def get_state_ids(obj, parent_key_list=None, result=None):
    """TBW.

    :param obj:
    :param parent_key_list:
    :param result:
    :return:
    """
    if result is None:
        from collections import OrderedDict
        result = OrderedDict()

    if parent_key_list is None:
        parent_key_list = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (str, int, float)):
                key = '.'.join(parent_key_list) + '.' + key
                result[key] = value
            else:
                list(parent_key_list) + [key]
                get_state_ids(value, list(parent_key_list) + [key], result)

    elif isinstance(obj, list):
        is_primitive = all([isinstance(value, (str, int, float)) for value in obj])
        if is_primitive:
            key = '.'.join(parent_key_list)
            result[key] = obj
        else:
            for i, value in enumerate(obj):
                get_state_ids(value, list(parent_key_list) + [str(i)], result)
    return result


def evaluate_reference(reference_str):
    """Evaluate a module's class, function, or constant.

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


__all__ = ['FitsFile', 'update_fits_header', 'get_obj_att',
           'eval_range', 'eval_entry', 'apply_run_number',
           'copy_processor', 'get_state', 'get_state_ids',
           'copy_state', 'evaluate_reference']
