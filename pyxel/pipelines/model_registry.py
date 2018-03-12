"""TBW."""
import inspect
from collections import OrderedDict

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
        model_def = dict(model_def)  # make copy
        group = model_def.pop('group')
        if group in processor.pipeline.model_groups:
            model_group = processor.pipeline.model_groups[group]
            model = ModelFunction(**model_def)
            model_group.models.append(model)


def create_model_def(func, group='', name=None, enabled=True):
    """Create a model definition by inspecting the callable.

    The dict returned may be passed to the import_model function.

    :param func:
    :param group:
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


class Registry:
    """TBW."""

    __instance = None

    def __new__(cls):
        """Create singleton."""
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        """TBW."""
        if not hasattr(self, '_model_defs'):
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
        for key in self:
            item = self[key]
            if not name or name == item['name'] or name == item['group']:
                import_model(processor, item)

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

    def register(self, func, name=None, group=None, enabled=True):
        """TBW.

        :param func:
        :param name:
        :param group:
        :param enabled:
        """
        if inspect.isclass(func):
            func = func()

        model_def = create_model_def(func, group, name, enabled)

        self[model_def['name']] = model_def

    def decorator(self, group, name=None, enabled=True):
        """Auto register callable class or function using a decorator."""
        def _wrapper(func):
            self.register(func, group=group, name=name, enabled=enabled)
            return func

        return _wrapper


registry = Registry()


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
