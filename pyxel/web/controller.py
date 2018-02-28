"""TBW."""
import yaml
import os
import threading
from pathlib import Path


import pyxel
from pyxel import util
from pyxel.web import signals
from pyxel.web import webapp
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.web.sequencer import Sequencer


class Controller:
    """TBW."""

    def __init__(self, processor: DetectionPipeline, address_viewer: str=None) -> None:
        """TBW.

        :param processor:
        """
        config_dir = Path(__file__).parent.parent
        self.pipeline_paths = {
            'ccd': config_dir.joinpath('settings_ccd.yaml'),
            'cmos': config_dir.joinpath('settings_cmos.yaml'),
        }
        self._th = None             # type: threading.Thread
        self._is_running = False    # type: bool
        self._modified_time = None  # type: float
        self._items = None          # type: dict
        self._address_viewer = address_viewer  # type: str
        self.processor = processor  # type: DetectionPipeline
        self.processor_name = None  # type: str
        self.sequencer = Sequencer(self)

        signals.dispatcher.connect(sender='api', signal=signals.LOAD_PIPELINE, callback=self.load_pipeline)
        signals.dispatcher.connect(sender='api', signal=signals.RUN_PIPELINE, callback=self.start_pipeline)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SETTING, callback=self.set_setting)
        signals.dispatcher.connect(sender='api', signal=signals.GET_SETTING, callback=self.get_setting)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SEQUENCE, callback=self.set_sequence)
        signals.dispatcher.connect(sender='api', signal=signals.PROGRESS, callback=webapp.announce_progress)
        signals.dispatcher.connect(sender='api', signal=signals.SET_MODEL_STATE, callback=self.set_model_state)
        signals.dispatcher.connect(sender='api', signal=signals.GET_MODEL_STATE, callback=self.get_model_state)

    @property
    def address_viewer(self):
        """TBW."""
        if isinstance(self._address_viewer, str):
            if ':' in self._address_viewer:
                host_port = self._address_viewer.rsplit(':', 1)
                return host_port[0], int(host_port[1])
        return None

    def load_pipeline(self, name):
        """Load a new YAML pipeline file into memory.

        :param name:
        """
        if name in self.pipeline_paths:
            config_path = self.pipeline_paths[name]
            cfg = pyxel.load_config(config_path)
            root_key = list(cfg.keys())[0]
            self.processor = cfg[root_key]
            self.processor_name = name
        else:
            self.processor = None
            self.processor_name = None

    def get_model_groups(self):
        """TBW.

        :return:
        """
        if self.processor:
            return self.processor.pipeline.model_groups
        return []

    def get_pipeline_names(self):
        """TBW."""
        return list(self.pipeline_paths.keys())

    @staticmethod
    def get_gui_props(entry):
        """Append all the GUI properties into a key="value" string that is inserted into the generated HTML template.

        This method is referenced in control.html template file.

        :return:
        """
        result = []
        for key in entry:
            result.append('%s="%s"' % (key, entry[key]))
        return ' '.join(result)

    def get_gui_defs(self):
        """Retrieve the dictionary object model that is defined in the gui.yaml configuration file.

        This method is referenced in control.html template file.

        :return:
        """
        mtime = os.path.getmtime('gui.yaml')
        if self._modified_time != mtime:
            self._modified_time = mtime
            with open('gui.yaml', 'r') as fd:
                cfg = yaml.load(fd)
            self._items = cfg
        return self._items['gui']

    def start_pipeline(self, run_mode='single', output_file=None):
        """TBW."""
        if self._is_running:
            self._is_running = False
        else:
            self._th = threading.Thread(target=self.run_pipeline_sequence, args=[run_mode, output_file])
            self._th.start()

    def run_pipeline_sequence(self, run_mode='single', output_file=None):
        """TBW."""
        # is_sequence = True in [sequence['enabled'] for sequence in self.sequence]
        try:
            self._is_running = True
            self.sequencer.set_mode(run_mode)
            self.sequencer.set_output_file(output_file)
            self.sequencer.run()
        except Exception as exc:
            signals.progress('state', {'value': 'error: %s' % str(exc), 'state': -1})
        finally:
            self._is_running = False

    def set_sequence(self, index, key, values, enabled):
        """TBW.

        :param index:
        :param key:
        :param values:
        :param enabled:
        """
        self.sequencer.set_range(index, key, values, enabled)

    def get_model_state(self, model_name):
        """TBW.

        :param model_name:
        :return:
        """
        model = self.processor.pipeline.get_model(model_name)
        enabled = False
        if model:
            enabled = model.enabled

        msg = {
            'type': 'enabled',
            'id': model_name,
            'fields': {'value': enabled},
        }
        webapp.WebSocketHandler.announce(msg)
        return enabled

    def set_model_state(self, model_name, enabled):
        """TBW.

        :param model_name:
        :param enabled:
        """
        model = self.processor.pipeline.get_model(model_name)
        if model:
            model.enabled = enabled
        self.get_model_state(model_name)  # signal updated value to listeners

    # def _get_setting_object(self, key):
    #     """TBW.
    #
    #     :param key:
    #     :return:
    #     """
    #     obj_props = key.split('.')
    #     att = obj_props[-1]
    #     obj = self.processor
    #     for part in obj_props[:-1]:
    #         if isinstance(obj, functools.partial) and part == 'arguments':
    #             obj = obj.keywords
    #         else:
    #             try:
    #                 obj = getattr(obj, part)
    #             except AttributeError:
    #                 # logging.error('Cannot find attribute %r in key %r', part, key)
    #                 obj = None
    #                 break
    #     return obj, att

    def has_setting(self, key):
        """TBW.

        :param key:
        :return:
        """
        found = False
        obj, att = util.get_obj_att(self.processor, key)
        if isinstance(obj, dict) and att in obj:
            found = True
        elif hasattr(obj, att):
            found = True
        return found

    def get_setting(self, key):
        """TBW.

        :param key:
        :return:
        """
        obj, att = util.get_obj_att(self.processor, key)

        if isinstance(obj, dict) and att in obj:
            value = obj[att]
        else:
            value = getattr(obj, att)

        msg = {
            'type': 'get',
            'id': key,
            'fields': {'value': value},
        }
        webapp.WebSocketHandler.announce(msg)
        return value

    def set_setting(self, key, value):
        """TBW.

        :param key:
        :param value:
        """
        if value:
            if isinstance(value, list):
                for i, val in enumerate(value):
                    if val:
                        value[i] = util.eval_entry(val)
            else:
                value = util.eval_entry(value)

        obj, att = util.get_obj_att(self.processor, key)

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)
        self.get_setting(key)   # signal updated value to listeners
