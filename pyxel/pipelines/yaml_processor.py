import functools
import typing as t
from pathlib import Path

import numpy as np
import yaml

from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
import pyxel.detectors.ccd_characteristics
import pyxel.detectors.cmos_characteristics
import pyxel.detectors.geometry
import pyxel.detectors.cmos_geometry
import pyxel.detectors.environment
from pyxel.pipelines import detection_pipeline
from pyxel.util import fitsfile
from pyxel.util import util
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry


class PyxelLoader(yaml.SafeLoader):
    """Custom `SafeLoader` that constructs Pyxel objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature."""


class PyxelDumper(yaml.SafeDumper):
    """Custom `SafeDumper` that represents Pyxel objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature."""


def _constructor_processor(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.Processor(**mapping)

    return obj


def _geometry_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = Geometry(**mapping)
    return obj


def _geometry_representer(dumper: PyxelDumper, obj: Geometry):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    mapping = obj.__getstate__()  # type: dict
    out = dumper.represent_mapping('!geometry', mapping, flow_style=True)
    return out


def _environment_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = Environment(**mapping)
    return obj


def _environment_representer(dumper: PyxelDumper, obj: Environment):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    mapping = obj.__getstate__()  # type: dict
    out = dumper.represent_mapping('!environment', mapping, flow_style=True)
    return out


def _ccd_characteristics_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CCDCharacteristics(**mapping)
    return obj


def _ccd_characteristics_representer(dumper: PyxelDumper, obj: CCDCharacteristics):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    mapping = obj.__getstate__()  # type: dict
    out = dumper.represent_mapping('!ccd_characteristics', mapping, flow_style=True)
    return out


def _constructor_ccd_pipeline(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CCDDetectionPipeline(**mapping)

    return obj


def _constructor_cmos_pipeline(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CMOSDetectionPipeline(**mapping)

    return obj


def _constructor_ccd(loader: PyxelLoader, node: yaml.MappingNode):
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


def _constructor_cmos(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = pyxel.detectors.cmos_geometry.CMOSGeometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = pyxel.detectors.environment.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = pyxel.detectors.cmos_characteristics.CMOSCharacteristics(**mapping['characteristics'])
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


def _constructor_from_file(loader: PyxelLoader, node: yaml.ScalarNode):
    filename = Path(loader.construct_scalar(node))
    if filename.suffix.lower().startswith('.fit'):
        result = fitsfile.FitsFile(str(filename)).data
    else:
        result = np.fromfile(str(filename), dtype=float, sep=' ')
    return result


def _constructor_models(loader: PyxelLoader, node: yaml.ScalarNode):

    if isinstance(node, yaml.ScalarNode):
        # OK: no kwargs provided
        mapping = {}  # type: dict
    else:
        mapping = loader.construct_mapping(node, deep=True)

    return detection_pipeline.Models(mapping)


def _constructor_function(loader: PyxelLoader, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    function_name = mapping['name']                      # type: str
    kwargs = mapping.get('kwargs', {})
    args = mapping.get('args', {})

    func = util.evaluate_reference(function_name)

    return functools.partial(func, *args, **kwargs)


PyxelLoader.add_constructor('!PROCESSOR', _constructor_processor)

PyxelLoader.add_constructor('!geometry', _geometry_constructor)
PyxelDumper.add_representer(Geometry, _geometry_representer)

PyxelLoader.add_constructor('!environment', _environment_constructor)
PyxelDumper.add_representer(Environment, _environment_representer)

PyxelLoader.add_constructor('!ccd_characteristics', _ccd_characteristics_constructor)
PyxelDumper.add_representer(CCDCharacteristics, _ccd_characteristics_representer)

PyxelLoader.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PyxelLoader.add_constructor('!CMOS_PIPELINE', _constructor_cmos_pipeline)

PyxelLoader.add_constructor('!CCD', _constructor_ccd)
PyxelLoader.add_constructor('!CMOS', _constructor_cmos)

PyxelLoader.add_constructor('!from_file', _constructor_from_file)
PyxelLoader.add_constructor('!function', _constructor_function)
PyxelLoader.add_constructor('!models', _constructor_models)


def load(stream: t.Union[str, t.TextIO]):
    """Parse a YAML document.

    :param stream: document to process.
    :return: a python object
    """
    return yaml.load(stream, Loader=PyxelLoader)


def dump(data) -> str:
    """Serialize a Python object into a YAML stream using `PyxelDumper`

    :param data: Object to serialize to YAML.
    :return: the YAML output as a `str`.
    """
    return yaml.dump(data, Dumper=PyxelDumper)


def load_config(yaml_file: str):

    with open(yaml_file, 'r') as file_obj:
        cfg = load(file_obj)

    return cfg
