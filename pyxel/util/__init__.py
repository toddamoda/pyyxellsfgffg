"""Utility functions."""
import glob

from pyxel.util.fitsfile import FitsFile


class PipelineAborted(Exception):
    """Exception to force the pipeline to stop processing."""


# def load(yaml_filename):
#     """TBW.
#
#     :param yaml_filename:
#     :return:
#     """
#     from pyxel.io.yaml_processor import load
#     cfg = load(yaml_filename)
#     if 'parametric' in cfg:
#         parametric = cfg.pop('parametric')  # type: pyxel.pipelines.parametric.ParametricConfig
#     else:
#         parametric = None
#
#     processor = cfg[next(iter(cfg))]  # type: pyxel.pipelines.processor.Processor
#     return parametric, processor


def update_fits_header(header, key, value):
    """TBW.

    :param header:
    :param key:
    :param value:
    :return:
    """
    if not isinstance(value, (str, int, float)):
        value = '%r' % value

    if isinstance(value, str):
        value = value[0:24]

    if isinstance(key, (list, tuple)):
        key = '/'.join(key)

    key = key.replace('.', '/')[0:36]

    header[key] = value


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


__all__ = ['FitsFile', 'update_fits_header', 'apply_run_number']
