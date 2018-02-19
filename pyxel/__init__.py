"""PyXEL is an detector simulation framework."""


from pyxel.io.yaml_processor import load_config
from pyxel.pipelines import ccd_pipeline
from pyxel.pipelines import cmos_pipeline
from pyxel.pipelines import models
from pyxel.pipelines import processor

__all__ = ['load_config', 'ccd_pipeline', 'cmos_pipeline', 'models', 'processor']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__author_email__ = 'david.lucsanyi@esa.int'
__pkgname__ = 'pyxel'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
