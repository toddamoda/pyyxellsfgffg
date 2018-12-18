#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Readout electronics model."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector
# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def simple_digitization(detector: Detector) -> Detector:
    """Create an image array from signal array.

    :param detector:
    :return: detector:
    """
    logging.info('')
    # floor of signal values element-wise (quantization)
    array = np.floor(detector.signal.array)
    # convert floats to integers
    detector.image.array = array.astype('uint16')

    return detector
