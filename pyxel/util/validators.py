"""TBW."""

import typing as t

import esapy_config.funcargs as funcargs
import esapy_config.validators as validators

__all__ = ['validate', 'validate_choices', 'validate_range', 'validate_type']


# from functools import wraps
def validate(func: t.Callable):
    """TBW."""
    # @wraps(func)
    # def new_func(*args, **kwargs):
    #     prev_func = om.validate(func)  # type: t.Callable
    #     return prev_func(*args, **kwargs)
    # return new_func
    new_func = funcargs.validate(func)            # type: t.Callable
    new_func.__doc__ = func.__doc__                     # used by sphinx
    new_func.__annotations__ = func.__annotations__     # used by sphinx
    new_func.__module__ = func.__module__               # used by sphinx

    # new_func.__name__ = func.__name__               # not used by sphinx unless we missing something
    # new_func.__defaults__ = func.__defaults__       # not used by sphinx unless we missing something !!!!
    return new_func


def validate_choices(choices, is_optional=False):
    """TBW."""
    return validators.validate_choices(choices=choices,
                                       is_optional=is_optional)


def validate_range(min_val: t.Union[float, int], max_val: t.Union[float, int],
                   is_optional: bool = False):
    """TBW."""
    return validators.validate_range(min_val=min_val,
                                     max_val=max_val,
                                     is_optional=is_optional,
                                     step=None, enforce_step=False)
    # todo: rounding BUG in om.check_range() when value is a float!


def validate_type(att_type, is_optional: bool = False):
    """TBW."""
    return validators.validate_type(att_type=att_type,
                                    is_optional=is_optional)
