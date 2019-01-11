"""Pyxel photon generator models."""
import logging
from astropy.io import fits
import pyxel
from pyxel import check_type, check_path
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='image_file', label='fits file', validate=check_path)
@pyxel.argument(name='row0', label='first row', validate=check_type(int))
@pyxel.argument(name='col0', label='first column', validate=check_type(int))
@pyxel.argument(name='load_full_image', label='full image (updates geometry)', validate=check_type(bool))
# @pyxel.register(group='photon_generation', name='load image')
def load_image(detector: Detector,
               image_file: str,
               row0: int = 0,
               col0: int = 0,
               load_full_image: bool = False
               ):
    """TBW.

    :param detector:
    :param image_file:
    :param row0:
    :param col0:
    :param load_full_image:
    """
    logging.info('')
    geo = detector.geometry

    image = fits.getdata(image_file)
    if load_full_image:
        row0, col0 = 0, 0
        geo.row, geo.col = image.shape
    image = image[row0: row0 + geo.row, col0: col0 + geo.col]
    detector.input_image = image
