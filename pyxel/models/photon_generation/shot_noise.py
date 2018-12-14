"""Pyxel photon generator models."""
import logging
import numpy as np
import esapy_config as om
import pyxel
from pyxel.detectors.detector import Detector


@om.validate
@om.argument(name='seed', label='random seed', units='', validate=om.check_type_function(int))
@pyxel.register(group='photon_generation', name='shot noise')
def add_shot_noise(detector: Detector,
                   random_seed: int = 0) -> Detector:
    """Add shot noise to number of photons.

    :param detector:
    :param random_seed:
    :return:
    """
    logging.info('')

    if random_seed:
        np.random.seed(random_seed)
    lambda_list = detector.photons.get_photon_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    detector.photons.change_all_number(new_list)

    return detector
