#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! CCD detector modelling class
"""
import numpy as np
from os import path
from pathlib import Path

from pyxel.util import fitsfile
from pyxel.util import get_data_dir


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


class CcdTransferFunction(object):
    """
    Class for CCD detectors, storing CCD parameters and
    calculating number of incident photons, charges, signals per pixel
    using CCD transfer function model

    Ref.: J. Janesick - Scientific Charge-Coupled Devices, page 98.
    """

    def __init__(self, **kwargs):
        """
        CCD parameters
        """
        self._p = None    # np int 2D array of incident photon number per pixel
        self._row = kwargs.get('row', 0)      # number of rows in image
        self._col = kwargs.get('row', 0)      # number of columns in image
        self._k = kwargs.get('k', 0.0)        # camera gain constant in digital number (DN)
        self._j = kwargs.get('k', 0.0)        # camera gain constant in photon number
        self._charge = kwargs.get('charge', 0)  # int number of electrons per pixel
        self._qe = kwargs.get('qe', 0.0)      # quantum efficiency
        self._eta = kwargs.get('eta', 0.0)    # quantum yield
        self._sv = kwargs.get('sv', 0.0)      # sensitivity of CCD amplifier [V/-e]
        self._accd = kwargs.get('accd', 0.0)  # output amplifier gain
        self._a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
        self._a2 = kwargs.get('a2', 0)        # gain of the ADC
        self._fwc = kwargs.get('fwc', 0)      # full well compacity

        self._signal = None  # np int 2D array mutable the image data plus the accumulated noise after processing
        self.init_transfer_function(kwargs.get('photons', 0), kwargs.get('fits_file', ''))

    def init_transfer_function(self, photons=0, fits_file=''):
        """
        Initialization of the transfer function: reading data from FITS
        file or generating new data array and calculating the incident
        photon array for each pixel.

        :param ccd: CCD transfer function
        :param photon_mean: incident photon mean
        :type ccd: CcdTransferFunction
        :type photon_mean: 2d numpy array
        """
        if fits_file:  # OPEN EXISTING FITS IMAGE
            if not Path(fits_file).exists():
                fits_file = get_data_dir(fits_file)
            if not Path(fits_file).exists():
                raise IOError('File not found: %s' % fits_file)

            fits_obj = fitsfile.FitsFile(fits_file)
            data = fits_obj.data
            self._row, self._col = data.shape
            self._signal = data  # DN
            self.compute_photon()  # gives ccd.p in photon/pixel
            # now we have the incident photon number per pixel (ccd.p) from the image
        else:  # GENERATE NEW DATA with uniform illumination / gradient
            self._row = 100
            self._col = 100
            # UNIFORM ILLUMINATION / DARK IMAGE:
            print('photon mean: ', photons)
            self._p = np.ones((self._row, self._col)) * photons  # photon average/pixel
            # SIGNAL GRADIENT ON ONE IMAGE:
            # ccd.p = np.arange(1, m*n+1, 1).reshape((m, n))    # photon average/pixel

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
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, new_sig):
        self._signal = new_sig
        self._signal = convert_to_int(self._signal)

    @property
    def k(self):
        return self._k

    @k.setter
    def k(self, new_k):
        self._k = new_k

    @property
    def j(self):
        return self._j

    @j.setter
    def j(self, new_j):
        self._j = new_j

    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, new_p):
        self._p = convert_to_int(new_p)

    @property
    def qe(self):
        return self._qe

    @qe.setter
    def qe(self, new_qe):
        self._qe = new_qe

    @property
    def eta(self):
        return self._eta

    @eta.setter
    def eta(self, new_eta):
        self._eta = new_eta

    @property
    def sv(self):
        return self._sv

    @sv.setter
    def sv(self, new_sv):
        self._sv = new_sv

    @property
    def accd(self):
        return self._accd

    @accd.setter
    def accd(self, new_accd):
        self._accd = new_accd

    @property
    def a1(self):
        return self._a1

    @a1.setter
    def a1(self, new_a1):
        self._a1 = new_a1

    @property
    def a2(self):
        return self._a2

    @a2.setter
    def a2(self, new_a2):
        self._a2 = new_a2

    @property
    def fwc(self):
        return self._fwc

    @fwc.setter
    def fwc(self, new_fwc):
        self._fwc = new_fwc

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, new_charge):
        self._charge = new_charge

    # check whether everything is defined necessary for computations below

    def compute_photon(self):
        """
        Calculate incident photon number per pixel from signal and CCD parameters
        :return:
        """
        self._p = self._signal / (self._qe * self._eta * self._sv * self._accd * self._a1 * self._a2)
        self._p = convert_to_int(self._p)

    def compute_charge(self):
        """
        Calculate charges per pixel from incident photon number and CCD parameters
        :return:
        """
        self._charge = self._p * self._qe * self._eta
        self._charge = convert_to_int(self._charge)

    def charge_excess(self):
        """
        Limiting charges per pixel according to full well capacity
        :return:
        """
        excess_x, excess_y = np.where(self._charge > self._fwc)
        self._charge[excess_x, excess_y] = self._fwc
        self._charge = convert_to_int(self._charge)

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

    def compute_signal(self):
        """
        Calculate CCD signal per pixel in units of DN from charges and CCD parameters
        :return:
        """
        self._signal = self._charge * self._sv * self._accd * self._a1 * self._a2
        self._signal = convert_to_int(self._signal)


