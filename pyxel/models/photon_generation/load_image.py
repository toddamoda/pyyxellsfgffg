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
@pyxel.argument(name='convert_to_photons', label='convert image values to photon numbers', validate=check_type(bool))
def load_image(detector: Detector,
               image_file: str,
               row0: int = 0,
               col0: int = 0,
               load_full_image: bool = False,
               convert_to_photons: bool = False):
    r"""Load FITS file as a numpy array and add to the detector as input image.

    :param detector: Pyxel Detector object
    :param image_file: path to FITS image file
    :param row0: index of starting row
    :param col0: index of starting column
    :param load_full_image: use this to load the full image and update the detector geometry based on image size
    :param convert_to_photons: if ``True``, the model will generate photon numbers per pixel
        from detector.input_image array using the Photon Transfer Function:
        :math:`PTF = QE \cdot \eta \cdot S_{v} \cdot amp \cdot a_{1} \cdot a_{2}`
    """
    logging.info('')
    geo = detector.geometry
    cht = detector.characteristics

    image = fits.getdata(image_file)
    if load_full_image:
        row0, col0 = 0, 0
        geo.row, geo.col = image.shape

    image = image[row0: row0 + geo.row, col0: col0 + geo.col]
    detector.input_image = image

    if convert_to_photons:
        detector.photons.array = detector.input_image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
