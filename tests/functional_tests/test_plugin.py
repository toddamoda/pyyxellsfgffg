# import sys
# from pathlib import Path
#
# import yaml
#
# from pyxel import plugins
# from pyxel.io.yaml_processor import load_config
# from pyxel.pipelines.detector_pipeline import Detector
#
# CWD = Path(__file__).parent.parent
#
# sys.path.append(str(CWD))
#
#
# MODEL="""
# models:
#     -
#         processor: ccd_process
#         name: my_model
#         group: charge_generation
#         model:
#             name: functional_tests.test_plugin.my_model
#             arguments:
#                   my_arg: 1.0
#
# """
#
# repository = {
#
# }
#
# def my_model(detector: Detector, my_arg: float):
#     new_detector = detector
#     # TODO: implement model
#     return new_detector
#
#
# def test_plugin():
#
#     cfg = load_config(Path('tests/data/pipeline_template.yaml'))
#     processor = cfg['ccd_process']      # type: pyxel.pipelines.processor.Processor
#
#     pipeline = processor.pipeline  # type: t.Union[CCDDetectionPipeline, CMOSDetectionPipeline]
#
#     plugins.import_model(cfg, MODEL)
#     plugins.import_model(cfg, repository['load_image_def'])
#     plugins.import_model(cfg, repository['photon_level_def'])
#     plugins.import_model(cfg, repository['shot_noise_def'])
#     plugins.import_model(cfg, MODEL4)
#     plugins.import_model(cfg, MODEL5)
#     plugins.import_model(cfg, MODEL6)
#     plugins.import_model(cfg, MODEL7)
#
#     yaml.dumps(cfg, 'my_settings.yaml')
#
#     # Step 2: Run the pipeline
#     detector = pipeline.run_pipeline(processor.detector)  # type: CCD
#     print('Pipeline completed.')
#
#
# if __name__ == '__main__':
#     test_plugin()
#
#
#
# class ModelFoo:
#
#     def __init__(self, name: str, func: str, default_args):
#         pass
#
#     def give_me_func(self) -> typing.Callable:
#         pass
#
#
# class ModelsGroup:
#
#     def __init__(self, group='photon_generation', detector_family='ccd'):
#         pass
#
#     def add_model(self, model: ModelFoo, order_num: int):
#         pass
#
#     def ordered_list(self):
#         return None
#
#
# photon_generation_group = ModelsGroup(group='photon_generation')
# photon_generation_group.add(name='load_image', func='pyxel.xxx.func')
#
# MODEL = """
# -
#   group: photon_generation
#
#   models:
#
#     model:
#         order: 1
#         name: tim_model
#         func: tim_lib.tim_func
# """
#
# plugins = yaml.load(MODEL, Loader=yaml.SafeLoader)
#
# >>> assert isinstance(plugins['photon_generation'], ModelsGroup)
# True
#
# >>> plugins['photon_generation'].ordered_list()
# ['load_image', 'tim_model']
#
# >>> assert plugins['photon_generation'].give_model('load_image')
# callable_load_image
#
# >>> assert plugins['photon_generation'].give_model('tim_model')
# callable_tim_model
#
#
#
#
#
#
#
#
#
#
