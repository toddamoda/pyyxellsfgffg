"""Pyxel detector simulation framework."""
import os
import typing as t
import esapy_config.checkers as checkers
import esapy_config.validators as validators
import esapy_config.funcargs as funcargs
import esapy_config.config as config
from ._version import get_versions


__all__ = ['models',
           # 'detectors', 'pipelines',
           # 'Detector', 'CCD', 'CMOS',     # todo
           'attribute', 'detector_class',
           'check_type', 'check_path', 'check_range', 'check_choices',
           'validate_choices', 'validate_range', 'validate_type']


__version__ = get_versions()['version']
del get_versions


def detector_class(cls):
    """TBW."""
    return config.attr_class(maybe_cls=cls, init_set=True)


def attribute(doc: t.Optional[str] = None,
              is_property: t.Optional[bool] = None,
              on_set: t.Optional[t.Callable] = None,
              on_get: t.Optional[t.Callable] = None,
              on_change: t.Optional[t.Callable] = None,
              use_dispatcher: t.Optional[bool] = None,
              on_get_update: t.Optional[bool] = None,
              **kwargs):
    """TBW."""
    return config.attr_def(doc=doc,
                           is_property=is_property,
                           on_set=on_set,
                           on_get=on_get,
                           on_change=on_change,
                           use_dispatcher=use_dispatcher,
                           on_get_update=on_get_update,
                           **kwargs)


def argument(name: str, **kwargs):
    """TBW."""
    return funcargs.argument(name=name, **kwargs)


# def logger():     # todo
#     """TBW."""
#     log = logging.getLogger('pyxel')
#     log.info('')


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


def check_path(path):
    """TBW."""
    return os.path.exists(path)


def check_type(att_type, is_optional: bool = False) -> t.Callable[..., bool]:
    """TBW."""
    return checkers.check_type_function(att_type=att_type, is_optional=is_optional)


def check_range(min_val: t.Union[float, int], max_val: t.Union[float, int]):
    """TBW."""
    return checkers.check_range(min_val=min_val,
                                max_val=max_val,
                                step=None, enforce_step=False)
    # todo: rounding BUG in checkers.check_range() when value is a float!


def check_choices(choices: list):
    """TBW."""
    return checkers.check_choices(choices)


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
