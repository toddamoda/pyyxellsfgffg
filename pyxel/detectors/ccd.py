#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" CCD detector modeling class
"""
# import typing as t  # noqa: F401

import numpy as np
# from astropy import units as u
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry


def convert_to_int(value):
    """
    Convert any type of numbers to integers
    :param value:
    :type value: ndarray
    :return value:
    :rtype: int ndarray
    """
    int_value = np.rint(value)
    int_value = int_value.astype(int)
    return int_value


class CCD:
    """ The CCD detector class. """

    def __init__(self,
                 geometry: Geometry = None,
                 environment: Environment = None,
                 characteristics: CCDCharacteristics = None,
                 photons: int = None,
                 signal=None,
                 ) -> None:

        if photons is not None and signal is None:
            self._photon_mean = photons
            self._signal = None
            # self._photon_mean = photons * u.ph      # unit: photons
        elif photons is None and signal is not None:
            self._photon_mean = None
            self._signal = signal
            # self._signal = signal * u.adu       # unit: ADU
        else:
            raise ValueError("Only signal or photon number has to be provided as input")

        # self._photon_number_list = None
        self._photons = None
        self._charges = None

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics

    def generate_incident_photons(self):
        """
        Calculate incident photon number per pixel from signal or illumination
        :return:
        """
        # TODO: can both signal and photons be passed?
        photon_number_list = []
        photon_energy_list = []

        if self._signal is not None and self._photon_mean is None:
            self.row, self.col = self._signal.shape
            photon_number_list = self._signal / (self.qe * self.eta * self.sv * self.accd * self.a1 * self.a2)
            photon_number_list = np.rint(photon_number_list).astype(int).flatten()
            photon_energy_list = [0.] * self.row * self.col

        if self._photon_mean is not None and self._signal is None:
            # TODO: photon illumination generator to be implemented
            if isinstance(self._photon_mean, int):
                # uniform illumination
                photon_number_list = np.ones(self.row * self.col, dtype=int) * self._photon_mean
                photon_energy_list = [0.] * self.row * self.col

        self._create_photons_per_pixel_(photon_number_list, photon_energy_list)

    def _create_photons_per_pixel_(self, photon_number_list, photon_energy_list):
        """
        Create photons randomly distributed inside pixels with Photon class from photon_number_list
        :param photon_number_list:
        :return:
        """
        pixel_numbers = self.row * self.col

        init_ver_position = (np.arange(0.0, self.row, 1.0) + np.random.rand(self.row)) * self.pix_vert_size
        init_hor_position = (np.arange(0.0, self.col, 1.0) + np.random.rand(self.col)) * self.pix_horz_size
        init_ver_position = np.tile(init_ver_position, self.col)
        init_hor_position = np.tile(init_hor_position, self.row)
        init_z_position = [0.] * pixel_numbers

        init_ver_velocity = [0.] * pixel_numbers
        init_hor_velocity = [0.] * pixel_numbers
        init_z_velocity = [0.] * pixel_numbers

        self._photons.create_photon(photon_number_list,
                                    photon_energy_list,
                                    init_ver_position,
                                    init_hor_position,
                                    init_z_position,
                                    init_ver_velocity,
                                    init_hor_velocity,
                                    init_z_velocity)

    # def compute_charge_array(self):
    #     """
    #     Calculate charges per pixel from incident photon number and CCD parameters
    #     :return:
    #     """
    #     # self._charge = self._photons * self.qe * self.eta
    #     # self._charge = np.rint(self._charge).astype(int)
    #     pass

    def compute_k(self):
        """
        Calculate camera gain constant in units of e-/DN from CCD parameters
        :return:
        """
        self.characteristics.k = 1 / (self.sv * self.accd * self.a1 * self.a2)

    def compute_j(self):
        """
        Calculate camera gain constant in units of photons/DN from CCD parameters
        :return:
        """
        self.characteristics.j = 1 / (self.eta * self.sv * self.accd * self.a1 * self.a2)

    def compute_signal(self):   # TODO reimplement
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        # self._signal = self._charges * self.sv * self.accd     # what is self.accd exactly??
        # self.signal = np.rint(self.signal).astype(int)  # let's assume it could be real number (float)
        pass

    def compute_readout_signal(self):   # TODO reimplement
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        # self._readout_signal = self._signal * self.a1 * self.a2
        # self._readout_signal = np.rint(self._readout_signal).astype(int)   # DN
        pass

    @property
    def pix_non_uniformity(self):
        return self.characteristics.pix_non_uniformity.reshape((self.col, self.row))

    @property
    def row(self):
        return self.geometry.row

    @row.setter
    def row(self, new_row):
        self.geometry.row = new_row

    @property
    def col(self):
        return self.geometry.col

    @col.setter
    def col(self, new_col):
        self.geometry.col = new_col

    @property
    def photons(self):
        return self._photons

    @photons.setter
    def photons(self, new_photon):
        self._photons = new_photon

    @property
    def charges(self):
        return self._charges

    @charges.setter
    def charges(self, new_charge: np.ndarray):
        self._charges = new_charge

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, new_signal: np.ndarray):
        self._signal = new_signal

    # @property
    # def ccd_signal_updated(self):
    #     self.computesignal()
    #     return self.signal

    # @ccd_signal.setter
    # def ccd_signal(self, new_sig: np.ndarray):
    #     self.signal = new_sig
    #     # self.signal = convert_to_int(self.signal)

    @property
    def readout_signal(self):
        return self._readout_signal

    # @readout_signal.setter
    # def readout_signal(self, new_read_sig: np.ndarray):
    #     self._readout_signal = new_read_sig
    #     self._readout_signal = convert_to_int(self._readout_signal)

    @property
    def k(self):
        return self.characteristics.k

    # @k.setter
    # def k(self, new_k):
    #     self._k = new_k

    @property
    def j(self):
        return self.characteristics.j

    # @j.setter
    # def j(self, new_j):
    #     self._j = new_j

    @property
    def qe(self):
        return self.characteristics.qe

    # @qe.setter
    # def qe(self, newqe):
    #     self.qe = newqe

    @property
    def eta(self):
        return self.characteristics.eta

    # @eta.setter
    # def eta(self, neweta):
    #     self.eta = neweta

    @property
    def sv(self):
        return self.characteristics.sv

    # @sv.setter
    # def sv(self, newsv):
    #     self.sv = newsv

    @property
    def accd(self):
        return self.characteristics.accd

    # @accd.setter
    # def accd(self, newaccd):
    #     self.accd = newaccd

    @property
    def a1(self):
        return self.characteristics.a1

    # @a1.setter
    # def a1(self, newa1):
    #     self.a1 = newa1

    @property
    def a2(self):
        return self.characteristics.a2

    @property
    def fwc(self):
        return self.characteristics.fwc

    @property
    def temperature(self):
        return self.environment.temperature

    @property
    def depletion_zone(self):
        return self.geometry.depletion_thickness

    @property
    def field_free_zone(self):
        return self.geometry.field_free_thickness

    @property
    def pix_vert_size(self):
        return self.geometry.pixel_vert_size

    @property
    def pix_horz_size(self):
        return self.geometry.pixel_horz_size

    @property
    def total_thickness(self):
        return self.geometry.total_thickness

    @property
    def vert_dimension(self):
        return self.geometry.vert_dimension

    @property
    def horz_dimension(self):
        return self.geometry.horz_dimension

    @property
    def material_density(self):
        return self.geometry.material_density

    @property
    def material_ionization_energy(self):
        return self.geometry.material_ionization_energy
