"""Pyxel detector simulation framework."""
import os
import typing as t
import esapy_config as om

from pyxel.pipelines.parametric import Configuration
from pyxel.pipelines.parametric import ParametricAnalysis
from pyxel.pipelines.parametric import StepValues
from pyxel.calibration.calibration import Calibration
from pyxel.calibration.calibration import Algorithm
from pyxel.pipelines.model_function import ModelFunction
from pyxel.pipelines.model_group import ModelGroup

__all__ = ['models', 'detectors', 'pipelines',
           'check_type', 'check_path', 'check_range', 'check_choices']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__author_email__ = 'david.lucsanyi@esa.int'
__pkgname__ = 'pyxel'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

om.ObjectModelLoader.add_class_ref(['processor', 'class'])
om.ObjectModelLoader.add_class_ref(['processor', 'detector', 'class'])
om.ObjectModelLoader.add_class_ref(['processor', 'detector', None, 'class'])
om.ObjectModelLoader.add_class_ref(['processor', 'pipeline', 'class'])

om.ObjectModelLoader.add_class(Configuration, ['simulation'])
om.ObjectModelLoader.add_class(ParametricAnalysis, ['simulation', 'parametric_analysis'])
om.ObjectModelLoader.add_class(StepValues, ['simulation', 'parametric_analysis', 'steps'], is_list=True)

om.ObjectModelLoader.add_class(Calibration, ['simulation', 'calibration'])
om.ObjectModelLoader.add_class(ModelFunction, ['simulation', 'calibration', 'fitness_function'])
om.ObjectModelLoader.add_class(Algorithm, ['simulation', 'calibration', 'algorithm'])

om.ObjectModelLoader.add_class(ModelGroup, ['processor', 'pipeline', None])
om.ObjectModelLoader.add_class(ModelFunction, ['processor', 'pipeline', None, None])


# def register(group, maybe_func=None, **kwargs):         # TODO WHAT IS THIS DOING AND WHY?!?!?
#     """TBW.
#
#     :param group:
#     :param maybe_func:
#     :param kwargs:
#     :return:
#     """
#     enabled = kwargs.pop('enabled', True)
#     ignore_args = kwargs.pop('ignore_args', ['detector'])
#     name = kwargs.pop('name', None)
#     metadata = kwargs
#     metadata['group'] = group
#     return om.register(maybe_func, ignore_args, name, enabled, metadata)


def validate(func: t.Callable):
    """TBW."""
    return om.validate(func)


def argument(name: str, **kwargs):
    """TBW."""
    return om.argument(name, **kwargs)


def check_type(att_type, is_optional: bool = False) -> t.Callable[..., bool]:
    """TBW."""
    return om.check_type_function(att_type, is_optional)


def check_path(path):
    """TBW."""
    return os.path.exists(path)


def check_range(min_val: t.Union[float, int], max_val: t.Union[float, int]):
                # step: t.Union[float, int] = None, enforce_step: bool = False):
    """TBW."""
    return om.check_range(min_val, max_val, step=None, enforce_step=False)
    # todo: rounding BUG in om.check_range() when value is a float!


def check_choices(choices: list):
    """TBW."""
    return om.check_choices(choices)
