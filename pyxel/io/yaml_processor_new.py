"""TBW."""
import typing as t
import yaml
from pathlib import Path

try:
    # Use LibYAML library
    from yaml import CSafeLoader as SafeLoader  # type: ignore
except ImportError:
    from yaml import SafeLoader  # noqa: F401

from pyxel import util
from pyxel.pipelines.parametric import StepValues
from pyxel.pipelines.parametric import ParametricConfig
from pyxel.pipelines.model_group import ModelFunction
from pyxel.pipelines.model_group import ModelGroup


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


def _constructor_model_function(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node)             # type: dict
    model = ModelFunction(**mapping)
    return model


def _constructor_model_group(loader: PyxelLoader, node: yaml.SequenceNode):
    if isinstance(node, yaml.ScalarNode):
        return node.value

    sequence = loader.construct_sequence(node)             # type: list
    model = ModelGroup(sequence)
    return model


def _constructor_object(loader: PyxelLoader, node: yaml.MappingNode):
    if isinstance(node, yaml.ScalarNode):
        result = node.value
    elif isinstance(node, yaml.SequenceNode):
        result = loader.construct_sequence(node, deep=True)
    else:
        result = loader.construct_mapping(node, deep=True)
        if 'class' in result:
            class_name = result.pop('class')
            try:
                klass = util.evaluate_reference(class_name)
                result = klass(**result)
            except TypeError as exc:
                print('Cannot evaluate class: %s' % str(exc))
                return
    return result


def _constructor_class(loader: PyxelLoader, node: yaml.ScalarNode):
    return node.value


def _constructor_parametric(loader: PyxelLoader, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict
    obj = ParametricConfig(**mapping)
    return obj


def _constructor_steps(loader: PyxelLoader, node: yaml.SequenceNode):
    sequence = loader.construct_sequence(node, deep=True)     # type: list
    obj = [StepValues(**kwargs) for kwargs in sequence]
    return obj


PyxelLoader.add_path_resolver('!Class', ['processor', 'class'])
PyxelLoader.add_path_resolver('!Class', ['processor', 'detector', None, 'class'])
PyxelLoader.add_path_resolver('!Class', ['processor', 'detector', 'class'])
# NOTE 1: not called - refer to NOTE 2 below
PyxelLoader.add_path_resolver('!Class', ['processor', 'pipeline', 'class'])
PyxelLoader.add_constructor('!Class', _constructor_class)

PyxelLoader.add_path_resolver('!Object', ['processor'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'detector', None])
PyxelLoader.add_path_resolver('!Object', ['processor', 'detector'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'pipeline'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'pipeline', None])
PyxelLoader.add_constructor('!Object', _constructor_object)


PyxelLoader.add_path_resolver('!ParametricConfig', ['parametric'])
PyxelLoader.add_constructor('!ParametricConfig', _constructor_parametric)

PyxelLoader.add_path_resolver('!StepValues', ['parametric', 'steps'])
PyxelLoader.add_constructor('!StepValues', _constructor_steps)

# NOTE 2: overrides the : 'processor', 'pipeline', 'class'
PyxelLoader.add_path_resolver('!ModelGroup', ['processor', 'pipeline', None])
PyxelLoader.add_constructor('!ModelGroup', _constructor_model_group)

PyxelLoader.add_path_resolver('!Model', ['processor', 'pipeline', None, None])
PyxelLoader.add_constructor('!Model', _constructor_model_function)


def load(stream: t.Union[str, t.IO]):
    """Parse a YAML document.

    :param stream: document to process.
    :return: a python object
    """
    return yaml.load(stream, Loader=PyxelLoader)


def load_config(yaml_filename: Path):
    """Load the YAML configuration file.

    :param yaml_filename:
    :return:
    """
    with yaml_filename.open('r') as file_obj:
        cfg = load(file_obj)

    return cfg


def dump(cfg_obj) -> str:
    """Serialize a Python object into a YAML stream.

    :param cfg_obj: Object to serialize to YAML.
    :return: the YAML output as a `str`.
    """
    cfg_map = util.get_state_dict(cfg_obj)

    keys = [
        'processor.detector',
        'processor.detector.geometry',
        'processor.detector.environment',
        'processor.detector.characteristics',
        'processor.pipeline',
    ]
    for key in keys:
        cfg_map_val = util.get_value(cfg_map, key)
        cfg_obj_val = util.get_value(cfg_obj, key)
        cfg_map_val['class'] = cfg_obj_val.__module__ + '.' + cfg_obj_val.__class__.__name__

    result = yaml.dump(cfg_map, default_flow_style=False)
    return result
