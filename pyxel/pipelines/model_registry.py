"""TBW."""
import inspect
import logging
from collections import OrderedDict
import typing as t  # noqa: F401

import yaml

from pyxel import util
# from pyxel.pipelines.model_group import ModelFunction
# from pyxel import Processor
# from pyxel import ModelFunction
from pyxel.detectors.detector import Detector
from pyxel.pipelines.processor import Processor
from pyxel.pipelines.model_group import ModelFunction


EXAMPLE_MODEL_YAML = """
    group: charge_generation
    name: my_model_name
    enabled: false
    func: pyxel.models.ccd_noise.add_output_node_noise
    arguments:
          std_deviation: 1.0
"""

EXAMPLE_MODEL_DICT = {
    'name': 'my_model_name',
    'group': 'charge_generation',
    'enabled': False,
    'func': 'pyxel.models.ccd_noise.add_output_node_noise',
    'arguments': {'std_deviation': 1.0}
}


def import_model(processor, model_def):
    """Dynamically import a model definition.

    :param processor:
    :param model_def:
    """
    import yaml
    if isinstance(model_def, str):
        model_def = yaml.load(model_def)

    if isinstance(model_def, list):
        for model_def_i in model_def:
            import_model(processor, model_def_i)
        return

    if isinstance(model_def, dict):
        # model_def = dict(model_def)  # make copy
        group = model_def['group']
        if group in processor.pipeline.model_groups:
            model_group = processor.pipeline.model_groups[group]
            model = ModelFunction(name=model_def['name'],
                                  func=model_def['func'],
                                  arguments=model_def.get('arguments'),
                                  enabled=model_def.get('enabled', True))
            model_group.models.append(model)


def create_model_def(func, group='', name=None, enabled=True, detector=None, gui=None):
    """Create a model definition by inspecting the callable.

    The dict returned may be passed to the import_model function.

    :param func:
    :param group:
    :param name:
    :param enabled:
    :param detector:
    :param gui:
    :return:
    """
    if isinstance(func, str):
        func = util.evaluate_reference(func)
        if inspect.isclass(func):
            func = func()

    if inspect.isfunction(func):
        spec = inspect.getfullargspec(func)
        default_name = func.__name__
        module_path = func.__module__

    elif hasattr(func, '__call__'):
        spec = inspect.getfullargspec(func.__call__)
        default_name = func.__class__.__name__
        module_path = func.__class__.__module__
    else:
        raise RuntimeError('Cannot create model definition for: %r' % func)

    if spec.defaults is not None:
        start = len(spec.args) - len(spec.defaults)
        values = dict(zip(spec.args[start:], spec.defaults))
    else:
        values = {}

    arguments = {}
    for arg in spec.args:
        if arg == 'self':
            continue
        if arg in spec.annotations and isinstance(spec.annotations[arg], Detector):
            continue
        # NOTE: the if statement above is better (if an annotation is provided)
        # else the argument name 'detector' is to become a keyword.
        if arg == 'detector':
            continue
        if arg in values:
            value = values[arg]
        else:
            value = None
        arguments[arg] = value

    if not name:
        name = default_name

    model_def = {
        'name': name,
        'group': group,
        'enabled': enabled,
        'func': module_path + '.' + default_name,
        'arguments': arguments
    }

    if detector:
        model_def['type'] = detector

    if gui:
        model_def['gui'] = gui

    return model_def


class LateBind:
    """TBW."""

    def __init__(self, func, *args):
        """TBW.

        :param func:
        :param args:
        """
        self.func = func
        self.args = args

    def __call__(self):
        """TBW."""
        return self.func(*self.args)


class EntryTypes:
    """Collection of generic GUI entry types."""

    num_uint = {
        'tag': 'input',
        'type': 'number',
        'step': 1,
        'min': 0,
        'max': 65536
    }


class Registry:
    """TBW."""

    __instance = None

    entry = EntryTypes()

    def __new__(cls, singleton=True):
        """Create singleton."""
        if singleton:
            if cls.__instance is None:
                cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return object.__new__(cls)

    def __init__(self, singleton=True):
        """TBW."""
        self._log = logging.getLogger(__name__)
        if singleton:
            if not hasattr(self, '_model_defs'):
                self._model_defs = OrderedDict()
        else:
            self._model_defs = OrderedDict()

    def __iter__(self):
        """TBW."""
        return iter(self._model_defs)

    def __len__(self):
        """TBW."""
        return len(self._model_defs)

    def __setitem__(self, item, value):
        """TBW.

        :param key:
        :param item:
        :return:
        """
        self._model_defs[item] = value

    def __getitem__(self, item):
        """TBW.

        :param item:
        :return:
        """
        value = self._model_defs[item]
        if isinstance(value, LateBind):
            value = value()
        return value

    def clear(self):
        """TBW."""
        self._model_defs.clear()

    def get_group(self, detector, group=None):
        """TBW.

        :param detector:
        :param group:
        :return:
        """
        result = []
        for item in self.values():
            item_detector = item.get('type', '')
            if item_detector and detector not in item_detector:
                continue
            if group and item['group'] != group:
                continue
            result.append(item)
        return result

    def values(self):
        """TBW."""
        return [value for key, value in self.items()]

    def items(self):
        """TBW."""
        keys = list(self._model_defs.keys())
        for key in keys:
            # convert any LateBind values to a dictionary and save it
            self._model_defs[key] = self[key]

        return self._model_defs.items()

    def import_models(self, processor: Processor, name: str=None):
        """TBW.

        :param processor:
        :param name: group or model name
        """
        items = self.get_group(processor.pipeline.name)
        for item in items:
            if not name or name == item['name'] or name == item['group']:
                try:
                    import_model(processor, item)
                except Exception as exc:
                    self._log.error('Cannot import: %r', item)
                    self._log.exception(exc)

    def save(self, file_path):
        """TBW.

        :param file_path:
        """
        cfg = list(self.values())
        content = yaml.dump(cfg, default_flow_style=False)
        with open(file_path, 'w') as fd:
            fd.write(content)

    def register_map(self, def_dict, processor_type=None):
        """Add multiple models based on a dictionary of groups."""
        for group, model_list in def_dict.items():
            for model_def in model_list:
                func = model_def['func']
                mtype = model_def.get('type')
                name = model_def.get('name')
                enabled = model_def.get('enabled', True)
                if processor_type and mtype:
                    if processor_type not in mtype:
                        continue  # skip the registration for this model
                self.register(func, name=name, group=group, enabled=enabled)

    def register(self, func, name=None, group=None, enabled=True, detector=None, gui=None):
        """TBW.

        :param func:
        :param name:
        :param group:
        :param enabled:
        :param detector:
        """
        if inspect.isclass(func):
            func = func()

        model_def = create_model_def(func, group, name, enabled, detector, gui)

        self[model_def['name']] = model_def

    def decorator(self, group, name=None, enabled=True, detector=None, gui=None):
        """Auto register callable class or function using a decorator."""
        def _wrapper(func):
            self.register(func, group=group, name=name, enabled=enabled, detector=detector, gui=gui)
            return func

        return _wrapper


registry = Registry()

parameters = {}  # type: t.Dict[str, t.Dict[str, t.Any]]


def register(name=None, group=None, enabled=True, detector=None, gui=None):
    """TBW."""
    """Auto register callable class or function using a decorator."""

    def _wrapper(func):
        registry.register(func, group=group, name=name, enabled=enabled, detector=detector, gui=gui)
        return func

    return _wrapper


def argument(name, **kwargs):
    """TBW."""
    def _register(func):
        """TBW."""
        func_id = func.__module__ + '.' + func.__name__
        if func_id not in parameters:
            parameters[func_id] = {}
        param = dict(kwargs)
        parameters[func_id][name] = param
        return func

    return _register


class ValidationError(Exception):
    """Exception thrown by the argument validate function."""


def validate(func):
    """TBW."""
    def _validate(*args, **kwargs):
        """TBW."""
        func_id = func.__module__ + '.' + func.__name__
        spec = inspect.getfullargspec(func)
        params = parameters[func_id]

        if spec.defaults is not None:
            start = len(spec.args) - len(spec.defaults)
            default_values = dict(zip(spec.args[start:], spec.defaults))
        else:
            default_values = {}

        for i, name in enumerate(spec.args):
            if name in params:
                value = None
                if name in default_values:
                    value = default_values[name]

                if name in kwargs:
                    value = kwargs[name]
                elif i < len(args):
                    value = args[i]
                param = params[name]
                if 'validate' in param:
                    if not param['validate'](value):
                        msg = 'Validation failed for: model: %s, argument: %s, value: %r' % (func_id, name, value)
                        raise ValidationError(msg)

        return func(*args, **kwargs)

    return _validate


class MetaModel(type):
    """Meta-class that auto registers a model class."""

    # reference: stackoverflow question 13762231
    @classmethod
    def __prepare__(cls, class_name, bases, **kwargs):
        """TBW."""
        return super().__prepare__(class_name, bases, **kwargs)

    def __new__(cls, class_name, bases, namespace, **kwargs):
        """TBW."""
        return super().__new__(cls, class_name, bases, namespace)

    def __init__(self, class_name, bases, namespace, **kwargs):
        """TBW."""
        super().__init__(class_name, bases, namespace)
        # global registry
        name = kwargs.get('name', class_name)
        group = kwargs.get('group', '')
        func = namespace['__module__'] + '.' + class_name
        registry[name] = LateBind(create_model_def, func, group, name)
