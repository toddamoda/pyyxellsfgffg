"""PyXEL is an detector simulation framework."""


from pyxel.io.yaml_processor import load_config
# from pyxel.pipelines import ccd_pipeline
# from pyxel.pipelines import cmos_pipeline
from pyxel.pipelines import models
from pyxel.pipelines import processor
from pyxel.pipelines.validator import check_range
from pyxel.pipelines.validator import check_choices
from pyxel.pipelines.validator import validate_call
from pyxel.pipelines.validator import validate
from pyxel.pipelines.validator import argument
from pyxel.pipelines.validator import parameters
from pyxel.pipelines.validator import ValidationError
from pyxel.pipelines.validator import AttrClass
from pyxel.pipelines.validator import attr_class
from pyxel.pipelines.validator import attr_def

from pyxel.pipelines.model_registry import register
from pyxel.pipelines.model_registry import registry
from pyxel.pipelines.model_registry import MetaModel
from pyxel.pipelines.model_group import ModelFunction
from pyxel.pipelines.model_group import ModelGroup
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.pipelines.processor import Processor
from pyxel.detectors.detector import Detector


__all__ = ['load_config', 'models', 'processor',
           # 'ccd_pipeline', 'cmos_pipeline',
           'check_range', 'check_choices',
           'validate_call', 'validate', 'ValidationError',
           'AttrClass', 'attr_class', 'attr_def',
           'argument', 'register', 'parameters',
           'registry', 'MetaModel', 'ModelFunction', 'ModelGroup',
           'DetectionPipeline', 'Processor', 'Detector']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__author_email__ = 'david.lucsanyi@esa.int'
__pkgname__ = 'pyxel'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
