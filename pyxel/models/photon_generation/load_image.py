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
@pyxel.argument(name='fit_image_to_det', label='fitting image to detector', validate=check_type(bool))
@pyxel.argument(name='convert_to_photons', label='convert ADU values to photon numbers', validate=check_type(bool))
def load_image(detector: Detector,
               image_file: str,
               fit_image_to_det: bool = False,
               row0: int = 0,
               col0: int = 0,
               convert_to_photons: bool = False):
    r"""Load FITS file as a numpy array and add to the detector as input image.

    :param detector: Pyxel Detector object
    :param image_file: path to FITS image file
    :param fit_image_to_det: fitting image to detector shape (Geometry.row, Geometry.col)
    :param row0: index of starting row, used when fitting image to detector
    :param col0: index of starting column, used when fitting image to detector
    :param convert_to_photons: if ``True``, the model converts the values of loaded image array from ADU to
        photon numbers for each pixel using the Photon Transfer Function:
        :math:`PTF = QE \cdot \eta \cdot S_{v} \cdot amp \cdot a_{1} \cdot a_{2}`
    """
    logging.info('')
    image = fits.getdata(image_file)

    if fit_image_to_det:
        geo = detector.geometry
        image = image[slice(row0, row0 + geo.row), slice(col0, col0 + geo.col)]

    detector.input_image = image

    if convert_to_photons:
        cht = detector.characteristics
        detector.photons.array = detector.input_image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
    else:
        detector.photons.array = detector.input_image
