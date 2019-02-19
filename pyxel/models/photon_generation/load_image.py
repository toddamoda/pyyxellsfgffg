"""Pyxel photon generator models."""
import logging
import typing as t
from astropy.io import fits
import pyxel
from pyxel import check_type, check_path
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='image_file', label='fits file', validate=check_path)
@pyxel.argument(name='fit_image_to_det', label='fitting image to detector', validate=check_type(bool))
@pyxel.argument(name='convert_to_photons', label='convert ADU values to photon numbers', validate=check_type(bool))
def load_image(detector: Detector,
               image_file: str,
               fit_image_to_det: bool = False,
               position: t.Optional[list] = None,                        # TODO Too many arguments
               convert_to_photons: bool = False):
    r"""Load FITS file as a numpy array and add to the detector as input image.

    :param detector: Pyxel Detector object
    :param image_file: path to FITS image file
    :param fit_image_to_det: fitting image to detector shape (Geometry.row, Geometry.col)
    :param position: indices of starting row and column, used when fitting image to detector
    :param convert_to_photons: if ``True``, the model converts the values of loaded image array from ADU to
        photon numbers for each pixel using the Photon Transfer Function:
        :math:`PTF = QE \cdot \eta \cdot S_{v} \cdot amp \cdot a_{1} \cdot a_{2}`
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    image = fits.getdata(image_file)

    if fit_image_to_det:
        if position is None:
            position = [0, 0]
        geo = detector.geometry
        image = image[slice(position[0], position[0]+geo.row), slice(position[1], position[1]+geo.col)]

    detector.input_image = image
    photon_array = image

    if convert_to_photons:
        cht = detector.characteristics
        photon_array = photon_array / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)

    detector.photons.new_array(photon_array)
