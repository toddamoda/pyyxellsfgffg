""" PyXEL is an detector simulation framework. """
from pyxel.pipelines.yaml_processor import load_config
from pyxel.pipelines import detection_pipeline

__all__ = ['load_config', 'detection_pipeline']

__appname__ = 'Pyxel'
__author__ = 'David Lucsanyi'
__pkgname__ = 'pyxel'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
