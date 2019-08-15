"""Readout noise model."""
import logging
import numpy as np
from pyxel.detectors.detector import Detector

# from astropy import units as u


# @validators.validate
# @config.argument(name='', label='', units='', validate=)

def output_node_noise(detector: Detector,
                      std_deviation: float,
                      random_seed: int = None):
    """Adding noise to signal array of detector output node using normal random distribution.

    detector Signal unit: Volt

    :param detector: Pyxel Detector object
    :param std_deviation: standard deviation
    :param random_seed: seed
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    if random_seed:
        np.random.seed(random_seed)

    signal_mean_array = detector.signal.array.astype('float64')
    sigma_array = std_deviation * np.ones(signal_mean_array.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)

    detector.signal.array = signal
