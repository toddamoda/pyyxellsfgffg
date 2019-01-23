"""Pyxel photon generator models."""
import logging
import poppy as op
from scipy import signal
import matplotlib.pyplot as plt
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='image_file', label='', validate=check_path)
def optical_psf(detector: Detector,
                wavelength: float,
                pixelscale: float,
                fov_pixels: int,
                optical_system,
                fov_arcsec: float = None
                ):
    """POPPY (Physical Optics Propagation in PYthon) model wrapper.

    https://poppy-optics.readthedocs.io/en/stable/index.html

    :param detector: Pyxel Detector object
    :param wavelength:
    :param pixelscale:
    :param fov_pixels: Field Of View on detector plane in pixels
    :param fov_arcsec: Field Of View on detector plane in arcsec
    :return:
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

    plt.figure()
    ax_orig = plt.gca()
    ax_orig.imshow(detector.photons.array, cmap='gray')
    ax_orig.set_title('Original')
    ax_orig.set_axis_off()

    # Convolution
    detector.photons.array = signal.convolve2d(detector.photons.array, psf[0][0].data,
                                               mode='same', boundary='fill', fillvalue=0)

    plt.figure()
    ax_int = plt.gca()
    ax_int.imshow(detector.photons.array, cmap='gray')
    ax_int.set_title('Convolution with intensity')
    ax_int.set_axis_off()

    plt.show()

    # conv_with_wavefront = signal.convolve2d(detector.photons.array, psf[1][2].wavefront,
    #                                         mode='same', boundary='fill', fillvalue=0)

    # plt.figure()
    # plt.subplot(3, 3, 1, title='amplitude 0')
    # plt.imshow(psf[1][0].amplitude, cmap='gray')
    # plt.subplot(3, 3, 4, title='amplitude 1')
    # plt.imshow(psf[1][1].amplitude, cmap='gray')
    # plt.subplot(3, 3, 7, title='amplitude 2')
    # plt.imshow(psf[1][2].amplitude, cmap='gray')
    #
    # plt.subplot(3, 3, 2, title='phase 0')
    # plt.imshow(psf[1][0].phase)
    # plt.subplot(3, 3, 5, title='phase 1')
    # plt.imshow(psf[1][1].phase)
    # plt.subplot(3, 3, 8, title='phase 2')
    # plt.imshow(psf[1][2].phase)
    #
    # plt.subplot(3, 3, 3, title='intensity 0')
    # plt.imshow(psf[1][0].intensity, cmap='gray')
    # plt.subplot(3, 3, 6, title='intensity 1')
    # plt.imshow(psf[1][1].intensity, cmap='gray')
    # plt.subplot(3, 3, 9, title='intensity 2')
    # plt.imshow(psf[1][2].intensity, cmap='gray')

    # plt.figure()
    # op.display_psf(psf[0], title='display_psf')
    # plt.figure()
    # plt.imshow(np.log(psf[1][2].intensity))

    # plt.figure()
    # ax_mag = plt.gca()
    # ax_mag.imshow(np.absolute(conv_with_wavefront), cmap='gray')
    # ax_mag.set_title('Magnitude')
    # ax_mag.set_axis_off()
    #
    # plt.figure()
    # ax_ang = plt.gca()
    # ax_ang.imshow(np.angle(conv_with_wavefront), cmap='hsv')   # hsv is cyclic, like angles
    # ax_ang.set_title('Angle')
    # ax_ang.set_axis_off()
