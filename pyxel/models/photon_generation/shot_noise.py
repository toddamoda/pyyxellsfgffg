"""Pyxel photon generator models."""
import logging
import numpy as np
import pyxel
from pyxel import check_type
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='seed', label='random seed', units='', validate=check_type(int))
# @pyxel.register(group='photon_generation', name='shot noise')
def add_shot_noise(detector: Detector,
                   random_seed: int = None):
    """Add shot noise to the number of photons.

    :param detector: Pyxel Detector object
    :param random_seed: int seed
    """
    logging.info('')
    if random_seed:                         # TODO: is this needed here?
        np.random.seed(random_seed)
    lambda_list = detector.photons.get_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    detector.photons.change_all_number(new_list)
