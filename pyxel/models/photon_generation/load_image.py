"""Pyxel photon generator models."""
import os
import logging
from astropy.io import fits
import esapy_config as om
import pyxel
from pyxel.detectors.detector import Detector


@om.validate
@om.argument(name='image_file', label='fits file', validate=os.path.exists)
@om.argument(name='row0', label='first row', validate=om.check_type_function(int))
@om.argument(name='col0', label='first column', validate=om.check_type_function(int))
@om.argument(name='load_full_image', label='full image (updates geometry)', validate=om.check_type_function(bool))
@pyxel.register(group='photon_generation', name='load image')
def load_image(detector: Detector,
               image_file: str,
               row0: int = 0,
               col0: int = 0,
               load_full_image: bool = False
               ) -> Detector:
    """TBW.

    :param detector:
    :param image_file:
    :param row0:
    :param col0:
    :param load_full_image:
    :return:
    """
    logging.info('')
    geo = detector.geometry

    image = fits.getdata(image_file)
    if load_full_image:
        row0, col0 = 0, 0
        geo.row, geo.col = image.shape
    image = image[row0: row0 + geo.row, col0: col0 + geo.col]
    detector.input_image = image

    return detector
