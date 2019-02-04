"""Utility functions."""

import numpy as np
# from pyxel.util.outputs import image, numpy_array, hist_plot, graph_plot, show_plots
from pyxel.util.outputs import Outputs, apply_run_number

__all__ = ['convert_to_int', 'round_convert_to_int',
           'PipelineAborted',
           'Outputs',
           'apply_run_number']


class PipelineAborted(Exception):
    """Exception to force the pipeline to stop processing."""

    def __init__(self, message: str = None, errors=None):
        """TBW."""
        super().__init__(message)
        self.errors = errors


def round_convert_to_int(input_array: np.ndarray):
    """Round list of floats in numpy array and convert to integers.

    Use on data before adding into DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    array = input_array.astype(float)
    array = np.rint(array)
    array = array.astype(int)
    return array


def convert_to_int(input_array: np.ndarray):
    """Convert numpy array to integer.

    Use on data after getting it from DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    return input_array.astype(int)
