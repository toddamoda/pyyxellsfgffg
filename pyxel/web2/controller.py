"""TBW."""
import logging
import threading
import importlib
from pathlib import Path
import typing as t

import esapy_config as om  # noqa: F401

from esapy_web.webapp2.modules import guiconfig

from pyxel import util
from pyxel.pipelines.processor import Processor
from pyxel.pipelines.model_registry import registry
from pyxel.pipelines.model_group import ModelFunction


CWD_PATH = Path(__file__).parent
SET_MODEL_STATE = 'SET-MODEL-STATE'
GET_MODEL_STATE = 'GET-MODEL-STATE'
RUN_APPLICATION = 'RUN-APPLICATION'
LOAD_PIPELINE = 'LOAD-PIPELINE'
RUN_PIPELINE = 'RUN-PIPELINE'
SET_SEQUENCE = 'SET-SEQUENCE'
OUTPUT_DATA_DIR = 'OUTPUT-DIR'
SET_SETTING = 'SET-SETTING'
GET_SETTING = 'GET-SETTING'
GET_STATE = 'GET-STATE'
# APPEND_STATE = 'APPEND-STATE'
# SAVE_STATE = 'SAVE-STATE'
# LOAD_STATE = 'LOAD-STATE'
# UPDATED = 'UPDATED'
PROGRESS = 'PROGRESS'
EXECUTE_CALL = 'EXECUTE-CALL'
# CALL_FUNCTION = 'CALL-FUNCTION'
# CALL_FUNCTION_ASYNC = 'CALL-FUNCTION-ASYNC'


class Controller(guiconfig.Controller):
    """TBW."""

    def __init__(self, dispatcher: t.Any, processor: Processor=None) -> None:
        """TBW.

        :param processor:
        """
        super(Controller, self).__init__(processor, dispatcher)

        config_dir = Path(__file__).parent.parent
        self.pipeline_paths = {
            'ccd': config_dir.joinpath('io', 'templates', 'ccd.yaml'),
            'cmos': config_dir.joinpath('io', 'templates', 'cmos.yaml'),
        }
        self._log = logging.getLogger(__name__)
        self._th = None             # type: t.Optional[threading.Thread]
        self._is_running = False    # type: bool
        self._modified_time = None  # type: t.Optional[float]
        self._items = None          # type: t.Optional[dict]
        self.processor = processor  # type: t.Optional[Processor]
        self.parametric = None
        self.dispatcher = dispatcher

        sender = guiconfig.Signals.SENDER_CONFIG
        dispatcher.connect(sender, signal=LOAD_PIPELINE, callback=self.load_template)
        dispatcher.connect(sender, signal=RUN_PIPELINE, callback=self.toggle_pipeline)
        dispatcher.connect(sender, signal=SET_SEQUENCE, callback=self.set_sequence)
        dispatcher.connect(sender, signal=SET_MODEL_STATE, callback=self.set_model_state)
        dispatcher.connect(sender, signal=GET_MODEL_STATE, callback=self.get_model_state)
        dispatcher.connect(sender, signal=SET_SETTING, callback=self.set_setting)
        dispatcher.connect(sender, signal=GET_SETTING, callback=self.get_setting)
        dispatcher.connect(sender, signal=PROGRESS, callback=self.progress)
        # dispatcher.connect(sender, signal=PROGRESS, callback=webapp.announce_progress)
        dispatcher.connect(sender, signal=GET_STATE, callback=self.get_state)
        dispatcher.connect(sender, signal=EXECUTE_CALL, callback=self.execute_call)

    @property
    def config(self):
        """TBW."""
        return self.processor

    @config.setter
    def config(self, config_object):
        """TBW."""
        self.processor = config_object

    def execute_call(self, method, *args, **kwargs):
        """TBW."""
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)

    def load_template(self, name):
        """Load a new YAML pipeline file into memory.

        :param name: ccd or cmos
        """
        if name in self.pipeline_paths:
            config_path = self.pipeline_paths[name]
            cfg = om.load(config_path)
            self.parametric = cfg['parametric']
            self.processor = cfg['processor']
            registry.import_models(self.processor)
        else:
            self.parametric = None
            self.processor = None

    @staticmethod
    def _rewire_pipeline_dict(pipeline: dict):
        """Convert pipeline models to a dict like structure.

        The pipeline JSON structure is like so::

            {'charge_generation': [
                {'func': 'pyxel.models.photoelectrons.simple_conversion', 'name': 'photoelectrons', ... },
                ...
            ]},
            {'photon_generation': [
                {'func': 'pyxel.models.photon_generation.load_image', 'name': 'load_image', ... },
                ...
            ]}

        The pipeline is rewired like so::

            {'charge_generation': {
                'photoelectrons': {'func': 'pyxel.models.photoelectrons.simple_conversion', ... },
                ...
            ]},
            {'photon_generation': [
                'load_image': {'func': 'pyxel.models.photon_generation.load_image', 'name': 'load_image', ... },
                ...
            ]}

        This simplifies the javascript side of the application.

        :param pipeline:
        """
        for model_group_key in pipeline:
            model_dict = {}
            if isinstance(pipeline[model_group_key], list):
                for model in pipeline[model_group_key]:
                    model_dict[model['name']] = model
            pipeline[model_group_key] = model_dict

    def load_defaults(self, path):
        """TBW."""
        cfg = om.load(Path(path))
        obj_dict = om.get_state_dict(cfg['processor'])

        self._rewire_pipeline_dict(obj_dict['pipeline'])

        state = om.get_state_ids(obj_dict)
        for key, value in state.items():
            try:
                self.processor.set(key, value)
            except om.ValidationError as exc:
                self.announce('error', key, value)
                self._log.error('Could not set key: %s', key)
                self._log.error(exc)
            except AttributeError as exc:
                self._log.error('Could not set key: %s', key)
                self._log.error(exc)
        self.get_state()

    def load_config(self, path):
        """TBW."""
        cfg = om.load(Path(path))
        self.parametric = cfg['parametric']
        self.processor = cfg['processor']
        self.get_state()

    def save_config(self, path):
        """TBW."""
        cfg = {
            'processor': self.processor,
            'parametric': self.parametric,
        }
        output = om.dump(cfg)
        print(output)
        with open(path, 'w') as fd:
            fd.write(output)

    @property
    def model_groups(self):
        """TBW."""
        if self.processor:
            return self.processor.pipeline.model_groups
        return {}

    def get_pipeline_names(self):
        """TBW."""
        return list(self.pipeline_paths.keys())

    @staticmethod
    def properties(entry):
        """Append all the GUI properties into a key="value" string that is inserted into the generated HTML template.

        This method is referenced in control.html template file.

        :return:
        """
        result = []
        for key in entry:
            result.append('%s="%s"' % (key, entry[key]))
        return ' '.join(result)

    def load_modules(self, *modules):
        """Load a list of modules."""
        for module in modules:
            importlib.import_module(module)
        self._modified_time = None  # force GUI definition to reload

    # @property
    # def gui(self):
    #     """Dynamically create the object model GUI schema.
    #
    #     This method is referenced in control.html template file.
    #
    #     :return:
    #     """
    #     sections_detector = []
    #     sections_model = []
    #     cfg = {
    #         'gui': [
    #             {
    #                 'label': 'Detector Attributes',
    #                 'section': sections_detector,
    #             },
    #             {
    #                 'label': 'Models Settings',
    #                 'section': sections_model,
    #             }
    #         ]
    #     }
    #     serializer = om.serializer.pyxel_gui.Serializer
    #     if self.processor:
    #         for key, value in self.processor.detector.__getstate__().items():
    #             sections = serializer.create_section_from_object(value, 'detector.' + key)
    #             sections_detector.extend(sections)
    #
    #         pipeline = self.processor.pipeline
    #         for group in pipeline.model_group_names:
    #             items = registry.get_group(pipeline.name, group)
    #             for item in items:
    #                 prefix = 'pipeline.' + group + '.' + item.name + '.arguments'
    #                 gui_def = serializer.create_section_from_func_def(item, prefix)
    #                 sections_model.append(gui_def)
    #
    #     return cfg['gui']

    def toggle_pipeline(self, output_file=None):
        """TBW."""
        if self._is_running:
            self._is_running = False
        else:
            self._th = threading.Thread(target=self.run_pipeline_sequence, args=[output_file])
            self._th.start()

    # @staticmethod
    # def announce(type_key, key, value):
    #     """TBW."""
    #     msg = {
    #         'type': type_key,
    #         'id': key,
    #         'fields': {'value': value},
    #     }
    #     dispatch.announce(msg)
    #
    # @staticmethod
    # def progress(key, fields):
    #     """TBW."""
    #     msg = {
    #         'type': 'progress',
    #         'id': key,
    #         'fields': fields,
    #     }
    #     dispatch.announce(msg)

    def set_sequence_mode(self, run_mode):
        """TBW."""
        self.parametric.mode = run_mode

    def set_sequence(self, index, key, values, enabled):
        """TBW.

        :param index:
        :param key:
        :param values:
        :param enabled:
        """
        if self.parametric:
            step = self.parametric.steps[index]
            step.key = key
            step.enabled = enabled
            step.values = values

    def get_model_state(self, model_name):
        """TBW.

        :param model_name:
        :return:
        """
        enabled = self.processor.get(model_name)
        self.announce('enabled', model_name, enabled)
        return enabled

    def set_model_state(self, model_name, enabled):
        """TBW.

        :param model_name:
        :param enabled:
        """
        self.processor.set(model_name, enabled)
        self.get_model_state(model_name)  # signal updated value to listeners

    def get_state(self):
        """TBW.

        :return:
        """
        if self.processor:
            result = {
                'processor': self.processor.get_state_json(),
                'parametric': self.parametric.get_state_json(),
            }
            self._rewire_pipeline_dict(result['processor']['pipeline'])

            id_value_dict = om.get_state_ids(result)
            self.announce('state', 'all', id_value_dict)
            return result

    def has_setting(self, key):
        """TBW.

        :param key:
        :return:
        """
        if self.processor:
            return self.processor.has(key)

    def get_setting(self, key):
        """TBW.

        :param key:
        :return:
        """
        if self.processor:
            value = self.processor.get(key)
            self.announce('get', key, value)
            return value

    def set_setting(self, key, value):
        """TBW.

        :param key:
        :param value:
        """
        if self.processor:
            model = om.get_obj_by_type(self.processor, key, ModelFunction)
            if model:
                try:
                    att = key.split('.')[-1]
                    om.validate_arg(model.func, att, value)
                except om.ValidationError as exc:
                    self.announce('error', key, exc.msg)
                    return

            try:
                self.processor.set(key, value)
            except om.ValidationError as exc:
                self.announce('error', key, exc.msg)
                return

            self.get_setting(key)   # signal updated value to listeners

    def run_pipeline_sequence(self, output_file=None):
        """TBW."""
        # is_sequence = True in [sequence['enabled'] for sequence in self.sequence]
        try:
            self._is_running = True
            if self.parametric:
                self.progress('state', {'value': 'running', 'state': 1})
                configs = self.parametric.collect(self.processor)
                configs_len = len(list(configs))
                configs = self.parametric.collect(self.processor)
                for i, config in enumerate(configs):
                    result = {
                        'processor': config.get_state_json(),
                        'parametric': self.parametric.get_state_json(),
                    }
                    id_value_dict = om.get_state_ids(result)
                    self.announce('state', 'all', id_value_dict)

                    self.progress('state', {'value': 'running (%d of %d)' % (i+1, configs_len), 'state': 1})
                    detector = config.pipeline.run_pipeline(config.detector)

                    if output_file:
                        save_to = util.apply_run_number(output_file)
                        out = util.FitsFile(save_to)
                        out.save(detector.signal, header=None, overwrite=True)
                        self.dispatcher.emit('*', signal=OUTPUT_DATA_DIR)(save_to)
                        self.progress('state', {'value': 'saved', 'state': 2, 'file': save_to})
                        # output.append(output_file)
                        self.progress('state', {'value': 'completed', 'state': 0})

        except Exception as exc:
            self._log.exception(exc)
            self.progress('state', {'value': 'error: %s' % str(exc), 'state': -1})
        finally:
            self._is_running = False
