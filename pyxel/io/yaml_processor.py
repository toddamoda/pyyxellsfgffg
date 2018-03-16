"""TBW."""
import inspect
import re
import typing as t
from pathlib import Path

import numpy as np
import yaml
from astropy.io import fits

import pyxel.pipelines.ccd_pipeline
import pyxel.pipelines.cmos_pipeline
import pyxel.pipelines.models
import pyxel.pipelines.processor

try:
    # Use LibYAML library
    from yaml import CSafeLoader as SafeLoader  # type: ignore
except ImportError:
    from yaml import SafeLoader  # noqa: F401

from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.cmos_characteristics import CMOSCharacteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.cmos_geometry import CMOSGeometry
from pyxel.pipelines.models import Model
from pyxel.pipelines.parametric import ParametricConfig
from pyxel.pipelines.parametric import StepValues


class PyxelLoader(yaml.SafeLoader):
    """Custom `SafeLoader` that constructs Pyxel objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature.
    """


class PyxelDumper(yaml.SafeDumper):
    """Custom `SafeDumper` that represents Pyxel objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature.
    """


def _expr_processor(loader: PyxelLoader, node: yaml.ScalarNode):
    value = loader.construct_scalar(node)

    try:
        result = eval(value, {}, np.__dict__)

        if callable(result) or inspect.ismodule(result):
            result = value

    except NameError:
        result = value

    return result


def _constructor_parametric(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict
    obj = ParametricConfig(**mapping)

    return obj


def _constructor_steps(loader: PyxelLoader, node: yaml.SequenceNode):
    sequence = loader.construct_sequence(node, deep=True)     # type: list
    obj = [StepValues(**kwargs) for kwargs in sequence]

    return obj


def _constructor_processor(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict
    obj = pyxel.pipelines.processor.Processor(**mapping)

    return obj


def _ccd_geometry_constructor(loader: PyxelLoader, node: yaml.MappingNode) -> CCDGeometry:
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CCDGeometry(**mapping)
    return obj


def _ccd_geometry_representer(dumper: PyxelDumper, obj: CCDGeometry):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!ccd_geometry', data=obj, cls=None, flow_style=False)


def _cmos_geometry_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CMOSGeometry(**mapping)
    return obj


def _cmos_geometry_representer(dumper: PyxelDumper, obj: CMOSGeometry):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!cmos_geometry', data=obj, cls=None, flow_style=False)


def _environment_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    # error: Too many arguments for "Environment"
    obj = Environment(**mapping)  # type: ignore
    return obj


def _environment_representer(dumper: PyxelDumper, obj: Environment):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!environment', data=obj, cls=None, flow_style=False)


def _ccd_characteristics_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CCDCharacteristics(**mapping)
    return obj


def _cmos_characteristics_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CMOSCharacteristics(**mapping)
    return obj


def _ccd_characteristics_representer(dumper: PyxelDumper, obj: CCDCharacteristics):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!ccd_characteristics', data=obj, cls=None, flow_style=False)


def _cmos_characteristics_representer(dumper: PyxelDumper, obj: CCDCharacteristics):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!cmos_characteristics', data=obj, cls=None, flow_style=False)


def _constructor_ccd_pipeline(loader: PyxelLoader,
                              node: yaml.MappingNode) -> pyxel.pipelines.ccd_pipeline.CCDDetectionPipeline:

    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = pyxel.pipelines.ccd_pipeline.CCDDetectionPipeline(**mapping)

    return obj


def _constructor_cmos_pipeline(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = pyxel.pipelines.cmos_pipeline.CMOSDetectionPipeline(**mapping)

    return obj


def _ccd_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CCD(**mapping)
    return obj


def _cmos_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    obj = CMOS(**mapping)
    return obj


def _ccd_representer(dumper: PyxelDumper, obj: CCD):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!CCD', data=obj, cls=None, flow_style=False)


def _cmos_representer(dumper: PyxelDumper, obj: CMOS):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!CMOS', data=obj, cls=None, flow_style=False)


def _constructor_from_file(loader: PyxelLoader, node: yaml.ScalarNode):
    filename = Path(loader.construct_scalar(node))
    if filename.suffix.lower().startswith('.fit'):
        result = fits.getdata(str(filename))
    else:
        result = np.fromfile(str(filename), dtype=float, sep=' ')
    return result


def _constructor_models(loader: PyxelLoader, node: yaml.ScalarNode):
    if isinstance(node, yaml.ScalarNode):
        # OK: no kwargs provided
        mapping = {}  # type: dict
    else:
        mapping = loader.construct_mapping(node, deep=True)

    return pyxel.pipelines.models.Models(mapping)


def _model_constructor(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node)             # type: dict
    model = Model(**mapping)
    return model


def _model_representer(dumper: PyxelDumper, obj: Model):
    """TBW.

    :param dumper:
    :param obj:
    :return:
    """
    return dumper.represent_yaml_object('!model', data=obj, cls=None, flow_style=False)


PyxelLoader.add_implicit_resolver('!expr', re.compile(r'^.*$'), None)
PyxelLoader.add_constructor('!expr', _expr_processor)

PyxelLoader.add_path_resolver('!PARAMETRIC', ['parametric'])
PyxelLoader.add_constructor('!PARAMETRIC', _constructor_parametric)

PyxelLoader.add_path_resolver('!steps', ['parametric', 'steps'])
PyxelLoader.add_constructor('!steps', _constructor_steps)

PyxelLoader.add_path_resolver('!PROCESSOR', ['cmos_process'])
PyxelLoader.add_path_resolver('!PROCESSOR', ['ccd_process'])
PyxelLoader.add_constructor('!PROCESSOR', _constructor_processor)

PyxelLoader.add_path_resolver('!ccd_geometry', ['ccd_process', 'detector', 'geometry'])
PyxelLoader.add_constructor('!ccd_geometry', _ccd_geometry_constructor)
PyxelDumper.add_representer(CCDGeometry, _ccd_geometry_representer)

PyxelLoader.add_path_resolver('!cmos_geometry', ['cmos_process', 'detector', 'geometry'])
PyxelLoader.add_constructor('!cmos_geometry', _cmos_geometry_constructor)
PyxelDumper.add_representer(CMOSGeometry, _cmos_geometry_representer)

PyxelLoader.add_path_resolver('!environment', ['ccd_process', 'detector', 'environment'])
PyxelLoader.add_path_resolver('!environment', ['cmos_process', 'detector', 'environment'])
PyxelLoader.add_constructor('!environment', _environment_constructor)
PyxelDumper.add_representer(Environment, _environment_representer)

PyxelLoader.add_path_resolver('!ccd_characteristics', ['ccd_process', 'detector', 'characteristics'])
PyxelLoader.add_constructor('!ccd_characteristics', _ccd_characteristics_constructor)
PyxelDumper.add_representer(CCDCharacteristics, _ccd_characteristics_representer)

PyxelLoader.add_path_resolver('!cmos_characteristics', ['cmos_process', 'detector', 'characteristics'])
PyxelLoader.add_constructor('!cmos_characteristics', _cmos_characteristics_constructor)
PyxelDumper.add_representer(CMOSCharacteristics, _cmos_characteristics_representer)

PyxelLoader.add_path_resolver('!CCD_PIPELINE', ['ccd_process', 'pipeline'])
PyxelLoader.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PyxelLoader.add_path_resolver('!CMOS_PIPELINE', ['cmos_process', 'pipeline'])
PyxelLoader.add_constructor('!CMOS_PIPELINE', _constructor_cmos_pipeline)

PyxelLoader.add_path_resolver('!CCD', ['ccd_process', 'detector'])
PyxelLoader.add_constructor('!CCD', _ccd_constructor)
PyxelDumper.add_representer(CCD, _ccd_representer)

PyxelLoader.add_path_resolver('!CMOS', ['cmos_process', 'detector'])
PyxelLoader.add_constructor('!CMOS', _cmos_constructor)
PyxelDumper.add_representer(CMOS, _cmos_representer)

PyxelLoader.add_path_resolver('!model', ['ccd_process', 'pipeline', None, None])
PyxelLoader.add_path_resolver('!model', ['cmos_process', 'pipeline', None, None])
PyxelLoader.add_constructor('!model', _model_constructor)
PyxelDumper.add_representer(Model, _model_representer)

PyxelLoader.add_constructor('!from_file', _constructor_from_file)

PyxelLoader.add_path_resolver('!models', ['ccd_process', 'pipeline', None])
PyxelLoader.add_path_resolver('!models', ['cmos_process', 'pipeline', None])
PyxelLoader.add_constructor('!models', _constructor_models)
# TODO: Implement add_representer for '!models'

yaml.add_path_resolver('!ccd_geometry', path=['geometry'], kind=dict, Loader=PyxelLoader)
yaml.add_path_resolver('!ccd_characteristics', path=['characteristics'], kind=dict, Loader=PyxelLoader)
yaml.add_path_resolver('!environment', path=['environment'], kind=dict, Loader=PyxelLoader)
yaml.add_path_resolver('!cmos_geometry', path=['geometry'], kind=dict, Loader=PyxelLoader)
yaml.add_path_resolver('!cmos_characteristics', path=['characteristics'], kind=dict, Loader=PyxelLoader)


def load(stream: t.Union[str, t.IO]):
    """Parse a YAML document.

    :param stream: document to process.
    :return: a python object
    """
    return yaml.load(stream, Loader=PyxelLoader)


def dump(data) -> str:
    """Serialize a Python object into a YAML stream using `PyxelDumper`.

    :param data: Object to serialize to YAML.
    :return: the YAML output as a `str`.
    """
    return yaml.dump(data, Dumper=PyxelDumper)


def load_config(yaml_filename: Path):
    """Load the YAML configuration file.

    :param yaml_filename:
    :return:
    """
    with yaml_filename.open('r') as file_obj:
        cfg = load(file_obj)

    return cfg
