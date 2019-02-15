"""Pyxel photon generator models: photon shot noise."""
import numpy as np
import pyxel
from pyxel.detectors import Detector


@pyxel.validate
@pyxel.argument(name='seed', label='random seed', units='', validate=pyxel.check_type(int))
def shot_noise(detector: Detector, random_seed: int = None):
    """Add shot noise to the number of photons per pixel.

    :param detector: Pyxel Detector object
    :param random_seed: int seed
    """
    pyxel.logger()
    if random_seed:
        np.random.seed(random_seed)
    detector.photons.array = np.random.poisson(lam=detector.photons.array)
