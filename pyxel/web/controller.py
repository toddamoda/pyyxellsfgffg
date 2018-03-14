"""TBW."""
import logging
import threading
import importlib
from pathlib import Path

import yaml

from pyxel import util
from pyxel.web import signals
from pyxel.web import webapp
from pyxel.io.yaml_processor_new import load_config
from pyxel.io.yaml_processor_new import dump
from pyxel.pipelines.processor import Processor
from pyxel.pipelines.model_registry import registry


CWD_PATH = Path(__file__).parent


class Controller:
    """TBW."""

    def __init__(self, processor: Processor=None) -> None:
        """TBW.

        :param processor:
        """
        config_dir = Path(__file__).parent.parent
        self.pipeline_paths = {
            'ccd': config_dir.joinpath('io', 'templates', 'ccd.yaml'),
            'cmos': config_dir.joinpath('io', 'templates', 'cmos.yaml'),
        }
        self._log = logging.getLogger(__name__)
        self._th = None             # type: threading.Thread
        self._is_running = False    # type: bool
        self._modified_time = None  # type: float
        self._items = None          # type: dict
        self.processor = processor  # type: Processor
        self.parametric = None

        signals.dispatcher.connect(sender='api', signal=signals.LOAD_PIPELINE, callback=self.load_template)
        signals.dispatcher.connect(sender='api', signal=signals.RUN_PIPELINE, callback=self.toggle_pipeline)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SETTING, callback=self.set_setting)
        signals.dispatcher.connect(sender='api', signal=signals.GET_SETTING, callback=self.get_setting)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SEQUENCE, callback=self.set_sequence)
        signals.dispatcher.connect(sender='api', signal=signals.PROGRESS, callback=webapp.announce_progress)
        signals.dispatcher.connect(sender='api', signal=signals.SET_MODEL_STATE, callback=self.set_model_state)
        signals.dispatcher.connect(sender='api', signal=signals.GET_MODEL_STATE, callback=self.get_model_state)
        signals.dispatcher.connect(sender='api', signal=signals.GET_STATE, callback=self.get_state)
        signals.dispatcher.connect(sender='api', signal=signals.EXECUTE_CALL, callback=self.execute_call)

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
            cfg = load_config(config_path)
            self.parametric = cfg['parametric']
            self.processor = cfg['processor']
            registry.import_models(self.processor)
        else:
            self.parametric = None
            self.processor = None

    def load_defaults(self, path):
        """TBW."""
        cfg = load_config(Path(path))
        obj_dict = util.get_state_dict(cfg['processor'])
        state = util.get_state_ids(obj_dict)
        for key, value in state.items():
            try:
                self.processor.set(key, value)
            except AttributeError as exc:
                self._log.error('Could not set key: %s', key)
        self.get_state()

    def load_config(self, path):
        """TBW."""
        cfg = load_config(Path(path))
        self.parametric = cfg['parametric']
        self.processor = cfg['processor']
        self.get_state()

    def save_config(self, path):
        """TBW."""
        cfg = {
            'processor': self.processor,
            'parametric': self.parametric,
        }
        output = dump(cfg)
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
        registry.save('registry.yaml')  # for debugging

    def get_gui_defs(self):
        """Retrieve the dictionary object model that is defined in the gui.yaml configuration file.

        This method is referenced in control.html template file.

        :return:
        """
        gui_file = CWD_PATH.joinpath('gui.yaml')  # TODO: hardcoded
        mtime = gui_file.stat().st_mtime  # os.path.getmtime(gui_file)
        if self._modified_time != mtime:
            self._modified_time = mtime
            with gui_file.open() as fd:
                cfg = yaml.load(fd)
                self.load_gui_model_defs(cfg)
            self._items = cfg
        return self._items['gui']

    def toggle_pipeline(self, output_file=None):
        """TBW."""
        if self._is_running:
            self._is_running = False
        else:
            self._th = threading.Thread(target=self.run_pipeline_sequence, args=[output_file])
            self._th.start()

    @staticmethod
    def announce(type_key, key, value):
        """TBW."""
        msg = {
            'type': type_key,
            'id': key,
            'fields': {'value': value},
        }
        webapp.WebSocketHandler.announce(msg)

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
            id_value_dict = util.get_state_ids(result)
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
            self.processor.set(key, value)
            self.get_setting(key)   # signal updated value to listeners

    def load_gui_model_defs(self, cfg):
        """TBW."""
        model_settings = cfg['gui'][1]['items']
        model_settings.clear()
        if self.processor:
            pipeline = self.processor.pipeline

            for group in pipeline.model_group_names:
                items = registry.get_group(pipeline.name, group)
                # items = [registry[key] for key in registry if registry[key]['group'] == group]
                for item in items:
                    gui_def_override = item.get('gui', {})
                    entry_def_override = gui_def_override.get('arguments', {})
                    group_label = group.replace('_', ' ').title()
                    model_label = gui_def_override.get('label', item['name']).replace('_', ' ').title()
                    label = '{}: {}'.format(group_label, model_label)
                    gui_def = {
                        'label': label,
                        'arguments': []
                    }
                    for arg in item['arguments']:
                        entry_def = {
                            'id': 'pipeline.' + group + '.' + item['name'] + '.arguments.' + arg,
                            'label': arg,
                            'entry': {
                                'tag': 'input',
                                'type': 'text'
                            }
                        }
                        entry_def.update(entry_def_override.get(arg, {}))

                        gui_def['arguments'].append(entry_def)

                    model_settings.append(gui_def)

            x = yaml.dump(cfg, default_flow_style=False)
            print(x)
            return

    def run_pipeline_sequence(self, output_file=None):
        """TBW."""
        # is_sequence = True in [sequence['enabled'] for sequence in self.sequence]
        try:
            self._is_running = True
            if self.parametric:
                signals.progress('state', {'value': 'running', 'state': 1})
                configs = self.parametric.collect(self.processor)
                configs_len = len(list(configs))
                configs = self.parametric.collect(self.processor)
                for i, config in enumerate(configs):
                    result = {
                        'processor': config.get_state_json(),
                        'parametric': self.parametric.get_state_json(),
                    }
                    id_value_dict = util.get_state_ids(result)
                    self.announce('state', 'all', id_value_dict)

                    signals.progress('state', {'value': 'running (%d of %d)' % (i+1, configs_len), 'state': 1})
                    detector = config.pipeline.run_pipeline(config.detector)

                    if output_file:
                        save_to = util.apply_run_number(output_file)
                        out = util.FitsFile(save_to)
                        out.save(detector.signal, header=None, overwrite=True)
                        signals.progress('state', {'value': 'saved', 'state': 2, 'file': save_to})
                        # output.append(output_file)
                signals.progress('state', {'value': 'completed', 'state': 0})

        except Exception as exc:
            self._log.exception(exc)
            signals.progress('state', {'value': 'error: %s' % str(exc), 'state': -1})
        finally:
            self._is_running = False

    # def load_registry(self, path='pyxel/model_registry.yaml'):
    #     """Deprecated."""
    #     pipeline = self.processor.pipeline
    #     pipeline.clear()
    #     registry.clear()
    #     with open(path, 'r') as fd:  # TODO: hardcoded
    #         reg_map = yaml.load(fd.read())
    #         registry.register_map(reg_map, pipeline.name)
    #         registry.import_models(self.processor)
    #
    #     self._modified_time = None
