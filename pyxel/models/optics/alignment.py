"""Pyxel photon generator models."""
import logging
from pyxel.detectors.detector import Detector


# @validators.validate
# @config.argument(name='image_file', label='', validate=check_path)
def alignment(detector: Detector):
    """Optical alignment.

    :param detector: Pyxel Detector object
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    rows, cols = detector.photon.array.shape
    row0 = int((rows - geo.row) / 2)
    col0 = int((cols - geo.col) / 2)
    if row0 < 0 or col0 < 0:
        raise ValueError
    aligned_optical_image = detector.photon.array[slice(row0, row0 + geo.row), slice(col0, col0 + geo.col)]
    detector.photon.new_array(aligned_optical_image)
