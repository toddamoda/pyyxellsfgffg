#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t
from pathlib import Path

import yaml

from ..evaluator import evaluate_reference


try:
    # Use LibYAML library
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader  # type: ignore   # noqa


"""TBW."""

__all__ = ["load", "ObjectModelLoader"]


class ObjectModelLoader(yaml.SafeLoader):
    """Custom `SafeLoader` that constructs Pyxel objects.

    This class is not directly instantiated by user code, but instead is
    used to maintain the available constructor functions that are
    called when parsing a YAML stream.  See the `PyYaml documentation
    <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
    class signature.
    """

    class_paths = []  # type: t.List[t.List[str]]

    @classmethod
    def add_class(cls, klass: type, paths: list, is_list: bool = False) -> None:
        """TBW.

        :param klass:
        :param paths:
        :param is_list:
        :return:
        """
        ClassConstructor(cls, klass, paths, is_list)

    @classmethod
    def add_class_ref(cls, path_to_class: list) -> None:
        """TBW.

        :param path_to_class:
        :return:
        """
        if path_to_class not in cls.class_paths:
            cls.class_paths.append(path_to_class)

        path_to_obj = path_to_class[:-1]

        cls.add_path_resolver("!Class", path_to_class)
        cls.add_path_resolver("!Object", path_to_obj)

        cls.add_constructor("!Class", _constructor_class)
        cls.add_constructor("!Object", _constructor_object)


#
# class ObjectModelDumper(yaml.SafeDumper):
#     """Custom `SafeDumper` that represents Pyxel objects.
#
#     This class is not directly instantiated by user code, but instead is
#     used to maintain the available constructor functions that are
#     called when parsing a YAML stream.  See the `PyYaml documentation
#     <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ for details of the
#     class signature.
#     """


def _constructor_object(loader: ObjectModelLoader, node: yaml.Node) -> t.Any:
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    if isinstance(node, yaml.ScalarNode):
        result = node.value
    elif isinstance(node, yaml.SequenceNode):
        result = loader.construct_sequence(node, deep=True)
    else:
        result = loader.construct_mapping(node, deep=True)
        if "class" in result:
            class_name = result.pop("class")
            try:
                klass = evaluate_reference(class_name)
                result = klass(**result)
            except TypeError as exc:
                print("Cannot evaluate class: %s" % str(exc))
                return
    return result


def _constructor_class(loader: ObjectModelLoader, node: yaml.ScalarNode) -> t.Any:
    """TBW.

    :param loader:
    :param node:
    :return:
    """
    return node.value


class ClassConstructor:
    """TBW."""

    def __init__(
        self,
        loader: t.Type[yaml.SafeLoader],
        klass: type,
        paths: t.List[str],
        is_list: bool = False,
    ) -> None:
        """TBW.

        :param klass:
        :param paths:
        :param is_list:
        """
        loader.add_path_resolver("!%s" % klass.__name__, paths)
        loader.add_constructor("!%s" % klass.__name__, self.__call__)
        self.klass = klass
        self.paths = paths
        self.is_list = is_list

    def __call__(self, loader, node) -> t.Union[list, dict, t.Any]:
        """TBW.

        :param loader:
        :param node:
        :return:
        """
        if isinstance(node, yaml.ScalarNode):
            obj = node.value

        elif isinstance(node, yaml.SequenceNode):
            lst = loader.construct_sequence(node, deep=True)  # type: t.List
            if self.is_list:
                obj = [self.klass(**kwargs) for kwargs in lst]
            else:
                obj = self.klass(lst)

        elif isinstance(node, yaml.MappingNode):
            dct = loader.construct_mapping(node, deep=True)
            obj = self.klass(**dct)

        else:
            raise RuntimeError("Invalid node: %r" % node)

        return obj


def load(yaml_file: t.Union[str, Path]) -> t.Any:
    """Load YAML file.

    :param yaml_file:
    :return:
    """
    if isinstance(yaml_file, str):
        with Path(yaml_file).open("r") as file_obj:
            return load_yaml(file_obj)
    else:
        with yaml_file.open("r") as file_obj:
            return load_yaml(file_obj)


def load_yaml(stream: t.Union[str, t.IO]) -> t.Any:
    """Load a YAML document.

    :param stream: document to process.
    :return: a python object
    """
    result = yaml.load(stream, Loader=ObjectModelLoader)
    return result


# def dump(cfg_obj) -> str:
#     """Serialize a Python object into a YAML stream.
#
#     :param cfg_obj: Object to serialize to YAML.
#     :return: the YAML output as a `str`.
#     """
#     cfg_map = get_state_dict(cfg_obj)
#
#     class_name = ''
#     keys = []
#     for paths in ObjectModelLoader.class_paths:
#         class_name = paths[-1]
#         key = '.'.join([str(path) for path in paths[:-1]])
#         if '.None' in key:
#             none_key = key.split('.None')[0]
#             cfg_map_val = get_value(cfg_map, none_key)
#             att_keys = cfg_map_val.keys()
#             for att_key in att_keys:
#                 keys.append(key.replace('None', att_key))
#         else:
#             keys.append(key)
#
#     for key in keys:
#         cfg_map_val = get_value(cfg_map, key)
#         cfg_obj_val = get_value(cfg_obj, key)
#         cfg_map_val[class_name] = cfg_obj_val.__module__ + '.' + cfg_obj_val.__class__.__name__
#
#     result = yaml.dump(cfg_map, default_flow_style=False)
#     return result


# def define_pyxel_loader():
#     """TBW."""
#     from pyxel.pipelines.parametric import StepValues
#     from pyxel.pipelines.parametric import ParametricConfig
#     from pyxel.pipelines.model_group import ModelFunction
#     from pyxel.pipelines.model_group import ModelGroup
#
#     ObjectModelLoader.add_class_ref(['processor', 'class'])
#     ObjectModelLoader.add_class_ref(['processor', 'detector', 'class'])
#     ObjectModelLoader.add_class_ref(['processor', 'detector', None, 'class'])
#     ObjectModelLoader.add_class_ref(['processor', 'pipeline', 'class'])
#
#     ObjectModelLoader.add_class(ParametricConfig, ['parametric'])
#     ObjectModelLoader.add_class(StepValues, ['parametric', 'steps'], is_list=True)
#     ObjectModelLoader.add_class(ModelGroup, ['processor', 'pipeline', None])
#     ObjectModelLoader.add_class(ModelFunction, ['processor', 'pipeline', None, None])
#
#
# define_pyxel_loader()
