"""Pyxel photon generator models."""
import logging
# from astropy.io import fits
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='image_file', label='', validate=check_path)
def alignment(detector: Detector):
    """Optical alignment.

    :param detector: Pyxel Detector object
    """
    logging.info('')
    geo = detector.geometry
    rows, cols = detector.photons.array.shape
    row0 = int((rows - geo.row) / 2)
    col0 = int((cols - geo.col) / 2)
    if row0 < 0 or col0 < 0:
        raise ValueError
    aligned_optical_image = detector.photons.array[slice(row0, row0+geo.row), slice(col0, col0+geo.col)]
    detector.photons.new_array(aligned_optical_image)
    pass
