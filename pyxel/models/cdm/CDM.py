"""
Charge Transfer Inefficiency
============================

This file contains a simple class to run a CDM03 CTI model developed by Alex Short (ESA).

This now contains both the official CDM03 and a new version that allows different trap
parameters in parallel and serial direction.

:requires: NumPy

:author: Sami-Matias Niemi
:contact: s.niemi@ucl.ac.uk

:version: 0.35
"""
# import copy
from os import path
import numpy as np
import datetime
import os
import astropy.io.fits as fits
import numba    # todo: remove or add to requirements, but only if it works

from pyxel.detectors.ccd import CCD


def cdm(detector: CCD) -> CCD:
    """ CDM wrapper """

    # new_detector = copy.deepcopy(detector)
    new_detector = detector

    # Charge injection:
    # image = np.zeros((100, 100), dtype=np.float32)
    # y_start1 = 50
    # y_stop1 = 55
    # x_start1 = 50
    # x_stop1 = 55
    # charge_injection = 100.
    # # add horizontal charge injection lines
    # image[y_start1:y_stop1, :] = charge_injection
    # # add vertical charge injection lines
    # image[:, x_start1:x_stop1] = charge_injection

    cdm_obj = CDM03Python()

    charge_data = new_detector.pixels.generate_2d_charge_array()
    image_with_cti = cdm_obj.apply_cti(charge_data)
    write_fits_file(image_with_cti, 'image_with_cti.fits', unsigned16bit=False)

    # new_detector.pixels.update_charge_from_array()    # TODO TO BE IMPLEMENTED

    return new_detector


class CDM03Python:
    """
    Class to run CDM03 CTI model, class Fortran routine to perform the actual CDM03 calculations.
    """

    def __init__(self):
        """
        Class constructor.

        # :param settings: input parameters
        # :type settings: dict
        # :param data: input data to be radiated
        # :type data: ndarray
        # :param log: instance to Python logging
        # :type log: logging instance
        """

        parallel_trap_file = path.dirname(path.abspath(__file__)) + '\cdm_euclid_parallel.dat'
        serial_trap_file = path.dirname(path.abspath(__file__)) + '\cdm_euclid_serial.dat'

        # read in trap information
        trapdata = np.loadtxt(parallel_trap_file)
        if trapdata.ndim > 1:
            self.nt_p = trapdata[:, 0]
            self.sigma_p = trapdata[:, 1]
            self.tr_p = trapdata[:, 2]
        else:
            raise ValueError('Trap data can not be read')

        trapdata = np.loadtxt(serial_trap_file)
        if trapdata.ndim > 1:
            self.nt_s = trapdata[:, 0]
            self.sigma_s = trapdata[:, 1]
            self.tr_s = trapdata[:, 2]
        else:
            raise ValueError('Trap data can not be read')

        self.rdose = 8.0e11
        self.dob = 0.0
        self.beta_p = 0.6
        self.beta_s = 0.6
        self.fwc = 200000.
        self.vth = 1.168e7
        self.vg = 6.e-11
        self.t = 20.48e-3
        self.sfwc = 730000.
        self.svg = 1.0e-10
        self.st = 5.0e-6
        self.parallel_cti = True
        self.serial_cti = True

    # def radiate_ccd_transpose(self):
    #     """
    #     This routine allows the whole CCD to be run through a radiation damage mode.
    #     The routine takes into account the fact that the amplifiers are in the corners
    #     of the CCD. The routine assumes that the CCD is using four amplifiers.
    #
    #     There is an excess of .copy() calls, which should probably be cleaned up. However,
    #     given that I had problem with the Fortran code, I have kept the calls. If memory
    #     becomes an issue then this should be cleaned.
    #
    #     :return: radiation damaged image
    #     :rtype: ndarray
    #     """
    #     ydim, xdim = self.data.shape
    #     out = np.zeros((xdim, ydim))
    #
    #     # transpose the data, because Python has different convention than Fortran
    #     data = self.data.transpose()
    #
    #     for quad in self.quads:
    #         # if self.logger:
    #         #     self.log.info('Adding CTI to Q%i' % quad)
    #
    #         if quad == 0:
    #             d = data[0:self.xsize, 0:self.ysize]
    #             out[0:self.xsize, 0:self.ysize] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 1:
    #             d = data[self.xsize:, :self.ysize]
    #             out[self.xsize:, :self.ysize] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 2:
    #             d = data[:self.xsize, self.ysize:]
    #             out[:self.xsize, self.ysize:] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 3:
    #             d = data[self.xsize:, self.ysize:]
    #             out[self.xsize:, self.ysize:] = self.apply_cti(d, iquadrant=quad)
    #         else:
    #             raise ValueError('ERROR -- too many quadrants!!')
    #
    #     return out.transpose()
    #
    # def radiate_ccd(self):
    #     """
    #     This routine allows the whole CCD to be run through a radiation damage mode.
    #     The routine takes into account the fact that the amplifiers are in the corners
    #     of the CCD. The routine assumes that the CCD is using four amplifiers.
    #
    #     There is an excess of .copy() calls, which should probably be cleaned up. However,
    #     given that I had problem with the Fortran code, I have kept the calls. If memory
    #     becomes an issue then this should be cleaned.
    #
    #     :return: radiation damaged image
    #     :rtype: ndarray
    #     """
    #     ydim, xdim = self.data.shape
    #     out = np.empty((ydim, xdim))
    #
    #     # transpose the data, because Python has different convention than Fortran
    #     data = self.data
    #
    #     for quad in self.quads:
    #
    #         if quad == 0:
    #             d = data[:self.ysize, :self.xsize]
    #             out[:self.ysize, :self.xsize] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 1:
    #             d = data[:self.ysize, self.xsize:]
    #             out[:self.ysize, self.xsize:] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 2:
    #             d = data[self.ysize:, :self.xsize]
    #             out[self.ysize:, :self.xsize] = self.apply_cti(d, iquadrant=quad)
    #         elif quad == 3:
    #             d = data[self.ysize:, self.xsize:]
    #             out[self.ysize:, self.xsize:] = self.apply_cti(d, iquadrant=quad)
    #         else:
    #             raise ValueError('ERROR -- too many quadrants!!')
    #
    #     return out

    def apply_cti(self, data, iquadrant=0):
        """
        Apply radian damage based on FORTRAN CDM03 model. The method assumes that
        input data covers only a single quadrant defined by the iquadrant integer.

        :param data: imaging data to which the CDM03 model will be applied to.
        :type data: ndarray

        :param iquadrant: number of the quadrant to process
        :type iquadrant: int

        cdm03 - Function signature::

              sout = cdm03(sinp,iflip,jflip,dob,rdose,in_nt,in_sigma,in_tr,[xdim,ydim,zdim])
            Required arguments:
              sinp : input rank-2 array('d') with bounds (xdim,ydim)
              iflip : input int
              jflip : input int
              dob : input float
              rdose : input float
              in_nt : input rank-1 array('d') with bounds (zdim)
              in_sigma : input rank-1 array('d') with bounds (zdim)
              in_tr : input rank-1 array('d') with bounds (zdim)
            Optional arguments:
              xdim := shape(sinp,0) input int
              ydim := shape(sinp,1) input int
              zdim := len(in_nt) input int
            Return objects:
              sout : rank-2 array('d') with bounds (xdim,ydim)

        .. Note:: Because Python/NumPy arrays are different row/column based, one needs
                  to be extra careful here. NumPy.asfortranarray will be called to get
                  an array laid out in Fortran order in memory. Before returning the
                  array will be laid out in memory in C-style (row-major order).

        :return: image that has been run through the CDM03 model
        :rtype: ndarray
        """""

        # iflip = iquadrant % 2
        # jflip = iquadrant % 2

        image_with_cti = self._run_cdm_(image=data,
                                        parallel_cti=self.parallel_cti,
                                        serial_cti=self.serial_cti)

        return np.asanyarray(image_with_cti)

    @numba.jit
    def _run_cdm_(self,
                  image=None,
                  parallel_cti=None,
                  serial_cti=None):
        """

        :param image:
        :param parallel_cti:
        :param serial_cti:
        :return:
        """

        # absolute trap density which should be scaled according to radiation dose
        # (nt=1.5e10 gives approx fit to GH data for a dose of 8e9 10MeV equiv. protons)
        self.nt_p *= self.rdose                    # absolute trap density [per cm**3]
        self.nt_s *= self.rdose                    # absolute trap density [per cm**3]

        # array sizes
        ydim, xdim = image.shape
        zdim_p = len(self.nt_p)
        zdim_s = len(self.nt_s)

        # work arrays
        no = np.zeros_like(image, dtype=np.float64)
        sno = np.zeros_like(image, dtype=np.float64)

        s = image

        # add background electrons
        s += self.dob

        # apply FWC (anti-blooming)
        msk = s > self.fwc
        s[msk] = self.fwc

        # start with parallel direction
        if parallel_cti:
            print('adding parallel')
            alpha_p = self.t * self.sigma_p * self.vth * self.fwc ** self.beta_p / 2. / self.vg
            g_p = self.nt_p * 2. * self.vg / self.fwc ** self.beta_p

            gamm_p = g_p * np.arange(ydim).reshape((ydim, 1))

            for i in range(ydim):
                print(i)
                for k in range(zdim_p):
                    for j in range(xdim):
                        nc = 0.

                        if s[i, j] > 0.01:
                            nc = max((gamm_p[i, k] * s[i, j] ** self.beta_p - no[j, k]) /
                                     (gamm_p[i, k] * s[i, j] ** (self.beta_p - 1.) + 1.) *
                                     (1. - np.exp(-alpha_p[k] * s[i, j] ** (1. - self.beta_p))), 0.)

                        no[j, k] += nc
                        nr = no[j, k] * (1. - np.exp(-self.t/self.tr_p[k]))
                        s[i, j] += -1 * nc + nr
                        no[j, k] -= nr

        # now serial direction
        if serial_cti:
            print('adding serial')
            alpha_s = self.st * self.sigma_s * self.vth * self.sfwc ** self.beta_s / 2. / self.svg
            g_s = self.nt_s * 2. * self.svg / self.sfwc ** self.beta_s

            gamm_s = g_s * np.arange(xdim).reshape((xdim, 1))

            for j in range(xdim):
                print(j)
                for k in range(zdim_s):
                    if self.tr_s[k] < self.t:
                        for i in range(ydim):
                            nc = 0.

                            if s[i, j] > 0.01:
                                nc = max((gamm_s[j, k] * s[i, j] ** self.beta_s - sno[i, k]) /
                                         (gamm_s[j, k] * s[i, j] ** (self.beta_s - 1.) + 1.) *
                                         (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - self.beta_s))), 0.)

                            sno[i, k] += nc
                            nr = sno[i, k] * (1. - np.exp(-self.st/self.tr_s[k]))
                            s[i, j] += -1 * nc + nr
                            sno[i, k] -= nr

        return s


def write_fits_file(data, output, unsigned16bit=True):
    """
    Write out FITS files using PyFITS.

    :param data: data to write to a FITS file
    :type data: ndarray
    :param output: name of the output file
    :type output: string
    :param unsigned16bit: whether to scale the data using bzero=32768
    :type unsigned16bit: bool

    :return: None
    """
    if os.path.isfile(output):
        os.remove(output)

    # create a new FITS file, using HDUList instance
    ofd = fits.HDUList(fits.PrimaryHDU())

    # new image HDU
    hdu = fits.ImageHDU(data=data)

    # convert to unsigned 16bit int if requested
    if unsigned16bit:
        hdu.scale('int16', '', bzero=32768)
        hdu.header.add_history('Scaled to unsigned 16bit integer!')

    # update and verify the header
    hdu.header.add_history('If questions, please contact Sami-Matias Niemi (s.niemi at ucl.ac.uk).')
    hdu.header.add_history('This file has been created with the VISsim Python Package at %s'
                           % datetime.datetime.isoformat(datetime.datetime.now()))
    hdu.verify('fix')

    ofd.append(hdu)

    # write the actual file
    ofd.writeto(output)


def mssl_cdm03_params():
    return dict(beta_p=0.29, beta_s=0.29,
                fwc=200000.,
                vth=1.168e7,
                t=20.48e-3,
                vg=6.e-11,
                st=5.e-6,
                sfwc=730000.,
                svg=1.2e-10)
