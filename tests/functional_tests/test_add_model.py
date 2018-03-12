from pathlib import Path
import inspect

import yaml
import sys
from pyxel import util
from pyxel.io.yaml_processor_new import load_config
from pyxel.io.yaml_processor_new import dump
from pyxel.pipelines.model_registry import import_model
from pyxel.pipelines.model_registry import create_model_def
from pyxel.pipelines.model_group import ModelFunction
# from pyxel.pipelines.model_group import ModelRegistry
from pyxel.detectors.detector import Detector
from pyxel import registry


CWD = Path(__file__).parent.parent
sys.path.append(str(CWD))


from functional_tests import my_models


my_model_def_yaml = """
    group: charge_generation
    name: my_model
    enabled: True
    func: functional_tests.test_add_model.my_model
    arguments:
          level: 5.0
"""

my_model_def_dict = {
    'group': 'charge_generation',
    'name': 'my_model',
    'enabled': True,
    'func': 'functional_tests.test_add_model.my_model',
    'arguments': {
        'level': 7.5
    }
}


def my_model(detector, level):
    # set a new attribute so it can be checked later
    setattr(detector, 'level', level)  # NOTE: this is purely for testing
    return detector


def my_other_model(detector: Detector, level: int, noise: float=2.0):
    # set a new attribute so it can be checked later
    setattr(detector, 'level', level)
    setattr(detector, 'noise', noise)
    return detector


def test_add_model():
    cfg = load_config(Path(CWD, 'data', 'test_yaml_new.yaml'))
    processor = cfg['processor']
    pipeline = processor.pipeline
    detector = processor.detector
    pipeline.set_model_enabled('*', False)

    # test that all models are disabled
    detector = pipeline.run(detector)
    assert detector.signal.sum() == 0.0

    # add a new model and call it
    new_model = ModelFunction('my_model', 'functional_tests.test_add_model.my_model',
                              arguments={'level': 1.5})
    pipeline.model_groups['charge_generation'].models.append(new_model)
    detector = pipeline.run(detector)
    assert detector.level == 1.5

    # add a new model using a function
    pipeline.model_groups['charge_generation'].models.clear()
    new_model = ModelFunction('my_model', my_model,
                              arguments={'level': 2.5})
    pipeline.model_groups['charge_generation'].models.append(new_model)
    detector = pipeline.run(detector)
    assert detector.level == 2.5

    # add a new model using the import functionality
    pipeline.model_groups['charge_generation'].models.clear()
    import_model(processor, my_model_def_yaml)
    detector = pipeline.run(detector)
    assert detector.level == 5.0

    # add a new model using the import functionality
    pipeline.model_groups['charge_generation'].models.clear()
    import_model(processor, my_model_def_dict)
    detector = pipeline.run(detector)
    assert detector.level == 7.5

    # remove all models from the pipeline
    for model_group in pipeline.model_groups.values():
        model_group.models.clear()

    # create a model through inspection
    model_def = create_model_def(my_other_model, 'charge_generation')
    model_def['arguments']['level'] = 10.0
    import_model(processor, model_def)
    detector = pipeline.run(detector)
    assert detector.level == 10.0
    assert detector.noise == 2.0

    # create a model definition using a callable class
    model_def = create_model_def(my_models.MyClassModel(), 'charge_generation')
    model_def['arguments']['level'] = 12.0
    import_model(processor, model_def)
    detector = pipeline.run(detector)
    assert detector.level == 12.0
    assert detector.noise == 2.0
    dump(cfg)


def test_model_registry():

    assert 'my_other_class_model' in registry
    assert 'my_class_model' in registry
    assert len(registry) == 5

    model_def = registry['my_class_model']
    assert isinstance(model_def, dict)
    for name, model_def in registry.items():
        assert isinstance(model_def, dict)


def test_model_registry_decorator():
    # my_models.my_decorated_function(None)
    ref = util.evaluate_reference('functional_tests.my_models.my_decorated_function')
    cfg = load_config(Path(CWD, 'data', 'test_yaml_new.yaml'))
    processor = cfg['processor']

    # remove all models from the pipeline
    for model_group in processor.pipeline.model_groups.values():
        model_group.models.clear()

    # import all model definitions into the processor
    for name in registry:
        model_def = registry[name]
        import_model(processor, model_def)

    # 'my_class_model'
    # 'my_other_class_model'
    # 'my_function_model'
    # 'my_dec_model_class'
    # 'my_dec_model_func'
    processor.pipeline.set_model_enabled('*', False)
    processor.pipeline.set_model_enabled('my_dec_model_class', True)
    processor.pipeline.set_model_enabled('my_dec_model_func', True)
    detector = processor.pipeline.run(processor.detector)
    assert detector.class_std == 1.0
    assert detector.func_std == 2.0


def test_model_registry_map():
    group_models = my_models.registry_map
    registry.register_map(group_models)


def test_pipeline_import():
    cfg = load_config(Path(CWD, 'data', 'test_yaml_new.yaml'))
    processor = cfg['processor']

    # remove all models from the pipeline
    for model_group in processor.pipeline.model_groups.values():
        model_group.models.clear()

    registry.import_models(processor)
    processor.set('pipeline.charge_generation.my_class_model.arguments.level', 1.0)
    processor.set('pipeline.charge_generation.my_function_model.arguments.level', 2.0)
    processor.set('pipeline.charge_generation.my_other_class_model.arguments.std', 3.0)

    processor.pipeline.run(processor.detector)

    value = processor.get('pipeline.charge_generation.my_other_class_model.arguments.std')
    assert processor.detector.std == value
    assert processor.detector.std == 3.0

    assert processor.detector.level == 2.0

    processor.pipeline.set_model_enabled('my_function_model', False)
    processor.pipeline.run(processor.detector)
    assert processor.detector.level == 1.0

    print(dump(cfg))

#
# if __name__ == '__main__':
#     test_add_model()
#     test_model_registry()
#     test_pipeline_import()
#     test_model_registry_decorator()
#     test_model_registry_map()

#
#
# import old_non_pyxel_models
#
# # __FOO__ = []
#
#
# def decorator_new(self, group, name=None, enabled=True):
#     """Auto register callable class or function using a decorator."""
#
#     def _wrapper(func):
#         self.register(func, group=group, name=name, enabled=enabled)
#
#
#         return func
#
#     return _wrapper
#
#
# @decorator_new(group='new_group', name='a_name')
# def pyxel_model_call(detector):
#     result = old_non_pyxel_models.some_model(detector.rows, detector.cols, ...)
#     detector.add_signal(result)
#     return detector

