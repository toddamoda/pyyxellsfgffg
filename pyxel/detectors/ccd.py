#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! CCD detector modelling class
"""
import numpy as np
# from os import path
# from pathlib import Path
# from astropy import units as u

import pyxel.pipelines.config
from . import Detector

# from pyxel.util import fitsfile
# from pyxel.util import get_data_dir


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


class CCDDetector(Detector):

    def __init__(self, **kwargs):
        """
        CCD parameters
        """
        self._dirty = False
        self._photons = kwargs.get('photons')                   # np int 2D array of incident photon number per pixel
        self._charge = kwargs.get('charge')                     # int number of electrons per pixel
        self._ccd_signal = kwargs.get('ccd_signal')             # np int 2D array mutable signal read out from CCD
        self._readout_signal = kwargs.get('readout_signal')     # np int 2D array mutable the image data
        # after signal (and image) processing

        ###### experimental: models will append the newly generated charges to this list
        self.charge_list = []                 # list of Charge class objects
        ###### later it should replace the self._charge 2d np array

        self._row = kwargs.get('row', 0)      # number of rows in image
        self._col = kwargs.get('col', 0)      # number of columns in image
        self._k = kwargs.get('k', 0.0)        # camera gain constant in digital number (DN)
        self._j = kwargs.get('j', 0.0)        # camera gain constant in photon number
        self._qe = kwargs.get('qe', 0.0)      # quantum efficiency
        self._eta = kwargs.get('eta', 0.0)    # quantum yield
        self._sv = kwargs.get('sv', 0.0)      # sensitivity of CCD amplifier [V/-e]
        self._accd = kwargs.get('accd', 0.0)  # output amplifier gain
        self._a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
        self._a2 = kwargs.get('a2', 0)        # gain of the ADC
        self._fwc = kwargs.get('fwc', 0)      # full well compacity
        self._temperature = kwargs.get('temperature', 0)  # temperature

        # we should put these in a GEOMETRY class
        self._depletion_zone = kwargs.get('depletion_thickness', 0.0)     # depletion zone thickness
        self._field_free_zone = kwargs.get('field_free_thickness', 0.0)   # field free zone thickness
        self._sub_thickness = kwargs.get('substrate_thickness', 0.0)      # substrate thickness
        self._pix_ver_size = kwargs.get('pixel_ver_size', 0.0)            # pixel vertical size (row)
        self._pix_hor_size = kwargs.get('pixel_hor_size', 0.0)            # pixel horizontal size (col)

        # self._total_thickness = kwargs.get('total_thickness', 0)  # total detector thickness
        self._total_thickness = self._depletion_zone + self._field_free_zone + self._sub_thickness   # total detector thickness
        self._ver_dimension = self._row * self._pix_ver_size        # detector vertical size
        self._hor_dimension = self._col * self._pix_hor_size        # detector horizontal size

        self._pix_non_uniformity = kwargs.get('pix_non_uniformity', None)

        # self._row = kwargs.get('noise_file', 0)      # number of rows in image

        self._material_density = 2.329                              # (silicon) material density [g/cm3]
        self._material_ionization_energy = 3.65                     # (silicon) ionization energy [eV]

    # check whether everything is defined necessary for computations below
    @classmethod
    def from_ccd(cls, ccd: pyxel.pipelines.config.CCD):
        # Create the CCD object
        params = {'photons': ccd.photons,
                  'signal': ccd.signal,
                  'charge': ccd.charge,
                  **vars(ccd.geometry),
                  **vars(ccd.environment),
                  **vars(ccd.characteristics)}

        ccd_obj = CCDDetector(**params)
        return ccd_obj

    def compute_photons(self):
        """
        Calculate incident photon number per pixel from signal and CCD parameters
        :return:
        """
        # TODO: can both signal and photons be passed?

        if self._ccd_signal is not None:
            self._photons = self._ccd_signal / (self._qe * self._eta * self._sv * self._accd * self._a1 * self._a2)
            self._photons = np.rint(self._photons).astype(int)
            self._row, self._col = self._photons.shape

        elif self._photons is not None:
            # TODO: photon illumination generator to be implement
            if isinstance(self._photons, int):
                # uniform illumination
                self._photons = np.ones((self._row, self._col)) * self._photons

    def compute_charge(self):
        """
        Calculate charges per pixel from incident photon number and CCD parameters
        :return:
        """
        self._charge = self._photons * self._qe * self._eta
        self._charge = np.rint(self._charge).astype(int)

    def charge_excess(self):
        """
        Limiting charges per pixel according to full well capacity
        :return:
        """
        excess_x, excess_y = np.where(self._charge > self._fwc)
        self._charge[excess_x, excess_y] = self._fwc
        self._charge = np.rint(self._charge).astype(int)

    def compute_k(self):
        """
        Calculate camera gain constant in units of e-/DN from CCD parameters
        :return:
        """
        self._k = 1 / (self._sv * self._accd * self._a1 * self._a2)

    def compute_j(self):
        """
        Calculate camera gain constant in units of photons/DN from CCD parameters
        :return:
        """
        self._j = 1 / (self._eta * self._sv * self._accd * self._a1 * self._a2)

    def compute_ccd_signal(self):
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        self._ccd_signal = self._charge * self._sv * self._accd     # what is self._accd exactly??
        # self._ccd_signal = np.rint(self._ccd_signal).astype(int)  # let's assume it could be real number (float)

    def compute_readout_signal(self):
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        self._readout_signal = self._ccd_signal * self._a1 * self._a2
        self._readout_signal = np.rint(self._readout_signal).astype(int)   # DN

    @property
    def pix_non_uniformity(self):
        return self._pix_non_uniformity.reshape((self.col, self.row))

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, new_row):
        self._row = new_row

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, new_col):
        self._col = new_col

    @property
    def photons(self):
        return self._photons

    @photons.setter
    def photons(self, new_photons):  # TODO: check that type is photons
        self._photons = convert_to_int(new_photons)

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, new_charge: np.ndarray):
        self._charge = new_charge

    @property
    def ccd_signal(self):
        return self._ccd_signal

    # @property
    # def ccd_signal_updated(self):
    #     self.compute_ccd_signal()
    #     return self._ccd_signal

    @ccd_signal.setter
    def ccd_signal(self, new_sig: np.ndarray):
        self._ccd_signal = new_sig
        # self._ccd_signal = convert_to_int(self._ccd_signal)

    @property
    def readout_signal(self):
        return self._readout_signal

    @readout_signal.setter
    def readout_signal(self, new_read_sig: np.ndarray):
        self._readout_signal = new_read_sig
        self._readout_signal = convert_to_int(self._readout_signal)

    @property
    def k(self):
        return self._k

    # @k.setter
    # def k(self, new_k):
    #     self._k = new_k

    @property
    def j(self):
        return self._j

    # @j.setter
    # def j(self, new_j):
    #     self._j = new_j

    @property
    def qe(self):
        return self._qe

    # @qe.setter
    # def qe(self, new_qe):
    #     self._qe = new_qe

    @property
    def eta(self):
        return self._eta

    # @eta.setter
    # def eta(self, new_eta):
    #     self._eta = new_eta

    @property
    def sv(self):
        return self._sv

    # @sv.setter
    # def sv(self, new_sv):
    #     self._sv = new_sv

    @property
    def accd(self):
        return self._accd

    # @accd.setter
    # def accd(self, new_accd):
    #     self._accd = new_accd

    @property
    def a1(self):
        return self._a1

    # @a1.setter
    # def a1(self, new_a1):
    #     self._a1 = new_a1

    @property
    def a2(self):
        return self._a2

    # @a2.setter
    # def a2(self, new_a2):
    #     self._a2 = new_a2

    @property
    def fwc(self):
        return self._fwc

    # @fwc.setter
    # def fwc(self, new_fwc):
    #     self._fwc = new_fwc

    @property
    def temperature(self):
        return self._temperature

    # @temperature.setter
    # def temperature(self, new_temperature):
    #     self._temperature = new_temperature

    @property
    def depletion_zone(self):
        return self._depletion_zone

    # @depletion_zone.setter
    # def depletion_zone(self, new_depletion_zone):
    #     self._depletion_zone = new_depletion_zone

    @property
    def field_free_zone(self):
        return self._field_free_zone

    # @field_free_zone.setter
    # def field_free_zone(self, new_field_free_zone):
    #     self._field_free_zone = new_field_free_zone

    @property
    def sub_thickness(self):
        return self._sub_thickness

    # @sub_thickness.setter
    # def sub_thickness(self, new_sub_thickness):
    #     self._sub_thickness = new_sub_thickness

    @property
    def pix_ver_size(self):
        return self._pix_ver_size

    # @pix_ver_size.setter
    # def pix_ver_size(self, new_pix_ver_size):
    #     self._pix_ver_size = new_pix_ver_size

    @property
    def pix_hor_size(self):
        return self._pix_hor_size

    # @pix_hor_size.setter
    # def pix_hor_size(self, new_pix_hor_size):
    #     self._pix_hor_size = new_pix_hor_size

    @property
    def total_thickness(self):
        return self._total_thickness

    # @total_thickness.setter
    # def total_thickness(self, new_total_thickness):
    #     self._total_thickness = new_total_thickness

    @property
    def ver_dimension(self):
        return self._ver_dimension

    @property
    def hor_dimension(self):
        return self._hor_dimension

    @property
    def material_density(self):
        return self._material_density

    @property
    def material_ionization_energy(self):
        return self._material_ionization_energy


# def convert_to_int(value):
#     """
#     Convert any type of numbers to integers
#     :param value:
#     :type value: ndarray
#     :return value:
#     :rtype: int ndarray
#     """
#     int_value = np.rint(value)
#     int_value = int_value.astype(int)
#     return int_value
#
#
# class CcdTransferFunction(object):
#     """
#     Class for CCD detectors, storing CCD parameters and
#     calculating number of incident photons, charges, signals per pixel
#     using CCD transfer function model
#
#     Ref.: J. Janesick - Scientific Charge-Coupled Devices, page 98.
#     """
#
#     def __init__(self, **kwargs):
#         """
#         CCD parameters
#         """
#         self._p = None    # np int 2D array of incident photon number per pixel
#         self._row = kwargs.get('row', 0)      # number of rows in image
#         self._col = kwargs.get('col', 0)      # number of columns in image
#         self._k = kwargs.get('k', 0.0)        # camera gain constant in digital number (DN)
#         self._j = kwargs.get('j', 0.0)        # camera gain constant in photon number
#         self._charge = kwargs.get('charge', 0)  # int number of electrons per pixel
#         self._qe = kwargs.get('qe', 0.0)      # quantum efficiency
#         self._eta = kwargs.get('eta', 0.0)    # quantum yield
#         self._sv = kwargs.get('sv', 0.0)      # sensitivity of CCD amplifier [V/-e]
#         self._accd = kwargs.get('accd', 0.0)  # output amplifier gain
#         self._a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
#         self._a2 = kwargs.get('a2', 0)        # gain of the ADC
#         self._fwc = kwargs.get('fwc', 0)      # full well compacity
#
#         self._signal = None  # np int 2D array mutable the image data plus the accumulated noise after processing
#         self.init_transfer_function(kwargs.get('photons', 0), kwargs.get('fits_file', ''))
#
#     def init_transfer_function(self, photons=0, fits_file=''):
#         """
#         Initialization of the transfer function: reading data from FITS
#         file or generating new data array and calculating the incident
#         photon array for each pixel.
#
#         :param ccd: CCD transfer function
#         :param photon_mean: incident photon mean
#         :type ccd: CcdTransferFunction
#         :type photon_mean: 2d numpy array
#         """
#         if fits_file:  # OPEN EXISTING FITS IMAGE
#             if not Path(fits_file).exists():
#                 fits_file = get_data_dir(fits_file)
#             if not Path(fits_file).exists():
#                 raise IOError('File not found: %s' % fits_file)
#
#             fits_obj = fitsfile.FitsFile(fits_file)
#             data = fits_obj.data
#             self._row, self._col = data.shape
#             self._signal = data  # DN
#             self.compute_photon()  # gives ccd.p in photon/pixel
#             # now we have the incident photon number per pixel (ccd.p) from the image
#         else:  # GENERATE NEW DATA with uniform illumination / gradient
#             self._row = 100
#             self._col = 100
#             # UNIFORM ILLUMINATION / DARK IMAGE:
#             print('photon mean: ', photons)
#             self._p = np.ones((self._row, self._col)) * photons  # photon average/pixel
#             # SIGNAL GRADIENT ON ONE IMAGE:
#             # ccd.p = np.arange(1, m*n+1, 1).reshape((m, n))    # photon average/pixel
#
#     @property
#     def row(self):
#         return self._row
#
#     @row.setter
#     def row(self, new_row):
#         self._row = new_row
#
#     @property
#     def col(self):
#         return self._col
#
#     @col.setter
#     def col(self, new_col):
#         self._col = new_col
#
#     @property
#     def signal(self):
#         return self._signal
#
#     @signal.setter
#     def signal(self, new_sig):
#         self._signal = new_sig
#         self._signal = convert_to_int(self._signal)
#
#     @property
#     def k(self):
#         return self._k
#
#     @k.setter
#     def k(self, new_k):
#         self._k = new_k
#
#     @property
#     def j(self):
#         return self._j
#
#     @j.setter
#     def j(self, new_j):
#         self._j = new_j
#
#     @property
#     def p(self):
#         return self._p
#
#     @p.setter
#     def p(self, new_p):
#         self._p = convert_to_int(new_p)
#
#     @property
#     def qe(self):
#         return self._qe
#
#     @qe.setter
#     def qe(self, new_qe):
#         self._qe = new_qe
#
#     @property
#     def eta(self):
#         return self._eta
#
#     @eta.setter
#     def eta(self, new_eta):
#         self._eta = new_eta
#
#     @property
#     def sv(self):
#         return self._sv
#
#     @sv.setter
#     def sv(self, new_sv):
#         self._sv = new_sv
#
#     @property
#     def accd(self):
#         return self._accd
#
#     @accd.setter
#     def accd(self, new_accd):
#         self._accd = new_accd
#
#     @property
#     def a1(self):
#         return self._a1
#
#     @a1.setter
#     def a1(self, new_a1):
#         self._a1 = new_a1
#
#     @property
#     def a2(self):
#         return self._a2
#
#     @a2.setter
#     def a2(self, new_a2):
#         self._a2 = new_a2
#
#     @property
#     def fwc(self):
#         return self._fwc
#
#     @fwc.setter
#     def fwc(self, new_fwc):
#         self._fwc = new_fwc
#
#     @property
#     def charge(self):
#         return self._charge
#
#     @charge.setter
#     def charge(self, new_charge):
#         self._charge = new_charge
#
#     # check whether everything is defined necessary for computations below
#
#     def compute_photon(self):
#         """
#         Calculate incident photon number per pixel from signal and CCD parameters
#         :return:
#         """
#         self._p = self._signal / (self._qe * self._eta * self._sv * self._accd * self._a1 * self._a2)
#         self._p = convert_to_int(self._p)
#
#     def compute_charge(self):
#         """
#         Calculate charges per pixel from incident photon number and CCD parameters
#         :return:
#         """
#         self._charge = self._p * self._qe * self._eta
#         self._charge = convert_to_int(self._charge)
#
#     def charge_excess(self):
#         """
#         Limiting charges per pixel according to full well capacity
#         :return:
#         """
#         excess_x, excess_y = np.where(self._charge > self._fwc)
#         self._charge[excess_x, excess_y] = self._fwc
#         self._charge = convert_to_int(self._charge)
#
#     def compute_k(self):
#         """
#         Calculate camera gain constant in units of e-/DN from CCD parameters
#         :return:
#         """
#         self._k = 1 / (self._sv * self._accd * self._a1 * self._a2)
#
#     def compute_j(self):
#         """
#         Calculate camera gain constant in units of photons/DN from CCD parameters
#         :return:
#         """
#         self._j = 1 / (self._eta * self._sv * self._accd * self._a1 * self._a2)
#
#     def compute_signal(self):
#         """
#         Calculate CCD signal per pixel in units of DN from charges and CCD parameters
#         :return:
#         """
#         self._signal = self._charge * self._sv * self._accd * self._a1 * self._a2
#         self._signal = convert_to_int(self._signal)
#
#
