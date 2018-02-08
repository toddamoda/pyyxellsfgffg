import functools
import re
import typing as t
from pathlib import Path

import numpy as np
import yaml

try:
    # Use LibYAML library
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

import pyxel.detectors.ccd_characteristics
import pyxel.detectors.environment
import pyxel.detectors.geometry
from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.pipelines import detection_pipeline
from pyxel.util import fitsfile
from pyxel.util import util


__all__ = ['load_config']


class PixelLoader(SafeLoader):
    """Custom `SafeLoader` that constructs Pixel core objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature."""


def _expr_processor(loader: PixelLoader, node: yaml.ScalarNode):
    """

    :param loader:
    :param node:
    :return:
    """
    value = loader.construct_scalar(node)

    try:
        result = eval(value, np.__dict__, {})
    except NameError:
        result = value

    return result


def _constructor_processor(loader: PixelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.Processor(**mapping)

    return obj


def _constructor_ccd_pipeline(loader: PixelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CCDDetectionPipeline(**mapping)

    return obj


def _constructor_cmos_pipeline(loader: PixelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CMOSDetectionPipeline(**mapping)

    return obj


def _constructor_ccd(loader: PixelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = pyxel.detectors.geometry.Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = pyxel.detectors.environment.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = pyxel.detectors.ccd_characteristics.CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    image = mapping.get('image', None)

    obj = CCD(photons=photons,
              image=image,
              geometry=geometry,
              environment=environment,
              characteristics=characteristics)

    return obj


def _constructor_cmos(loader: PixelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = pyxel.detectors.geometry.Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = pyxel.detectors.environment.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = pyxel.detectors.ccd_characteristics.CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    image = mapping.get('image', None)

    obj = CMOS(photons=photons,
               image=image,
               geometry=geometry,
               environment=environment,
               characteristics=characteristics)

    return obj


def _constructor_from_file(loader: PixelLoader, node: yaml.ScalarNode):
    filename = Path(loader.construct_scalar(node))
    if filename.suffix.lower().startswith('.fit'):
        result = fitsfile.FitsFile(str(filename)).data
    else:
        result = np.fromfile(str(filename), dtype=float, sep=' ')
    return result


def _constructor_models(loader: PixelLoader, node: yaml.ScalarNode):

    if isinstance(node, yaml.ScalarNode):
        # OK: no kwargs provided
        mapping = {}  # type: dict
    else:
        mapping = loader.construct_mapping(node, deep=True)

    return detection_pipeline.Models(mapping)


def _constructor_function(loader: PixelLoader, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    function_name = mapping['name']                      # type: str
    kwargs = mapping.get('kwargs', {})
    args = mapping.get('args', {})

    func = util.evaluate_reference(function_name)

    return functools.partial(func, *args, **kwargs)


PixelLoader.add_implicit_resolver('!expr', re.compile(r'^.*$'), None)

PixelLoader.add_constructor('!expr', _expr_processor)
PixelLoader.add_constructor('!PROCESSOR', _constructor_processor)

PixelLoader.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PixelLoader.add_constructor('!CMOS_PIPELINE', _constructor_cmos_pipeline)

PixelLoader.add_constructor('!CCD', _constructor_ccd)
PixelLoader.add_constructor('!CMOS', _constructor_cmos)

PixelLoader.add_constructor('!from_file', _constructor_from_file)
PixelLoader.add_constructor('!function', _constructor_function)
PixelLoader.add_constructor('!models', _constructor_models)


def load_stream(stream: t.Union[str, t.IO[str]]):
    """Parse the YAML stream.

    :param stream: stream to parse (str or file-like object)
    :return: object corresponding to YAML document
    """
    return yaml.load(stream, Loader=PixelLoader)


def load_config(yaml_filename: str):
    """Loads a YAML document and converts into an object

    :param yaml_filename: filename of the document
    :return: new object corresponding to YAML document
    """
    with open(yaml_filename, 'r') as stream:
        cfg = load_stream(stream)

    return cfg
