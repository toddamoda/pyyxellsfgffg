"""Pyxel photon generator models."""
import logging
import poppy as op
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='image_file', label='', validate=check_path)
def poppy(detector: Detector):
    """POPPY (Physical Optics Propagation in PYthon) model wrapper.

    https://poppy-optics.readthedocs.io/en/stable/index.html

    :param detector: Pyxel Detector object
    """
    logging.info('')
    # geo = detector.geometry

    radius = 3
    fov_arcsec = 5.
    pixelscale = 0.01
    wavelength = 2e-6   # um

    osys = op.OpticalSystem()
    osys.add_pupil(op.CircularAperture(radius=radius))                  # pupil radius in meters
    osys.add_detector(pixelscale=pixelscale, fov_arcsec=fov_arcsec)     # image plane coordinates in arcseconds

    psf = osys.calc_psf(wavelength=wavelength, display_intermediates=True)           # wavelength in microns
    op.display_psf(psf, title='The Airy Function')

    detector.photons.array = psf[0].data * 1.e10
    # detector.photons.array += psf[0].data
    # detector.photons.array *= psf[0].data
    pass
