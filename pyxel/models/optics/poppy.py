"""Pyxel photon generator models."""
import logging
import poppy as op
import numpy as np
from scipy import signal
# import matplotlib.pyplot as plt
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='image_file', label='', validate=check_path)
def optical_psf(detector: Detector,
                wavelength: float,
                pixelscale: float,
                fov_pixels: int,
                optical_system: list,
                fov_arcsec: float = None):
    """POPPY (Physical Optics Propagation in PYthon) model wrapper.

    It calculates the optical Point Spread Function of an optical system.

    Documentation:
    https://poppy-optics.readthedocs.io/en/stable/index.html

    detector: Detector
        Pyxel Detector object.
    wavelength: float
        Wavelength of incoming light in meters.
    pixelscale: float
        Pixel scale on detector plane (micron/pixel or arcsec/pixel).
        Defines sampling resolution of PSF.
    fov_pixels: int
        Field Of View on detector plane in pixels.
    optical_system:
        List of optical elements before detector with their specific arguments.

        See details about POPPY Optical Element classes:
        https://poppy-optics.readthedocs.io/en/stable/available_optics.html

        Supported optical elements:

        - ``CircularAperture``
        - ``SquareAperture``
        - ``RectangularAperture``
        - ``HexagonAperture``
        - ``ThinLens``
        - ``SecondaryObscuration``
        - ``ZernikeWFE``
        - ``SineWaveWFE``

        .. code-block:: yaml

          # YAML config: arguments of POPPY optical_system
          optical_system:
          - item: CircularAperture
            radius: 1.5
          - item: ThinLens
            radius: 1.2
            nwaves: 1
          - item: ZernikeWFE
            radius: 0.8
            coefficients: [0.1e-6, 3.e-6, -3.e-6, 1.e-6, -7.e-7, 0.4e-6, -2.e-6]
            aperture_stop: false

    fov_arcsec: float, optional
        Field Of View on detector plane in arcsec.
    """
    logging.info('')

    if fov_arcsec:                      # TODO
        raise NotImplementedError

    osys = op.OpticalSystem(npix=1000)  # default: 1024

    for item in optical_system:
        if item['item'] == 'CircularAperture':
            optical_item = op.CircularAperture(radius=item['radius'])
        elif item['item'] == 'ThinLens':
            optical_item = op.ThinLens(nwaves=item['nwaves'],
                                       reference_wavelength=wavelength,
                                       radius=item['radius'])
        elif item['item'] == 'SquareAperture':
            optical_item = op.SquareAperture(size=item['size'])
        elif item['item'] == 'RectangularAperture':
            optical_item = op.RectangleAperture(width=item['width'], height=item['height'])  # m
        elif item['item'] == 'HexagonAperture':
            optical_item = op.HexagonAperture(side=item['side'])
        elif item['item'] == 'SecondaryObscuration':
            optical_item = op.SecondaryObscuration(secondary_radius=item['secondary_radius'],
                                                   n_supports=item['n_supports'],
                                                   support_width=item['support_width'])      # cm
        elif item['item'] == 'ZernikeWFE':
            optical_item = op.ZernikeWFE(radius=item['radius'],
                                         coefficients=item['coefficients'],         # list of floats
                                         aperture_stop=item['aperture_stop'])       # bool
        elif item['item'] == 'SineWaveWFE':
            optical_item = op.SineWaveWFE(spatialfreq=item['spatialfreq'],      # 1/m
                                          amplitude=item['amplitude'],          # um
                                          rotation=item['rotation'])
        else:
            raise NotImplementedError
        osys.add_pupil(optical_item)

    osys.add_detector(pixelscale=pixelscale,
                      # fov_arcsec=None,
                      fov_pixels=fov_pixels)

    psf = osys.calc_psf(wavelength=wavelength,
                        return_intermediates=True,
                        # return_final=True,
                        display_intermediates=True,
                        normalize="last")                   # TODO NORMALIZATION!!!!

    # psf[0][0].data == psf[1][-1].intensity

    # plt.figure()
    # ax_orig = plt.gca()
    # ax_orig.imshow(detector.photons.array, cmap='gray')
    # ax_orig.set_title('Original')
    # ax_orig.set_axis_off()

    # Convolution
    a = detector.photons.array.shape[0]
    b = detector.photons.array.shape[1]
    new_shape = (a + 2 * fov_pixels, b + 2 * fov_pixels)
    array = np.zeros(new_shape, detector.photons.array.dtype)
    roi = slice(fov_pixels, fov_pixels + a), slice(fov_pixels, fov_pixels + b)
    array[roi] = detector.photons.array

    array = signal.convolve2d(array,
                              psf[0][0].data,
                              mode='same',
                              boundary='fill', fillvalue=0)
    detector.photons.new_array(array)

    # plt.figure()
    # ax_int = plt.gca()
    # ax_int.imshow(array, cmap='gray')
    # ax_int.set_title('Convolution with intensity')
    # ax_int.set_axis_off()

    # plt.show()

    # conv_with_wavefront = signal.convolve2d(detector.photons.array, psf[1][-1].wavefront,
    #                                         mode='same', boundary='fill', fillvalue=0)
