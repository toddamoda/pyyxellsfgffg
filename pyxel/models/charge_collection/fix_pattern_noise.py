#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Fix pattern noise model."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector
from pyxel.detectors.geometry import Geometry  # noqa: F401

# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_collection', name='fixed_pattern_noise', detector='ccd')
def add_fix_pattern_noise(detector: Detector,
                          pix_non_uniformity=None) -> Detector:
    """Add fix pattern noise caused by pixel non-uniformity during charge collection.

    :param detector:
    :param pix_non_uniformity: a path to a file
    :return:
    """
    logging.info('')
    geo = detector.geometry  # type: Geometry

    pnu = np.loadtxt(pix_non_uniformity)
    pnu = pnu.reshape((geo.row, geo.col))

    detector.pixels.array *= pnu

    return detector
