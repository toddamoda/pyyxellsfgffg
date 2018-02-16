
import logging
import argparse
import yaml
import functools
import os

from pathlib import Path

import pyxel
from pyxel.util import FitsFile
import pyxel.pipelines.processor

from pyxel.web import signals
from pyxel.web import webapp
from ast import literal_eval

import esapy_rpc as rpc
from esapy_rpc.rpc import SimpleSerializer

CFG_DEFAULT = {}


class API:

    def __init__(self, processor):
        self.processor = processor

    def atts(self, entry):
        result = []
        for key in entry:
            result.append('%s="%s"' % (key, entry[key]))
        return ' '.join(result)

    def items(self):

        with open('gui.yaml', 'r') as fd:
            cfg = yaml.load(fd)

        return cfg

    # @staticmethod
    # def pause():
    #     signals.dispatcher.emit(sender='sequencer', signal=signals.PAUSE)()
    #
    # @staticmethod
    # def resume():
    #     signals.dispatcher.emit(sender='sequencer', signal=signals.RESUME)()
    #
    # @staticmethod
    # def set_sequencer_state(signal):
    #     signals.dispatcher.emit(sender='sequencer', signal=signal)()
    #
    # @staticmethod
    # def run_sequencer(schema_file, config_file):
    #     signals.dispatcher.emit(sender='api', signal=signals.RUN_APPLICATION)(schema_file, config_file)
    #
    # @staticmethod
    # def state_change(measurement: str, fields: dict, tags: t.Optional[dict] = None):
    #     msg = {
    #         'type': 'hk',
    #         'measurement': measurement,
    #         'fields': fields,
    #         'tags': tags,
    #     }
    #     webapp.WebSocketHandler.announce(msg)

    def run_pipeline(self, output_file=None):
        try:
            signals.progress('state', {'value': 'running', 'state': 1})
            result = self.processor.pipeline.run_pipeline(self.processor.detector)
        except Exception as exc:
            signals.progress('state', {'value': 'error', 'state': -1})
            logging.exception(exc)
            return

        # print('Pipeline completed.')
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

    def progress(self, idn: str, fields: dict):
        msg = {
            'type': 'progress',
            'id': idn,
            'fields': fields,
        }
        webapp.WebSocketHandler.announce(msg)

    def get_setting(self, key):
        obj_atts = key.split('.')
        att = obj_atts[-1]
        obj = self.processor
        for part in obj_atts[:-1]:
            if isinstance(obj, functools.partial) and part == 'arguments':
                obj = obj.keywords
            else:
                obj = getattr(obj, part)
        if att == 'image':
            att = '_image'

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

        if att == 'photons':
            setattr(obj, '_photon_mean', value)
            setattr(obj, '_image', None)

        elif att == 'image':
            value = FitsFile(value)
            setattr(obj, '_photon_mean', None)
            setattr(obj, '_image', value.data)
            return

        if isinstance(obj, dict) and att in obj:
            obj[att] = value
        else:
            setattr(obj, att, value)
        self.get_setting(key)


def run_web_server(input_filename, port=8888):
    config_path = Path(__file__).parent.parent.joinpath(input_filename)
    cfg = pyxel.load_config(config_path)
    processor = cfg['process']

    controller = API(processor)
    signals.dispatcher.connect(sender='api', signal=signals.RUN_PIPELINE, callback=controller.run_pipeline)
    signals.dispatcher.connect(sender='api', signal=signals.SET_SETTING, callback=controller.set_setting)
    signals.dispatcher.connect(sender='api', signal=signals.GET_SETTING, callback=controller.get_setting)
    signals.dispatcher.connect(sender='*', signal=signals.PROGRESS, callback=controller.progress)
    # signals.dispatcher.connect(sender='*', signal=signals.HK_SIGNAL, callback=API.state_change)
    # signals.dispatcher.connect(sender='*', signal=signals.PROGRESS, callback=API.progress)
    # signals.dispatcher.connect(sender='sequencer', signal=signals.HK_SIGNAL, callback=API.state_change)

    api = webapp.WebApplication(controller)
    thread = webapp.TornadoServer(api, ('0.0.0.0', port))
    try:
        thread.run()
    except KeyboardInterrupt:
        logging.info("Exiting web server")
    finally:
        thread.stop()


def main():
    """ main entry point. """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    # Required positional arguments
    parser.add_argument('-c', '--config',
                        help='Configuration file to load (YAML or INI)')

    # # Required positional arguments
    # parser.add_argument('-o', '--output',
    #                     help='output file')

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(name)s - %(funcName)s - %(thread)d - %(levelname)s - %(message)s'
    del logging.root.handlers[:]
    logging.basicConfig(level=log_level, format=log_format)

    run_web_server(opts.config)


if __name__ == '__main__':
    main()
