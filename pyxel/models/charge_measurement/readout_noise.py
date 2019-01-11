#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Readout noise model."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector

# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_measurement', name='output_node_noise', detector='ccd')
def output_node_noise(detector: Detector,
                      std_deviation: float,
                      random_seed: int = None):
    """Adding noise to signal array of detector output node using normal random distribution.

    detector Signal unit: Volt
    :param detector:
    :param std_deviation:
    :param random_seed:
    :return: detector output signal with noise
    """
    logging.info('')
    if random_seed:
        np.random.seed(random_seed)

    signal_mean_array = detector.signal.array.astype('float64')
    sigma_array = std_deviation * np.ones(signal_mean_array.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)

    detector.signal.array = signal
