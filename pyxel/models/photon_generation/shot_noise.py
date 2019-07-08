"""Pyxel photon generator models: photon shot noise."""
import logging

import numpy as np

from pyxel.detectors import Detector
from ...util import validators, config, checkers


@validators.validate
@config.argument(name='seed', label='random seed', units='', validate=checkers.check_type(int))
def shot_noise(detector: Detector, random_seed: int = None):
    """Add shot noise to the number of photon per pixel.

    :param detector: Pyxel Detector object
    :param random_seed: int seed
    """
    log = logging.getLogger('pyxel')
    log.info('')
    if random_seed:
        np.random.seed(random_seed)
    detector.photon.array = np.random.poisson(lam=detector.photon.array)
