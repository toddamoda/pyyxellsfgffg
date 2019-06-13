#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Fix pattern noise model."""
import logging
import numpy as np
from pyxel import check_path
from pyxel.detectors.detector import Detector
from pyxel.detectors.geometry import Geometry  # noqa: F401

# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def fix_pattern_noise(detector: Detector,
                      pixel_non_uniformity=None):
    """Add fix pattern noise caused by pixel non-uniformity during charge collection.

    :param detector: Pyxel Detector object
    :param pixel_non_uniformity: path to an ascii file with and array
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry  # type: Geometry

    if pixel_non_uniformity is not None:
        if '.npy' in pixel_non_uniformity:
            pnu = np.load(pixel_non_uniformity)
        else:
            pnu = np.loadtxt(pixel_non_uniformity)
    else:
        filename = 'data/pixel_non_uniformity.npy'
        if check_path(filename):
            logger.warning('"pix_non_uniformity" file is not defined, '
                           'using array from file: ' + filename)
            pnu = np.load(filename)
        else:
            logger.warning('"pix_non_uniformity" file is not defined, '
                           'generated random array to file: ' + filename)
            # pnu = 0.99 + np.random.random((geo.row, geo.col)) * 0.02
            pnu = np.random.normal(loc=1.0, scale=0.03, size=(geo.row, geo.col))
            np.save(filename, pnu)

    pnu = pnu.reshape((geo.row, geo.col))

    detector.pixel.array = detector.pixel.array.astype(np.float64) * pnu      # TODO: dtype!
