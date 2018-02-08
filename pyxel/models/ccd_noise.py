#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! CCD noise generator class
"""
import copy
from astropy import units as u
import numpy as np
# from pyxel.physics.photon import Photon

# from . import Model

from pyxel.detectors.ccd import CCD


def add_shot_noise(detector: CCD) -> CCD:
    """
    Add shot noise to number of photons
    :return:
    """
    new_detector = copy.deepcopy(detector)

    lambda_list = new_detector.photons.get_photon_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    new_detector.photons.change_all_number(new_list)

    return new_detector


def add_fix_pattern_noise(detector: CCD,
                          pix_non_uniformity=None,
                          percentage=None,
                          inplace=True) -> CCD:
    """
    Add fix pattern noise caused by pixel non-uniformity during charge collection
    :param detector:
    :param pix_non_uniformity:
    :param percentage:
    :param inplace:
    :return:
    """

    if inplace:
        new_detector = copy.deepcopy(detector)
        # new_detector = CCD(detector)
        # new_detector.to_pickle(filename)
        # new_detector.to_fits(filename)
        # CCD.from_fits(filename)
    else:
        new_detector = detector

    if pix_non_uniformity is None and percentage is not None:
        # generate_pixel_non_uniformity_data(percentage)   # TODO
        pass
    else:
        pix_non_uniformity = pix_non_uniformity.reshape((new_detector.row, new_detector.col))

    pix_rows = new_detector.pixels.get_pixel_positions_ver()
    pix_cols = new_detector.pixels.get_pixel_positions_hor()

    charge_with_noise = np.zeros((new_detector.row, new_detector.col), dtype=float)
    charge_with_noise[pix_rows, pix_cols] = new_detector.pixels.get_pixel_charges()

    charge_with_noise *= pix_non_uniformity

    new_detector.pixels.change_all_charges(np.rint(charge_with_noise).astype(int).flatten())
    # TODO add np.rint and np.int to Pixels class funcs

    return new_detector


def add_output_node_noise(ccd: CCD, std_deviation: float) -> CCD:
    """
    Adding noise to signal array of ccd output node using normal random distribution
    CCD Signal unit: Volt
    :param ccd:
    :param std_deviation:
    :return: ccd output signal with noise
    """
    new_ccd = copy.deepcopy(ccd)

    signal_mean_array = new_ccd.signal.astype('float64')
    sigma_array = std_deviation * np.ones(new_ccd.signal.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)
    new_ccd.signal = signal * u.V

    return new_ccd


# class CCDNoiseGenerator(Model):
#
#     def __init__(self, **kwargs):
#         super(CCDNoiseGenerator, self).__init__(**kwargs)
#         self.shot_noise = kwargs.get('shot_noise', False)
#         self.fix_pattern_noise = kwargs.get('fix_pattern_noise', False)
#         self.readout_noise = kwargs.get('readout_noise', False)
#         self.noise_file = kwargs.get('noise_file', '')
#
#     # SHOT NOISE
#     def add_shot_noise(self, photon_mean_array):
#         """
#         Adding shot noise to incident mean photon array using a Poisson random distribution
#         :param photon_mean_array: mean photon number
#         :type photon_mean_array: 2d numpy array
#         :return: photon array with shot noise
#         :rtype: 2d numpy array
#         .. note:: mean photon = lambda = sigma**2
#         """
#         self._shot_noise_array = photon_mean_array - np.random.poisson(lam=photon_mean_array)
#         photon_mean_array -= self._shot_noise_array
#
#         return photon_mean_array
#
#     # FIXED PATTERN NOISE (periodic)
#     def add_fix_pattern_noise(self, charge_array, noise_file):
#         """
#         Adding fix pattern noise to charge array using the same pixel non-uniformity array loaded from a text file
#         Charge unit: e-
#         :param charge_array: charge
#         :type charge_array: 2d numpy array
#         :return: modified charge with pixel non-uniformity
#         :rtype: 2d numpy array
#         .. todo:: calc and save PN value, check and regenerate the pixel non-uniformity array if PN value has changed
#         .. note:: pixel non-uniformity: Pn = sigma_signal(DN) / S(DN)  # percentage
#         """
#         m, n = charge_array.shape
#
#         self._pixel_non_uniform_array = np.fromfile(noise_file, dtype=float, sep=' ').reshape((m, n))
#         self._pixel_non_uniform_array = self._pixel_non_uniform_array.reshape((m, n))
#         charge_array = charge_array * self._pixel_non_uniform_array
#         charge_array = np.int16(np.rint(charge_array))
#
#         return charge_array
#
#     # READOUT NOISE
#     def add_readout_noise(self, signal_mean_array):
#         """
#         Adding readout noise to signal array using normal random distribution
#         Signal unit: DN
#         :param signal_mean_array: signal
#         :type signal_mean_array: 2d numpy array
#         :return: signal with readout noise
#         :rtype: 2d numpy array
#         """
#         m, n = signal_mean_array.shape
#         sigma_readout_array = self._readout_sigma * np.ones((m, n)).reshape((m, n))
#
#         self._readout_noise_array = np.random.normal(loc=0.0, scale=sigma_readout_array)
#         signal_mean_array = signal_mean_array.astype('float64') + self._readout_noise_array
#         signal_mean_array = np.int16(np.rint(signal_mean_array))
#
#         return signal_mean_array
