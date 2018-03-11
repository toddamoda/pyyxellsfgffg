"""Utility functions for the web sub-package."""
import logging
import os

import esapy_rpc as rpc
from esapy_rpc.rpc import SimpleSerializer

from pyxel import util
from pyxel.util import FitsFile
from pyxel.web import signals
# from pyxel.pipelines.detector_pipeline import PipelineAborted


def run_pipeline(processor, output_file=None, address_viewer=None):
    """TBW.

    :param processor:
    :param output_file:
    :param address_viewer
    :return:
    """
    try:
        signals.progress('state', {'value': 'running', 'state': 1})
        processor.detector.update_header()
        result = processor.pipeline.run(processor.detector)
    except util.PipelineAborted:
        signals.progress('state', {'value': 'aborted', 'state': 0})
        return
    except Exception as exc:
        signals.progress('state', {'value': 'error', 'state': -1})
        logging.exception(exc)
        return

    if result and output_file:
        try:
            output_file = os.path.abspath(output_file)
            output_file = util.apply_run_number(output_file)
            signals.progress('state', {'value': 'saving', 'state': 2})
            out = FitsFile(output_file)
            out.save(result.signal.astype('uint16'), header=processor.detector.header, overwrite=True)
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
