#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! CCD noise generator class
"""
import copy
from astropy import units as u

import numpy as np

# from . import Model

from pyxel.detectors.ccd import CCDDetector

# from pyxel.models.tars.tars_v3 import TARS
# from pyxel.models.tars.tars_v3 import TARS_DIR
# from numpy import pi


def foo(ccd, cls, method_name, kwargs_init, kwargs_method):
    obj = cls(**kwargs_init)

    new_ccd = getattr(obj, method_name)(**kwargs_method)

    return new_ccd


def apply_shot_noise(ccd: CCDDetector) -> CCDDetector:
    """ Extract the shot noise

    :param photon_array: (unit photons)
    :return: (unit photons)
    """
    new_ccd = copy.deepcopy(ccd)

    new_ccd.photons = np.random.poisson(lam=new_ccd.photons.value) * u.ph

    return new_ccd


def add_fix_pattern_noise(ccd: CCDDetector) -> CCDDetector:

    new_ccd = copy.deepcopy(ccd)

    temp = new_ccd.charge
    temp2 = new_ccd.pix_non_uniformity

    new_ccd.charge = new_ccd.charge * new_ccd.pix_non_uniformity
    new_ccd.charge = np.int16(np.rint(new_ccd.charge))

    return new_ccd


def add_readout_noise(ccd: CCDDetector, readout_sigma: float) -> CCDDetector:
    """
    Adding readout noise to signal array using normal random distribution
    Signal unit: DN
    :param ccd:
    :param readout_sigma:
    :return: signal with readout noise
    """
    new_ccd = copy.deepcopy(ccd)

    signal_mean_array = new_ccd.signal_updated.astype('float64')
    sigma_readout_array = readout_sigma * np.ones(new_ccd.signal.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_readout_array)
    new_ccd.signal = np.int16(np.rint(signal)) * u.adu

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
