#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Readout noise model."""
import numpy as np
from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_registry import registry

# from astropy import units as u


@registry.decorator('charge_measurement', name='output_node_noise', detector='ccd')
def add_output_node_noise(detector: Detector,
                          std_deviation: float,
                          random_seed: int = None) -> Detector:
    """Adding noise to signal array of detector output node using normal random distribution.

    detector Signal unit: Volt
    :param detector:
    :param std_deviation:
    :param random_seed:
    :return: detector output signal with noise
    """
    new_detector = detector

    if random_seed:
        np.random.seed(random_seed)

    signal_mean_array = new_detector.signal.array.astype('float64')
    sigma_array = std_deviation * np.ones(signal_mean_array.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)

    new_detector.signal.array = signal

    return new_detector
