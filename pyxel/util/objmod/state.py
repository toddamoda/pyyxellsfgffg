"""TBW."""


def get_obj_by_type(obj, key, obj_type=None):
    """TBW.

    :param obj:
    :param key:
    :param obj_type:
    :return:
    """
    obj, att = get_obj_att(obj, key, obj_type)
    if isinstance(obj, obj_type):
        return obj


def get_obj_att(obj, key, obj_type=None):
    """TBW.

    :param obj:
    :param key:
    :param obj_type:
    :return:
    """
    obj_props = key.split('.')
    att = obj_props[-1]
    for part in obj_props[:-1]:
        try:
            if isinstance(obj, dict):
                obj = obj[part]
            else:
                obj = getattr(obj, part)

            if obj_type and isinstance(obj, obj_type):
                return obj, att

        except AttributeError:
            # logging.error('Cannot find attribute %r in key %r', part, key)
            obj = None
            break
    return obj, att


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
    elif isinstance(obj, list):
        result = []
        for value in obj:
            result.append(get_state_dict(value))
    else:
        if not hasattr(obj, '__getstate__'):
            return result
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
