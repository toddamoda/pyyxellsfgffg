"""Pyxel dummy model for demo."""
import logging
import numpy as np
import pyxel
from pyxel.detectors import Detector


@pyxel.validate
@pyxel.argument(name='number', label='label of arg',
                units='', validate=pyxel.check_type(int))
def new_model(detector: Detector, number: int = None):
    """My new dummy model.

    :param detector: Pyxel Detector object
    :param number: an integer
    """
    log = logging.getLogger('pyxel')
    log.info('')
    if number:
        print('number = ', str(number))
    detector.pixels.array *= np.random.rand()
