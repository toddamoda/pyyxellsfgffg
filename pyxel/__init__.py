"""PyXEL is an detector simulation framework."""

import esapy_config as om

from pyxel.pipelines import models
from pyxel.pipelines import processor
from pyxel.pipelines.model_registry import register
from pyxel.pipelines.model_registry import registry
from pyxel.pipelines.model_registry import MetaModel
from pyxel.pipelines.model_group import ModelFunction
from pyxel.pipelines.model_group import ModelGroup
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.pipelines.processor import Processor
from pyxel.detectors.detector import Detector


__all__ = ['models', 'processor',
           # 'ccd_pipeline', 'cmos_pipeline',
           # 'check_range', 'check_choices',
           # 'validate_call', 'validate', 'ValidationError',
           # 'AttrClass', 'attr_class', 'attr_def',
           # 'argument', 'parameters',
           'registry', 'register', 'MetaModel', 'ModelFunction', 'ModelGroup',
           'DetectionPipeline', 'Processor', 'Detector']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__author_email__ = 'david.lucsanyi@esa.int'
__pkgname__ = 'pyxel'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def define_pyxel_loader():
    """TBW."""
    from pyxel.pipelines.parametric import StepValues
    from pyxel.pipelines.parametric import ParametricConfig
    from pyxel.pipelines.model_group import ModelFunction
    from pyxel.pipelines.model_group import ModelGroup

    om.ObjectModelLoader.add_class_ref(['processor', 'class'])
    om.ObjectModelLoader.add_class_ref(['processor', 'detector', 'class'])
    om.ObjectModelLoader.add_class_ref(['processor', 'detector', None, 'class'])
    om.ObjectModelLoader.add_class_ref(['processor', 'pipeline', 'class'])

    om.ObjectModelLoader.add_class(ParametricConfig, ['parametric'])
    om.ObjectModelLoader.add_class(StepValues, ['parametric', 'steps'], is_list=True)
    om.ObjectModelLoader.add_class(ModelGroup, ['processor', 'pipeline', None])
    om.ObjectModelLoader.add_class(ModelFunction, ['processor', 'pipeline', None, None])


define_pyxel_loader()
