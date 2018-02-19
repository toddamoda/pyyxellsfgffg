import yaml
import functools
import os
import threading
import logging
from ast import literal_eval


import esapy_rpc as rpc
from esapy_rpc.rpc import SimpleSerializer

from pyxel.util import FitsFile
from pyxel.web import signals
from pyxel.web import webapp


class API:

    def __init__(self, processor):
        self.processor = processor
        self.sequence = [
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
        ]
        signals.dispatcher.connect(sender='api', signal=signals.RUN_PIPELINE, callback=self.run_pipeline)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SETTING, callback=self.set_setting)
        signals.dispatcher.connect(sender='api', signal=signals.GET_SETTING, callback=self.get_setting)
        signals.dispatcher.connect(sender='api', signal=signals.SET_SEQUENCE, callback=self.set_sequence)
        signals.dispatcher.connect(sender='api', signal=signals.PROGRESS, callback=self.progress)

    def atts(self, entry):
        """ Appends all the GUI properties into a key="value" string
        that is inserted into the generated HTML template.

        This method is referenced in control.html template file.
        """
        result = []
        for key in entry:
            result.append('%s="%s"' % (key, entry[key]))
        return ' '.join(result)

    def items(self):
        """ Retrieves the dictionary object model that is defined
        in the gui.yaml configuration file.

        This method is referenced in control.html template file.
        """

        with open('gui.yaml', 'r') as fd:
            cfg = yaml.load(fd)

        return cfg

    def _run_pipeline(self, output_file=None):
        try:
            signals.progress('state', {'value': 'running', 'state': 1})
            result = self.processor.pipeline.run_pipeline(self.processor.detector)
        except Exception as exc:
            signals.progress('state', {'value': 'error', 'state': -1})
            logging.exception(exc)
            return

        if result and output_file:
            try:
                output_file = os.path.abspath(output_file)
                signals.progress('state', {'value': 'saving', 'state': 2})
                out = FitsFile(output_file)
                out.save(result.signal, header=None, overwrite=True)
            except Exception as exc:
                signals.progress('state', {'value': 'error', 'state': -2})
                logging.exception(exc)
                return

            try:
                signals.progress('state', {'value': 'loading', 'state': 3})
                address = ('localhost', 8891)
                client = rpc.ProxySocketClient(address,
                                               serializer=SimpleSerializer(),
                                               protocol=rpc.http.Client(action='POST'))
                proxy = rpc.ProxyObject(client)
                proxy.load_file(output_file)
            except Exception as exc:
                signals.progress('state', {'value': 'error', 'state': -3})
                logging.exception(exc)
                return

        signals.progress('state', {'value': 'completed', 'state': 0})

    def run_pipeline(self, output_file=None):
        threading.Thread(target=self.run_pipeline_sequence, args=[output_file]).start()

    def run_pipeline_sequence(self, output_file=None):
        is_sequence_enabled = False
        for seq_index, sequence in enumerate(self.sequence):
            if sequence['enabled']:
                key = sequence['key']
                values = sequence['values']
                for index, value in enumerate(values):
                    is_sequence_enabled = True
                    self.set_setting(key, value)
                    self.progress('sequence_%d' % seq_index, fields={'value': value, 'state': 1})
                    self._run_pipeline(output_file)
                    self.progress('sequence_%d' % seq_index, fields={'value': value, 'state': 0})

        if not is_sequence_enabled:
            # run a single time with the current settings
            self._run_pipeline(output_file)

    def progress(self, idn: str, fields: dict):
        msg = {
            'type': 'progress',
            'id': idn,
            'fields': fields,
        }
        webapp.WebSocketHandler.announce(msg)

    def set_sequence(self, index, key, values, enabled):
        if values:
            if isinstance(values, str):
                values = literal_eval(values)

            if not isinstance(values, (list, tuple)):
                values = [values]
        else:
            values = []
        self.sequence[index]['key'] = key
        self.sequence[index]['values'] = values
        self.sequence[index]['enabled'] = enabled

    def get_setting(self, key):
        obj_atts = key.split('.')
        att = obj_atts[-1]
        obj = self.processor
        for part in obj_atts[:-1]:
            if isinstance(obj, functools.partial) and part == 'arguments':
                obj = obj.keywords
            else:
                obj = getattr(obj, part)

        if isinstance(obj, dict) and att in obj:
            value = obj[att]
        else:
            value = getattr(obj, att)

        if isinstance(value, FitsFile):
            value = str(value.filename)

        msg = {
            'type': 'get',
            'id': key,
            'fields': {'value': value},
        }
        webapp.WebSocketHandler.announce(msg)
        return value

    def _eval(self, value):
        if isinstance(value, str):
            try:
                literal_eval(value)
            except (SyntaxError, ValueError, NameError):
                # ensure quotes incase of string literal value
                if value[0] == "'" and value[-1] == "'":
                    pass
                elif value[0] == '"' and value[-1] == '"':
                    pass
                else:
                    value = '"' + value + '"'

            value = literal_eval(value)
        return value

    def set_setting(self, key, value):

        if isinstance(value, list):
            for i, val in enumerate(value):
                value[i] = self._eval(val)
        else:
            value = self._eval(value)

        obj_atts = key.split('.')
        att = obj_atts[-1]
        obj = self.processor
        for part in obj_atts[:-1]:
            if isinstance(obj, functools.partial) and part == 'arguments':
                obj = obj.keywords
            else:
                obj = getattr(obj, part)

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)
        self.get_setting(key)
