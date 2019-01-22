"""Pyxel photon generator models."""
import logging
import poppy as op
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
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

    radius1 = 1    # meter
    radius2 = 3    # meter

    nwaves = 1   # defocus

    # fov_arcsec = 10.
    fov_pixels = 30      # FOV: array with shape 2 pix x 2 pix
    pixelscale = 0.1

    wavelength = 2e-6   # wavelength in microns

    osys = op.OpticalSystem(npix=1000)      # TODO: this should be: max(detector.photon.array.shape)

    osys.add_pupil(op.CircularAperture(radius=radius1))

    # osys.add_pupil(op.CircularAperture(radius=radius2))
    osys.add_pupil(op.ThinLens(nwaves=nwaves,
                               reference_wavelength=wavelength,
                               radius=radius2))

    osys.add_detector(pixelscale=pixelscale,
                      # fov_arcsec=None,
                      fov_pixels=fov_pixels)

    psf = osys.calc_psf(wavelength=wavelength,
                        return_intermediates=True,
                        # return_final=True,
                        display_intermediates=True,
                        normalize="last")

    plt.figure()
    plt.subplot(3, 3, 1, title='amplitude 0')
    plt.imshow(psf[1][0].amplitude, cmap='gray')
    plt.subplot(3, 3, 4, title='amplitude 1')
    plt.imshow(psf[1][1].amplitude, cmap='gray')
    plt.subplot(3, 3, 7, title='amplitude 2')
    plt.imshow(psf[1][2].amplitude, cmap='gray')

    plt.subplot(3, 3, 2, title='phase 0')
    plt.imshow(psf[1][0].phase)
    plt.subplot(3, 3, 5, title='phase 1')
    plt.imshow(psf[1][1].phase)
    plt.subplot(3, 3, 8, title='phase 2')
    plt.imshow(psf[1][2].phase)

    plt.subplot(3, 3, 3, title='intensity 0')
    plt.imshow(psf[1][0].intensity, cmap='gray')
    plt.subplot(3, 3, 6, title='intensity 1')
    plt.imshow(psf[1][1].intensity, cmap='gray')
    plt.subplot(3, 3, 9, title='intensity 2')
    plt.imshow(psf[1][2].intensity, cmap='gray')

    # plt.figure()
    # op.display_psf(psf[0], title='display_psf')

    plt.figure()
    plt.imshow(np.log(psf[1][2].intensity))


    # from scipy import misc
    # ascent = misc.ascent()
    # scharr = np.array(
    #     [[-3 - 3j, 0 - 10j, +3 - 3j],
    #      [-10 + 0j, 0 + 0j, +10 + 0j],
    #      [-3 + 3j, 0 + 10j, +3 + 3j]])  # Gx + j*Gy
    # grad = signal.convolve2d(ascent, scharr, mode='same', boundary='fill', fillvalue=0)

    conv_with_wavefront = signal.convolve2d(detector.photons.array, psf[1][2].wavefront,
                                            mode='same', boundary='fill', fillvalue=0)
    conv_with_intensity = signal.convolve2d(detector.photons.array, psf[1][2].intensity,
                                            mode='same', boundary='fill', fillvalue=0)


    plt.figure()
    ax_orig = plt.gca()
    ax_orig.imshow(detector.photons.array, cmap='gray')
    ax_orig.set_title('Original')
    ax_orig.set_axis_off()

    plt.figure()
    ax_int = plt.gca()
    ax_int.imshow(conv_with_intensity, cmap='gray')
    ax_int.set_title('Convolution with intensity')
    ax_int.set_axis_off()

    plt.figure()
    ax_mag = plt.gca()
    ax_mag.imshow(np.absolute(conv_with_wavefront), cmap='gray')
    ax_mag.set_title('Magnitude')
    ax_mag.set_axis_off()

    plt.figure()
    ax_ang = plt.gca()
    ax_ang.imshow(np.angle(conv_with_wavefront), cmap='hsv')   # hsv is cyclic, like angles
    ax_ang.set_title('Angle')
    ax_ang.set_axis_off()

    plt.show()

    pass
