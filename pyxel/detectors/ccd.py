#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! CCD detector modelling class
"""
import numpy as np
from astropy import units as u

from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry
# from pyxel.detectors.optics import Optics



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

    def __init__(self,
                 geometry: Geometry = None,
                 environment: Environment = None,
                 characteristics: CCDCharacteristics = None,
                 photons=None, signal=None, charge=None):

        if photons is not None:
            photons = photons * u.ph   # unit: photons

        if signal is not None:
            signal = signal * u.adu  # unit: ADU

        if charge is not None:
            charge = charge * u.electron  # unit: electrons

        self._photons = photons
        self._signal = signal
        self._charge = charge

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics

    #
    # def __init__(self, **kwargs):
    #     """
    #     CCD parameters
    #     """
    #
    #     self._dirty = False
    #     self.photons = kwargs.get('photons')                   # np int 2D array of incident photon number per pixel
    #     self.charge = kwargs.get('charge')                     # int number of electrons per pixel
    #     self.signal = kwargs.get('signal')             # np int 2D array mutable signal read out from CCD
    #     self._readout_signal = kwargs.get('readout_signal')     # np int 2D array mutable the image data
    #     # after signal (and image) processing
    #
    #     ###### experimental: models will append the newly generated charges to this list
    #     self.charge_list = []                 # list of Charge class objects
    #     ###### later it should replace the self.charge 2d np array
    #
    #     self._row = kwargs.get('row', 0)      # number of rows in image
    #     self._col = kwargs.get('col', 0)      # number of columns in image
    #     self._k = kwargs.get('k', 0.0)        # camera gain constant in digital number (DN)
    #     self._j = kwargs.get('j', 0.0)        # camera gain constant in photon number
    #     self.qe = kwargs.get('qe', 0.0)      # quantum efficiency
    #     self.eta = kwargs.get('eta', 0.0)    # quantum yield
    #     self.sv = kwargs.get('sv', 0.0)      # sensitivity of CCD amplifier [V/-e]
    #     self.accd = kwargs.get('accd', 0.0)  # output amplifier gain
    #     self.a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
    #     self.a2 = kwargs.get('a2', 0)        # gain of the ADC
    #     self.fwc = kwargs.get('fwc', 0)      # full well compacity
    #     self._temperature = kwargs.get('temperature', 0)  # temperature
    #
    #     # we should put these in a GEOMETRY class
    #     self._depletion_zone = kwargs.get('depletion_thickness', 0.0)     # depletion zone thickness
    #     self._field_free_zone = kwargs.get('field_free_thickness', 0.0)   # field free zone thickness
    #     self._sub_thickness = kwargs.get('substrate_thickness', 0.0)      # substrate thickness
    #     self._pix_ver_size = kwargs.get('pixel_ver_size', 0.0)            # pixel vertical size (row)
    #     self._pix_hor_size = kwargs.get('pixel_hor_size', 0.0)            # pixel horizontal size (col)
    #
    #     # self._total_thickness = kwargs.get('total_thickness', 0)  # total detector thickness
    #     self._total_thickness = self._depletion_zone + self._field_free_zone + self._sub_thickness   # total detector thickness
    #     self._ver_dimension = self._row * self._pix_ver_size        # detector vertical size
    #     self._hor_dimension = self._col * self._pix_hor_size        # detector horizontal size
    #
    #     self._pix_non_uniformity = kwargs.get('pix_non_uniformity', None)
    #
    #     # self._row = kwargs.get('noise_file', 0)      # number of rows in image
    #
    #     self._material_density = 2.329                              # (silicon) material density [g/cm3]
    #     self._material_ionization_energy = 3.65                     # (silicon) ionization energy [eV]

    # # check whether everything is defined necessary for computations below
    # @classmethod
    # def from_ccd(cls, ccd: pyxel.pipelines.config.CCD):
    #     # Create the CCD object
    #     params = {'photons': ccd.photons,
    #               'signal': ccd.signal,
    #               'charge': ccd.charge,
    #               **vars(ccd.geometry),
    #               **vars(ccd.environment),
    #               **vars(ccd.characteristics)}
    #
    #     ccd_obj = CCDDetector(**params)
    #     return ccd_obj

    def compute_photons(self):
        """
        Calculate incident photon number per pixel from signal and CCD parameters
        :return:
        """
        # TODO: can both signal and photons be passed?

        if self._signal is not None:
            self._photons = self._signal / (self.qe * self.eta * self.sv * self.accd * self.a1 * self.a2)
            self._photons = np.rint(self._photons).astype(int)
            self.row, self.col = self._photons.shape

        elif self._photons is not None:
            # TODO: photon illumination generator to be implement
            if isinstance(self._photons, int):
                # uniform illumination
                self._photons = np.ones((self.row, self.col)) * self._photons

    def compute_charge(self):
        """
        Calculate charges per pixel from incident photon number and CCD parameters
        :return:
        """
        self._charge = self._photons * self.qe * self.eta
        self._charge = np.rint(self._charge).astype(int)

    def charge_excess(self):
        """
        Limiting charges per pixel according to full well capacity
        :return:
        """
        excess_x, excess_y = np.where(self._charge > self.fwc)
        self._charge[excess_x, excess_y] = self.fwc
        self._charge = np.rint(self._charge).astype(int)

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

    def compute_signal(self):
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        self._signal = self._charge * self.sv * self.accd     # what is self.accd exactly??
        # self.signal = np.rint(self.signal).astype(int)  # let's assume it could be real number (float)

    def compute_readout_signal(self):
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        self.readout_signal = self._signal * self.a1 * self.a2
        self.readout_signal = np.rint(self.readout_signal).astype(int)   # DN

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

    # @photons.setter
    # def photons(self, newphotons):  # TODO: check that type is photons
    #     self.photons = convert_to_int(newphotons)

    @property
    def charge(self):
        return self._charge

    # @charge.setter
    # def charge(self, newcharge: np.ndarray):
    #     self.charge = newcharge

    @property
    def signal(self):
        return self._signal

    # @property
    # def ccd_signal_updated(self):
    #     self.computesignal()
    #     return self.signal

    # @ccd_signal.setter
    # def ccd_signal(self, new_sig: np.ndarray):
    #     self.signal = new_sig
    #     # self.signal = convert_to_int(self.signal)

    # @property
    # def readout_signal(self):
    #     return self._readout_signal
    #
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

    # @a2.setter
    # def a2(self, newa2):
    #     self.a2 = newa2

    @property
    def fwc(self):
        return self.characteristics.fwc

    # @fwc.setter
    # def fwc(self, newfwc):
    #     self.fwc = newfwc

    @property
    def temperature(self):
        return self.environment.temperature

    # @temperature.setter
    # def temperature(self, new_temperature):
    #     self._temperature = new_temperature

    @property
    def depletion_zone(self):
        return self.geometry.depletion_zone

    # @depletion_zone.setter
    # def depletion_zone(self, new_depletion_zone):
    #     self._depletion_zone = new_depletion_zone

    @property
    def field_free_zone(self):
        return self.geometry.field_free_zone

    # @field_free_zone.setter
    # def field_free_zone(self, new_field_free_zone):
    #     self._field_free_zone = new_field_free_zone

    @property
    def sub_thickness(self):
        return self.geometry.sub_thickness

    # @sub_thickness.setter
    # def sub_thickness(self, new_sub_thickness):
    #     self._sub_thickness = new_sub_thickness

    @property
    def pix_ver_size(self):
        return self.geometry.pix_ver_size

    # @pix_ver_size.setter
    # def pix_ver_size(self, new_pix_ver_size):
    #     self._pix_ver_size = new_pix_ver_size

    @property
    def pix_hor_size(self):
        return self.geometry.pix_hor_size

    # @pix_hor_size.setter
    # def pix_hor_size(self, new_pix_hor_size):
    #     self._pix_hor_size = new_pix_hor_size

    @property
    def total_thickness(self):
        return self.geometry.total_thickness

    # @total_thickness.setter
    # def total_thickness(self, new_total_thickness):
    #     self._total_thickness = new_total_thickness

    @property
    def ver_dimension(self):
        return self.geometry.ver_dimension

    @property
    def hor_dimension(self):
        return self.geometry.hor_dimension

    @property
    def material_density(self):
        return self.geometry.material_density

    @property
    def material_ionization_energy(self):
        return self.geometry.material_ionization_energy
