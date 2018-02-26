"""TBW."""
import glob
import yaml
import functools
import os
import threading
import logging
import typing as t
from ast import literal_eval
from pathlib import Path

import esapy_rpc as rpc
from esapy_rpc.rpc import SimpleSerializer

import pyxel
from pyxel.util import FitsFile
from pyxel.web import signals
from pyxel.web import webapp
from pyxel.pipelines.detector_pipeline import PipelineAborted
from pyxel.pipelines.detector_pipeline import DetectionPipeline


def announce_progress(idn: str, fields: dict):
    """TBW.

    :param idn:
    :param fields:
    :return:
    """
    msg = {
        'type': 'progress',
        'id': idn,
        'fields': fields,
    }
    webapp.WebSocketHandler.announce(msg)


def run_pipeline(processor, output_file=None, address_viewer=None):
    """TBW.

    :param processor:
    :param output_file:
    :return:
    """
    try:
        signals.progress('state', {'value': 'running', 'state': 1})
        result = processor.pipeline.run(processor.detector)
    except PipelineAborted:
        signals.progress('state', {'value': 'aborted', 'state': 0})
        return
    except Exception as exc:
        signals.progress('state', {'value': 'error', 'state': -1})
        logging.exception(exc)
        return

    if result and output_file:
        try:
            output_file = os.path.abspath(output_file)
            output_file = apply_run_number(output_file)
            signals.progress('state', {'value': 'saving', 'state': 2})
            out = FitsFile(output_file)
            out.save(result.signal.astype('uint16'), header=None, overwrite=True)
            signals.progress('state', {'value': 'saved', 'state': 2, 'file': output_file})
        except Exception as exc:
            signals.progress('state', {'value': 'error', 'state': -2})
            logging.exception(exc)
            return

        if address_viewer:
            try:
                client = rpc.ProxySocketClient(address_viewer,
                                               serializer=SimpleSerializer(),
                                               protocol=rpc.http.Client(action='POST'))
                proxy = rpc.ProxyObject(client)
                signals.progress('state', {'value': 'loading', 'state': 3})
                proxy.load_file(output_file)
            except Exception as exc:
                signals.progress('state', {'value': 'warning', 'state': -3})
                logging.warning('No RPC server listening. Error :%s', exc)

    signals.progress('state', {'value': 'completed', 'state': 0})


def eval_entry(value):
    """TBW.

    :param value:
    :return:
    """
    if isinstance(value, str):
        try:
            literal_eval(value)
        except (SyntaxError, ValueError, NameError):
            # ensure quotes in case of string literal value
            if value[0] == "'" and value[-1] == "'":
                pass
            elif value[0] == '"' and value[-1] == '"':
                pass
            else:
                value = '"' + value + '"'

        value = literal_eval(value)
    return value


def apply_run_number(path):
    """Convert the file name numeric placeholder to a unique number.

    :param path:
    :return:
    """
    path_str = str(path)
    if '?' in path_str:
        dir_list = sorted(glob.glob(path_str))
        p_0 = path_str.find('?')
        p_1 = path_str.rfind('?')
        template = path_str[p_0: p_1 + 1]
        path_str = path_str.replace(template, '{:0%dd}' % len(template))
        last_num = 0
        if len(dir_list):
            path_last = dir_list[-1]
            last_num = int(path_last[p_0: p_1 + 1])
        last_num += 1
        path_str = path_str.format(last_num)
    return type(path)(path_str)


class API:
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
        signals.dispatcher.connect(sender='api', signal=signals.PROGRESS, callback=announce_progress)
        signals.dispatcher.connect(sender='api', signal=signals.SET_MODEL_STATE, callback=self.set_model_state)
        signals.dispatcher.connect(sender='api', signal=signals.GET_MODEL_STATE, callback=self.get_model_state)

    @property
    def address_viewer(self):
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
            return self.processor.pipeline._model_groups
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

    def _get_setting_object(self, key):
        """TBW.

        :param key:
        :return:
        """
        obj_props = key.split('.')
        att = obj_props[-1]
        obj = self.processor
        for part in obj_props[:-1]:
            if isinstance(obj, functools.partial) and part == 'arguments':
                obj = obj.keywords
            else:
                try:
                    obj = getattr(obj, part)
                except AttributeError:
                    # logging.error('Cannot find attribute %r in key %r', part, key)
                    obj = None
                    break
        return obj, att

    def has_setting(self, key):
        """TBW.

        :param key:
        :return:
        """
        found = False
        obj, att = self._get_setting_object(key)
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
        obj, att = self._get_setting_object(key)

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
                        value[i] = eval_entry(val)
            else:
                value = eval_entry(value)

        obj, att = self._get_setting_object(key)

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)
        self.get_setting(key)   # signal updated value to listeners


class Sequencer:
    """TBW."""

    def __init__(self, controller: API) -> None:
        """TBW.

        :param controller:
        :param steps:
        :param output_file:
        """
        self._log = logging.getLogger(__name__)
        self._controller = controller
        self._output_file = None
        # self._steps = steps  # type: t.List[dict]  # key[str], values[list], enabled[bool]
        self._current = None  # type: dict

        self._paused = False
        self._running = False
        self._th = None  # type: threading.Thread

        self._step = 0
        self._level = 0
        self._n_steps = 1
        self._run_mode = 'recurse'

        self._steps = [  # TODO: create a Step class
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
        ]

    def set_mode(self, mode):
        """Set the mode to run the sequencer in.

        :param mode: accepted values: recurse, linear, single

        """
        self._run_mode = mode

    def set_output_file(self, output_file):
        """TBW.

        :param output_file:
        """
        self._output_file = output_file

    def set_range(self, index, key, values, enabled):
        """TBW.

        :param index:
        :param key:
        :param values:
        :param enabled:
        """
        if values:
            if isinstance(values, str):
                values = eval(values)

            if not isinstance(values, (list, tuple)):
                values = list(values)
        else:
            values = []
        self._steps[index]['key'] = key
        self._steps[index]['values'] = values
        self._steps[index]['enabled'] = enabled

    @property
    def enabled_steps(self):
        """TBW."""
        result = []
        for step in self._steps:
            if step['enabled']:
                result.append(step)
        return result

    def is_running(self) -> bool:
        """TBW."""
        return self._running

    def start(self):
        """TBW."""
        self._th = threading.Thread(target=self.run)
        self._th.start()

    def join(self):
        """TBW."""
        if self._th is not None:
            self._th.join()
        self._th = None

    def stop(self):
        """TBW."""
        self._paused = False  # abort any paused state as well.
        self._running = False

    def _run_step(self, step, val):
        # self._log.info('Step %d of %d', self._step, self._n_steps)
        signals.progress('state', {'value': 'running', 'state': 1})
        try:
            key = step['key']
            self._controller.set_setting(key, val)
            signals.progress('sequence_%d' % self._level, {'value': val, 'state': 1})
            # run_pipeline(self._controller.processor, self._output_file)
            signals.progress('sequence_%d' % self._level, {'value': val, 'state': 0})
        except Exception as exc:
            self._log.exception(exc)
            pass  # TODO: what to do?

    def _load_initial_state(self):
        for i, step in enumerate(self.enabled_steps):
            if len(step['values']):
                val_0 = step['values'][0]
                key = step['key']
                self._controller.set_setting(key, val_0)
                signals.progress('sequence_%d' % i, {'value': val_0, 'state': 1})

    def _single(self):
        """TBW."""
        try:
            run_pipeline(self._controller.processor, self._output_file, self._controller.address_viewer)
        except Exception as exc:
            self._log.exception(exc)
            pass  # TODO: what to do?

    def _loop(self):
        """Linear loop method."""

        for i, step in enumerate(self.enabled_steps):  #step = self.enabled_steps[i]
            if not self.is_running():
                break
            self._level = i
            self._current = step
            for val in step['values']:
                if not self.is_running():
                    break

                self._step += 1
                self._run_step(step, val)
                self._single()

    def _recurse(self, i=0):
        """Recursive loop method.

        .. warning:: this method is re-entrant
        """
        step = self.enabled_steps[i]
        self._level = i
        self._current = step
        for val in step['values']:
            # check if the loop is still running
            if not self.is_running():
                break

            self._step += 1
            self._run_step(step, val)
            if i+1 < len(self.enabled_steps):
                self._recurse(i+1)
                # check if user-defined exit handler was called
                if not self.is_running():
                    break
                self._level = i
                self._current = step  # reset back to this context's step
            else:
                self._single()

    def _calculate_total_steps(self):
        """Calculate the number of steps in a recursive loop.

        The following equation is implemented::

            total steps = L3*(1+L2*(1+L1*(1+L0)))

        Where,

            * L0 is the outer most loop count
            * L3 is the inner most loop.

        Of course, this loop has no depth limit, so L3 is actually LN in this
        case.
        """
        num_steps = 1
        if self._run_mode == 'recurse':
            for item in reversed(self.enabled_steps):
                num_steps = 1 + len(list(item)) * num_steps
            num_steps -= 1
        elif self._run_mode == 'linear':
            for item in reversed(self.enabled_steps):
                num_steps += len(list(item))
        self._n_steps = num_steps

    def run(self):
        """TBW."""
        self._running = True
        try:
            self._calculate_total_steps()
            if self._run_mode == 'recurse':
                self._load_initial_state()
                self._recurse(0)
            elif self._run_mode == 'linear':
                self._load_initial_state()
                self._loop()
            else:
                self._single()

            if self._running:
                signals.progress('state', {'value': 'completed', 'state': 0})
            else:
                signals.progress('state', {'value': 'aborted', 'state': 0})

        except Exception as exc:
            signals.progress('state', {'value': 'error', 'state': -1})
            self._log.exception(exc)

        finally:
            self._running = False
