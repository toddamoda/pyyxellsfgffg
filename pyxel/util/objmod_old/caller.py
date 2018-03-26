"""TBW."""
import inspect
import functools


def get_call_ref(obj, func_name=None):
    """Return a reference to a object's method, function or property.

    :param obj:
    :param func_name:
    :return: callable
    """
    builtin_map = {
        '__dir__': dir,
        '__str__': str,
        '__setattr__': setattr,
        '__getattribute__': getattr,
        '__repr__': repr,
    }

    # case 0: built in function
    if func_name in builtin_map:
        func_ref = functools.partial(builtin_map[func_name], obj)

    elif inspect.ismodule(obj) and func_name:
        # case 1: object is a module instance
        func_ref = getattr(obj, func_name)

    elif inspect.isclass(obj):
        # case 2: object is a class/type
        if func_name in [None, '', '__init__', '__new__']:
            # case 2a: constructor
            func_ref = obj
        else:
            # case 2b: static method
            func_ref = getattr(obj, func_name)

    elif callable(obj) and not func_name:
        # case 3: object is a function or a object that has __call__ defined
        func_ref = obj

    elif hasattr(obj, '__class__') and func_name:
        # case 4: a class instance that inherits from object
        func_ref = obj.__class__.__dict__.get(func_name)
        if isinstance(func_ref, property):
            if func_ref.fget and not func_ref.fset:
                # case 4a: only property getter defined
                func_ref = functools.partial(func_ref.fget, obj)
            elif func_ref.fget and func_ref.fset:
                # case 4b: both property getter and setter are defined
                func_ref_prop = [functools.partial(func_ref.fget, obj),
                                 functools.partial(func_ref.fset, obj)]

                def set_get(*value):
                    return func_ref_prop[bool(len(value))](*value)

                func_ref = set_get
                # func_ref = lambda *vals: func_ref_prop[bool(len(vals))](*vals)

        elif func_ref:
            # case 4c: a method
            func_ref = functools.partial(func_ref, obj)

    return func_ref


def call(obj, func_name, *args, **kwargs):
    """Call a object method or property / module function or class constructor.

    :param obj:
    :param func_name:
    :param args:
    :param kwargs:
    :return:
    """
    func_ref = get_call_ref(obj, func_name)
    result = func_ref(*args, **kwargs)
    return result
