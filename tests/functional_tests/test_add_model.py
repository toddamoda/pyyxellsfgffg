from pathlib import Path
import sys

from pyxel.pipelines.model_group import ModelFunction
from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_registry import import_model
from tests.functional_tests import my_models
import esapy_config as om

CWD = Path(__file__).parent.parent
sys.path.append(str(CWD))

#
# my_model_def_yaml = """
#     group: charge_generation
#     name: my_model
#     enabled: True
#     func: functional_tests.test_add_model.my_model
#     arguments:
#           level: 5.0
# """
#
# my_model_def_dict = {
#     'group': 'charge_generation',
#     'name': 'my_model',
#     'enabled': True,
#     'func': 'functional_tests.test_add_model.my_model',
#     'arguments': {
#         'level': 7.5
#     }
# }


def my_model(detector, level):
    # set a new attribute so it can be checked later
    setattr(detector, 'level', level)  # NOTE: this is purely for testing
    return detector


def my_other_model(detector: Detector, level: int, noise: float=2.0):
    # set a new attribute so it can be checked later
    setattr(detector, 'level', level)
    setattr(detector, 'noise', noise)
    return detector


# def test_add_model():                                                      # todo reactivate this test
#     cfg = om.load(Path(CWD, 'data', 'test_yaml_new.yaml'))
#     processor = cfg['processor']
#     pipeline = processor.pipeline
#     detector = processor.detector
#     pipeline.set_model_enabled('*', False)
#
#     # test that all models are disabled
#     detector = pipeline.run(detector)
#     assert detector.signal.sum() == 0.0
#
#     # add a new model and call it
#     new_model = ModelFunction('my_model', 'functional_tests.test_add_model.my_model',
#                               arguments={'level': 1.5})
#     pipeline.model_groups['charge_generation'].models.append(new_model)
#     detector = pipeline.run(detector)
#     assert detector.level == 1.5
#
#     # add a new model using a function
#     pipeline.model_groups['charge_generation'].models.clear()
#     new_model = ModelFunction('my_model', my_model,
#                               arguments={'level': 2.5})
#     pipeline.model_groups['charge_generation'].models.append(new_model)
#     detector = pipeline.run(detector)
#     assert detector.level == 2.5
#
#     # # add a new model using the import functionality
#     # pipeline.model_groups['charge_generation'].models.clear()
#     # import_model(processor, my_model_def_yaml)
#     # detector = pipeline.run(detector)
#     # assert detector.level == 5.0
#     #
#     # # add a new model using the import functionality
#     # pipeline.model_groups['charge_generation'].models.clear()
#     # import_model(processor, my_model_def_dict)
#     # detector = pipeline.run(detector)
#     # assert detector.level == 7.5
#
#     # remove all models from the pipeline
#     for model_group in pipeline.model_groups.values():
#         model_group.models.clear()
#
#     # create a model through inspection
#     model_def = om.FunctionDef.create(my_other_model,
#                                       ignore_args=[Detector],
#                                       metadata={'group': 'charge_generation'})
#     # model_def = create_model_def(my_other_model, 'charge_generation')
#     model_def.arguments['level'] = 10.0
#     import_model(processor, model_def)
#     detector = pipeline.run(detector)
#     assert detector.level == 10.0
#     assert detector.noise == 2.0
#
#     # create a model definition using a callable class
#     model_def = om.FunctionDef.create(my_models.MyClassModel().__call__,
#                                       ignore_args=[Detector],
#                                       metadata={'group': 'charge_generation'})
#     # model_def = create_model_def(my_models.MyClassModel(), 'charge_generation')
#     model_def.arguments['level'] = 12.0
#     import_model(processor, model_def)
#     detector = pipeline.run(detector)
#     assert detector.level == 12.0
#     assert detector.noise == 2.0
#     om.dump(cfg)


# def test_model_registry_singleton():
#     reg1 = registry()
#     assert reg1 == registry
#     reg2 = registry(singleton=False)
#     assert reg2 != registry


# def test_model_registry():
#
#     assert 'my_other_class_model' in registry
#     assert 'my_class_model' in registry
#     assert len(registry) == 5
#
#     model_def = registry['my_class_model']
#     assert isinstance(model_def, dict)
#     for name, model_def in registry.items():
#         assert isinstance(model_def, dict)


def test_model_registry_decorator():
    # my_models.my_decorated_function(None)
    om.evaluate_reference('functional_tests.my_models.my_decorated_function')
    cfg = om.load(Path(CWD, 'data', 'test_yaml_new.yaml'))
    processor = cfg['processor']

    # remove all models from the pipeline
    for model_group in processor.pipeline.model_groups.values():
        model_group.models.clear()

    # import all model definitions into the processor
    for name in om.functions:
        model_def = om.functions[name]
        import_model(processor, model_def)

    # 'my_class_model'
    # 'my_other_class_model'
    # 'my_function_model'
    # 'my_dec_model_class'
    # 'my_dec_model_func'
    processor.pipeline.set_model_enabled('*', False)
    processor.pipeline.set_model_enabled('my_dec_model_class', True)
    processor.pipeline.set_model_enabled('my_dec_model_func', True)
    detector = processor.pipeline.run_pipeline(processor.detector)
    assert detector.class_std == 1.0
    assert detector.func_std == 2.0


# def test_model_registry_map():
#     group_models = my_models.registry_map
#     registry_new = registry(singleton=False)
#     registry_new.register_map(group_models)
#     expected_len = len(list(itertools.chain.from_iterable(group_models.values())))
#     assert expected_len == len(registry_new)


# def test_pipeline_import():
#     cfg = om.load(Path(CWD, 'data', 'test_yaml_new.yaml'))
#     processor = cfg['processor']
#
#     # remove all models from the pipeline
#     for model_group in processor.pipeline.model_groups.values():
#         model_group.models.clear()
#
#     registry.import_models(processor)
#     processor.pipeline.set_model_enabled('*', False)
#     processor.pipeline.set_model_enabled('my_class_model', True)
#     processor.pipeline.set_model_enabled('my_function_model', True)
#     processor.pipeline.set_model_enabled('my_other_class_model', True)
#     processor.set('pipeline.charge_generation.my_class_model.arguments.level', 1.0)
#     processor.set('pipeline.charge_generation.my_function_model.arguments.level', 2.0)
#     processor.set('pipeline.charge_generation.my_other_class_model.arguments.std', 3.0)
#
#     processor.pipeline.run(processor.detector)
#
#     value = processor.get('pipeline.charge_generation.my_other_class_model.arguments.std')
#     assert processor.detector.std == value
#     assert processor.detector.std == 3.0
#
#     assert processor.detector.level == 2.0
#
#     processor.pipeline.set_model_enabled('my_function_model', False)
#     processor.pipeline.run(processor.detector)
#     assert processor.detector.level == 1.0
#
#     print(om.dump(cfg))
