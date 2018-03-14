#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! CCD noise generator class."""
import numpy as np

from pyxel.detectors.detector import Detector
from pyxel.detectors.geometry import Geometry  # noqa: F401
from pyxel.pipelines.model_registry import registry


# from astropy import units as u


@registry.decorator('charge_collection', name='fix_pattern_noise', detector='ccd')
def add_fix_pattern_noise(detector: Detector,
                          pix_non_uniformity=None) -> Detector:
    """Add fix pattern noise caused by pixel non-uniformity during charge collection.

    :param detector:
    :param pix_non_uniformity: a path to a file
    :return:
    """
    new_detector = detector
    geo = new_detector.geometry  # type: Geometry

    pnu = np.loadtxt(pix_non_uniformity)
    pnu = pnu.reshape((geo.row, geo.col))

    pix_rows = new_detector.pixels.get_pixel_positions_ver()
    pix_cols = new_detector.pixels.get_pixel_positions_hor()

    charge_with_noise = np.zeros((geo.row, geo.col), dtype=float)
    charge_with_noise[pix_rows, pix_cols] = new_detector.pixels.get_pixel_charges()

    charge_with_noise *= pnu

    new_detector.pixels.update_from_2d_charge_array(charge_with_noise)

    return new_detector


@registry.decorator('charge_measurement', name='output_node_noise', detector='ccd')
def add_output_node_noise(detector: Detector, std_deviation: float) -> Detector:
    """Adding noise to signal array of detector output node using normal random distribution.

    detector Signal unit: Volt
    :param detector:
    :param std_deviation:
    :return: detector output signal with noise
    """
    new_detector = detector

    signal_mean_array = new_detector.signal.astype('float64')
    sigma_array = std_deviation * np.ones(new_detector.signal.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)

    new_detector.signal = signal

    return new_detector
