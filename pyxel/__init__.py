"""PyXEL is an detector simulation framework."""


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
