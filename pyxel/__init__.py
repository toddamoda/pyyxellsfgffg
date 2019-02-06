"""Pyxel detector simulation framework."""
import os
import typing as t
import esapy_config.checkers as checkers
import esapy_config.validators as validators
import esapy_config.funcargs as funcargs
import esapy_config.config as config
import esapy_config.io as io


__all__ = ['models', 'detectors', 'pipelines',
           'attribute', 'detector_class',
           'check_type', 'check_path', 'check_range', 'check_choices',
           'validate_choices', 'validate_range', 'validate_type']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__author_email__ = 'david.lucsanyi@esa.int'
__pkgname__ = 'pyxel'
__version__ = '0.3'


def detector_class(cls):
    """TBW."""
    return config.attr_class(maybe_cls=cls)


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


def pyxel_yaml_loader():
    """TBW."""
    from pyxel.parametric.parametric import Configuration
    from pyxel.parametric.parametric import ParametricAnalysis
    from pyxel.parametric.parameter_values import ParameterValues
    from pyxel.calibration.calibration import Calibration
    from pyxel.calibration.calibration import Algorithm
    from pyxel.pipelines.model_function import ModelFunction
    from pyxel.pipelines.model_group import ModelGroup

    io.ObjectModelLoader.add_class_ref(['detector', 'class'])
    io.ObjectModelLoader.add_class_ref(['detector', None, 'class'])

    io.ObjectModelLoader.add_class_ref(['pipeline', 'class'])
    io.ObjectModelLoader.add_class(ModelGroup, ['pipeline', None])
    io.ObjectModelLoader.add_class(ModelFunction, ['pipeline', None, None])

    io.ObjectModelLoader.add_class(Configuration, ['simulation'])

    io.ObjectModelLoader.add_class(ParametricAnalysis, ['simulation', 'parametric'])
    io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'parametric', 'parameters'], is_list=True)

    io.ObjectModelLoader.add_class(Calibration, ['simulation', 'calibration'])
    io.ObjectModelLoader.add_class(Algorithm, ['simulation', 'calibration', 'algorithm'])
    io.ObjectModelLoader.add_class(ModelFunction, ['simulation', 'calibration', 'fitness_function'])
    io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'calibration', 'parameters'], is_list=True)


pyxel_yaml_loader()
