"""Utility functions for the web sub-package."""
import importlib
import logging
import os
import glob
from ast import literal_eval

import esapy_rpc as rpc
from esapy_rpc.rpc import SimpleSerializer

from pyxel.web import webapp
from pyxel.util import FitsFile
from pyxel.web import signals
from pyxel.pipelines.detector_pipeline import PipelineAborted


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


def eval_range(values):
    """Evaluates a string representation of a list or numpy array.

    :param values:
    :return: list
    """
    if values:
        if isinstance(values, str):
            if 'numpy' in values:
                locals_dict = {'numpy': importlib.import_module('numpy')}
                globals_dict = None
                values = eval(values, globals_dict, locals_dict)
                # NOTE: the following casting is to ensure JSON serialization works
                # JSON does not accept numpy.int* or numpy.float* types.
                if values.dtype == float:
                    values = [float(value) for value in values]
                elif values.dtype == int:
                    values = [int(value) for value in values]
                else:
                    logging.warning('numpy data type is not a float or int: %r', values)
            else:
                values = eval(values)

        if not isinstance(values, (list, tuple)):
            values = list(values)
    else:
        values = []
    return values


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
