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
                 image=None,
                 ) -> None:

        if photons is not None and image is None:
            self._photon_mean = photons
            self._image = None
            # self._photon_mean = photons * u.ph      # unit: photons
        elif photons is None and image is not None:
            self._photon_mean = None
            self._image = image                    # final signal after processing , unit: ADU
        else:
            raise ValueError("Only signal or photon number has to be provided as input")

        # self._photon_number_list = None
        self._photons = None
        self._charges = None
        self._pixels = None
        self._signal = None     # signal read out directly from CCD

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics

    def generate_incident_photons(self):
        """
        Calculate incident photon number per pixel from image or illumination
        :return:
        """
        # TODO: can both image and photons be passed?
        photon_number_list = []
        photon_energy_list = []

        if self._image is not None and self._photon_mean is None:
            self.row, self.col = self._image.shape
            photon_number_list = self._image / (self.qe * self.eta * self.sv * self.accd * self.a1 * self.a2)
            photon_number_list = np.rint(photon_number_list).astype(int).flatten()
            photon_energy_list = [0.] * self.row * self.col

        if self._photon_mean is not None and self._image is None:
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

    def compute_image(self):   # TODO reimplement
        """
        Calculate CCD image in units of DN from charges and CCD parameters
        :return:
        """
        # self._image = self._signal * self.a1 * self.a2
        # self._image = np.rint(self._image).astype(int)   # DN
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
    def charges(self, new_charge):
        self._charges = new_charge

    @property
    def pixels(self):
        return self._pixels

    @pixels.setter
    def pixels(self, new_pixel):
        self._pixels = new_pixel

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, new_signal: np.ndarray):
        self._signal = new_signal

    @property
    def image(self):
        return self._image

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
