import yaml
import functools
import typing as t  # noqa: F401
from pathlib import Path

try:
    # Use LibYAML library
    from yaml import CSafeLoader as SafeLoader  # type: ignore
except ImportError:
    from yaml import SafeLoader  # noqa: F401

from pyxel import util
from pyxel.pipelines.parametric import StepValues
from pyxel.pipelines.parametric import ParametricConfig

CWD = Path(__file__).parent.parent


class ModelFunction:
    """TBW."""

    def __init__(self, name: str, func: str, arguments: dict = None, enabled: bool = True) -> None:
        """TBW.

        :param name:
        :param enabled:
        :param arguments:
        """
        if arguments is None:
            arguments = {}
        self.func = func
        self.name = name
        self.enabled = enabled
        self.arguments = arguments

    def copy(self):
        """TBW."""
        # kwargs = {key: type(value)(value) for key, value in self.__getstate__().items()}
        return ModelFunction(**util.copy_state(self))

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'name': self.name,
            'func': self.func,
            'enabled': self.enabled,
            'arguments': self.arguments
        }

    @property
    def function(self):
        """TBW."""
        func_ref = util.evaluate_reference(self.function)
        func = functools.partial(func_ref, **self.arguments)
        return func


class ModelGroup:
    """TBW."""

    def __init__(self, models: t.List[ModelFunction]) -> None:
        """TBW.

        :param models:
        """
        self.models = models    # type: t.List[ModelFunction]

    def copy(self):
        """TBW."""
        models = {key: model.copy() for key, model in self.models.items()}
        return ModelGroup(models=models)

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'models': self.models
        }

    def __getattr__(self, item):
        """TBW."""
        if item in self.models:
            return self.models[item]
        return super().__getattr__(item)



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


PyxelLoader.add_path_resolver('!ParametricConfig', ['parametric'])
PyxelLoader.add_constructor('!ParametricConfig', _constructor_parametric)

PyxelLoader.add_path_resolver('!StepValues', ['parametric', 'steps'])
PyxelLoader.add_constructor('!StepValues', _constructor_steps)


PyxelLoader.add_path_resolver('!Class', ['processor', 'class'])
PyxelLoader.add_path_resolver('!Class', ['processor', 'detector', None, 'class'])
PyxelLoader.add_path_resolver('!Class', ['processor', 'detector', 'class'])
PyxelLoader.add_path_resolver('!Class', ['processor', 'pipeline', 'class'])
PyxelLoader.add_constructor('!Class', _constructor_class)

PyxelLoader.add_path_resolver('!Object', ['processor'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'detector', None])
PyxelLoader.add_path_resolver('!Object', ['processor', 'detector'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'pipeline'])
PyxelLoader.add_path_resolver('!Object', ['processor', 'pipeline', None])
PyxelLoader.add_constructor('!Object', _constructor_object)

PyxelLoader.add_path_resolver('!Model', ['processor', 'pipeline', None, None])
PyxelLoader.add_constructor('!Model', _constructor_model_function)


def test_yaml_new():
    yaml_file = CWD.joinpath('data', 'test_yaml_new.yaml')
    with open(str(yaml_file)) as file_obj:
        cfg = yaml.load(file_obj, Loader=PyxelLoader)

    print(cfg)
    cfg_dict = util.get_state_dict(cfg)

    def set_class_name(obj_dict, obj_model, key):
        obj_dict_val = util.get_value(obj_dict, key)
        obj_model_val = util.get_value(obj_model, key)
        obj_dict_val['class'] = obj_model_val.__module__ + '.' + obj_model_val.__class__.__name__

    set_class_name(cfg_dict, cfg, 'processor.detector')
    set_class_name(cfg_dict, cfg, 'processor.detector.geometry')
    set_class_name(cfg_dict, cfg, 'processor.detector.environment')
    set_class_name(cfg_dict, cfg, 'processor.detector.characteristics')
    set_class_name(cfg_dict, cfg, 'processor.pipeline')

    result = yaml.dump(cfg_dict, default_flow_style=False)
    print(result)


if __name__ == '__main__':
    test_yaml_new()


# cfg = load in a template yaml file
# pipeline = get referecnce to DetectionPipeline instance
# construct many ModelFunctions (or existing)
# ModelFunction(name, func, arg, tec)
# pipeline.charge_generation.add_model(xxxx)
# pipeline.charge_generation.add_model(yyyy)
# pipeline.photon_generation.add_model(xxxz)
# ..
# ..
# yaml.dump(cfg) = >save to yaml file => DONE!
