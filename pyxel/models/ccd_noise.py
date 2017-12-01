#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! CCD noise generator class
"""
import numpy as np


class CcdNoiseGenerator(object):
    """
    Noise generator class for CCD detectors
    """
    def __init__(self):
        """
        Arrays storing the different noise components and standard deviations
        """
        self._shot_noise_array = 0
        self._pixel_non_uniform_array = 0
        self._readout_noise_array = 0
        self._readout_sigma = 0

    @property
    def readout_sigma(self):
        return self._readout_sigma

    @readout_sigma.setter
    def readout_sigma(self, new_sigma):
        self._readout_sigma = new_sigma

    # SHOT NOISE
    def add_shot_noise(self, photon_mean_array):
        """
        Adding shot noise to incident mean photon array using a Poisson random distribution
        :param photon_mean_array: mean photon number
        :type photon_mean_array: 2d numpy array
        :return: photon array with shot noise
        :rtype: 2d numpy array
        .. note:: mean photon = lambda = sigma**2
        """
        self._shot_noise_array = photon_mean_array - np.random.poisson(lam=photon_mean_array)
        photon_mean_array -= self._shot_noise_array

        return photon_mean_array

    # FIXED PATTERN NOISE (periodic)
    def add_fix_pattern_noise(self, charge_array, noise_file):
        """
        Adding fix pattern noise to charge array using the same pixel non-uniformity array loaded from a text file
        Charge unit: e-
        :param charge_array: charge
        :type charge_array: 2d numpy array
        :return: modified charge with pixel non-uniformity
        :rtype: 2d numpy array
        .. todo:: calc and save PN value, check and regenerate the pixel non-uniformity array if PN value has changed
        .. note:: pixel non-uniformity: Pn = sigma_signal(DN) / S(DN)  # percentage
        """
        m, n = charge_array.shape

        self._pixel_non_uniform_array = np.fromfile(noise_file, dtype=float, sep=' ').reshape((m, n))
        self._pixel_non_uniform_array = self._pixel_non_uniform_array.reshape((m, n))
        charge_array = charge_array * self._pixel_non_uniform_array
        charge_array = np.int16(np.rint(charge_array))

        return charge_array

    # READOUT NOISE
    def add_readout_noise(self, signal_mean_array):
        """
        Adding readout noise to signal array using normal random distribution
        Signal unit: DN
        :param signal_mean_array: signal
        :type signal_mean_array: 2d numpy array
        :return: signal with readout noise
        :rtype: 2d numpy array
        """
        m, n = signal_mean_array.shape
        sigma_readout_array = self._readout_sigma * np.ones((m, n)).reshape((m, n))

        self._readout_noise_array = np.random.normal(loc=0.0, scale=sigma_readout_array)
        signal_mean_array = signal_mean_array.astype('float64') + self._readout_noise_array
        signal_mean_array = np.int16(np.rint(signal_mean_array))

        return signal_mean_array
