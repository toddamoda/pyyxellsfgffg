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

import numpy as np
from pyxel.models.cdm.CDMtest import write_fits_file


def main():
    """ main entry point. """

    # lines = dict(
    ystart1 = 15     # 1064
    ystop1 = 16      # 1075
    xstart1 = 25
    xstop1 = 26

    # image = np.zeros((2066, 2048), dtype=np.float32)
    image = np.zeros((50, 50), dtype=np.float32)

    charge_injection = 100.

    # add horizontal charge injection lines
    image[ystart1:ystop1, :] = charge_injection
    # add vertical charge injection lines
    image[:, xstart1:xstop1] = charge_injection

    write_fits_file(image, 'before_cti.fits', unsigned16bit=False)

    cdm = CDM03Python(image)
    # image_cti = cdm.radiate_ccd()
    # image_cti = cdm.radiate_ccd_transpose()
    image_cti = cdm.apply_radiation_damage(image, iquadrant=0)
    write_fits_file(image_cti, 'after_cti.fits', unsigned16bit=False)


class CDM03Python:
    """
    Class to run CDM03 CTI model, class Fortran routine to perform the actual CDM03 calculations.
    """

    def __init__(self, data):     # settings , log=None
        """
        Class constructor.

        # :param settings: input parameters
        # :type settings: dict
        :param data: input data to be radiated
        :type data: ndarray
        # :param log: instance to Python logging
        # :type log: logging instance
        """
        self.data = data

        # self.quads = (0, 1, 2, 3)
        self.quads = 0

        self.xsize = 50     # 2048      # BUG has to be same as image shape
        self.ysize = 50     # 2066      # BUG has to be same as image shape

        # self.values = dict(quads=(0, 1, 2, 3), xsize=2048, ysize=2066, dob=0.0, rdose=8.0e9)
        # self.dob=0.0
        # self.rdose=8.0e9
        # self.values.update(settings)

        # self.log = log
        # self.logger = True
        # self._setupLogger()

        # default CDM03 settings
        # self.params = dict(beta_p=0.6, beta_s=0.6, fwc=200000., vth=1.168e7, vg=6.e-11, t=20.48e-3,
        #                    sfwc=730000., svg=1.0e-10, st=5.0e-6, parallel=1., serial=1.)
        # update with inputs
        # self.params.update(self.values)

        parallel_trap_file = 'cdm_euclid_parallel.dat'
        serial_trap_file = 'cdm_euclid_serial.dat'

        # trapdata = np.loadtxt(parallel_trap_file)
        # nt_p = trapdata[:, 0]
        # sigma_p = trapdata[:, 1]
        # tr_p = trapdata[:, 2]
        #
        # trapdata = np.loadtxt(serial_trap_file)
        # nt_s = trapdata[:, 0]
        # sigma_s = trapdata[:, 1]
        # tr_s = trapdata[:, 2]

        self.sigma_p = 0.
        self.sigma_s = 0.
        self.nt_p = 0.
        self.nt_s = 0.
        # read in trap information
        trapdata = np.loadtxt(parallel_trap_file)
        if trapdata.ndim > 1:
            self.nt_p = trapdata[:, 0]
            self.sigma_p = trapdata[:, 1]
            self.tr_p = trapdata[:, 2]
        else:
            # only one trap species
            # self.nt_p = [trapdata[0], ]
            # self.sigma_p = [trapdata[1], ]
            # self.tr_p = [trapdata[2], ]
            pass

        trapdata = np.loadtxt(serial_trap_file)
        if trapdata.ndim > 1:
            self.nt_s = trapdata[:, 0]
            self.sigma_s = trapdata[:, 1]
            self.tr_s = trapdata[:, 2]
        else:
            # only one trap species
            # self.nt_s = [trapdata[0], ]
            # self.sigma_s = [trapdata[1], ]
            # self.tr_s = [trapdata[2], ]
            pass

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

        # scale thibaut's values
        # if 'thibaut' in self.values['parallelTrapfile']:
        #     self.nt_p /= 0.576      # thibaut's values traps / pixel
        #     self.sigma_p *= 1.e4    # thibaut's values in m**2
        # if 'thibaut' in self.values['serialTrapfile']:
        #     self.nt_s *= 0.576      # thibaut's values traps / pixel  # should be division?
        #     self.sigma_s *= 1.e4    # thibaut's values in m**2

    # def _setupLogger(self):
    #     """
    #     Set up the logger.
    #     """
    #     self.logger = True
    #     if self.log is None:
    #         self.logger = False

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
    #     # data = self.data.transpose().copy()
    #     data = self.data.transpose()
    #
    #     for quad in self.quads:
    #         # if self.logger:
    #         #     self.log.info('Adding CTI to Q%i' % quad)
    #
    #         if quad == 0:
    #             d = data[0:self.xsize, 0:self.ysize]    # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[0:self.xsize, 0:self.ysize] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 1:
    #             d = data[self.xsize:, :self.ysize]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[self.xsize:, :self.ysize] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 2:
    #             d = data[:self.xsize, self.ysize:]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[:self.xsize, self.ysize:] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 3:
    #             d = data[self.xsize:, self.ysize:]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[self.xsize:, self.ysize:] = self.apply_radiation_damage(d, iquadrant=quad)
    #         else:
    #             # self.log.error('Too many quadrants! This method allows only four quadrants.')
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
    #     # data = self.data.copy()
    #     data = self.data
    #
    #     for quad in self.quads:
    #         # if self.logger:
    #             # self.log.info('Adding CTI to Q%i' % quad)
    #
    #         if quad == 0:
    #             d = data[:self.ysize, :self.xsize]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[:self.ysize, :self.xsize] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 1:
    #             d = data[:self.ysize, self.xsize:]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[:self.ysize, self.xsize:] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 2:
    #             d = data[self.ysize:, :self.xsize]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[self.ysize:, :self.xsize] = self.apply_radiation_damage(d, iquadrant=quad)
    #         elif quad == 3:
    #             d = data[self.ysize:, self.xsize:]  # .copy()
    #             # tmp = self.apply_radiation_damage(d, iquadrant=quad).copy()
    #             out[self.ysize:, self.xsize:] = self.apply_radiation_damage(d, iquadrant=quad)
    #         else:
    #             # self.log.error('Too many quadrants! This method allows only four quadrants.')
    #             raise ValueError('ERROR -- too many quadrants!!')
    #
    #     return out

    def apply_radiation_damage(self, data, iquadrant):
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
        # iflip = iquadrant / 2
        iflip = iquadrant % 2
        jflip = iquadrant % 2

        # if self.logger:
        #     self.log.info('nt_p=' + str(self.nt_p))
        #     self.log.info('nt_s=' + str(self.nt_s))
        #     self.log.info('sigma_p= ' + str(self.sigma_p))
        #     self.log.info('sigma_s= ' + str(self.sigma_s))
        #     self.log.info('taur_p= ' + str(self.taur_p))
        #     self.log.info('taur_s= ' + str(self.taur_s))
        #     self.log.info('dob=%f' % self.dob)
        #     self.log.info('rdose=%e' % self.rdose)
        #     self.log.info('xsize=%i' % data.shape[1])
        #     self.log.info('ysize=%i' % data.shape[0])
        #     self.log.info('quadrant=%i' % iquadrant)
        #     self.log.info('iflip=%i' % iflip)
        #     self.log.info('jflip=%i' % jflip)

        image_with_cti = self._run_cdm_(image=data,
                                        jflip=jflip,
                                        iflip=iflip,
                                        parallel_cti=self.parallel_cti,
                                        serial_cti=self.serial_cti)

        return np.asanyarray(image_with_cti)

    def _run_cdm_(self,
                  image=None,
                  iflip=None, jflip=None,
                  parallel_cti=None, serial_cti=None):
        """

        :param image:
        :param iflip:
        :param jflip:
        :param parallel_cti:
        :param serial_cti:
        :return:
        """

        # parallel = 'cdm_euclid_parallel.dat'
        # serial = 'cdm_euclid_serial.dat'
        # trapdata = np.loadtxt(parallel)
        # nt_p = trapdata[:, 0]
        # sigma_p = trapdata[:, 1]
        # tr_p = trapdata[:, 2]
        #
        # trapdata = np.loadtxt(serial)
        # nt_s = trapdata[:, 0]
        # sigma_s = trapdata[:, 1]
        # tr_s = trapdata[:, 2]

        # iflip = 0
        # jflip = 0
        # parallel_cti = True
        # serial_cti = True

        # rdose = 8.0e9
        # dob = 0.0
        # beta_p = 0.6
        # beta_s = 0.6
        # fwc = 200000.
        # vth = 1.168e7
        # vg = 6.e-11
        # t = 20.48e-3
        # sfwc = 730000.
        # svg = 1.0e-10
        # st = 5.0e-6

        # absolute trap density which should be scaled according to radiation dose
        # (nt=1.5e10 gives approx fit to GH data for a dose of 8e9 10MeV equiv. protons)
        self.nt_p *= self.rdose                    # absolute trap density [per cm**3]
        self.nt_s *= self.rdose                    # absolute trap density [per cm**3]

        # array sizes
        ydim, xdim = image.shape
        zdim_p = len(self.nt_p)
        zdim_s = len(self.nt_s)

        # work arrays
        # s = np.zeros_like(image)
        no = np.zeros_like(image, dtype=np.float64)
        sno = np.zeros_like(image, dtype=np.float64)
        sout = np.zeros_like(image, dtype=np.float64)

        # flip data for Euclid depending on the quadrant being processed and
        # rotate (j, i slip in s) to move from Euclid to Gaia coordinate system
        # because this is what is assumed in CDM03 (EUCLID_TN_ESA_AS_003_0-2.pdf)
        # for i in range(xdim):
        #    for j in range(ydim):
        #       s[j, i] = image[i+iflip*(xdim+1-2*i), j+jflip*(ydim+1-2*j)]
        s = image   # .copy()

        # add background electrons
        s += self.dob

        # apply FWC (anti-blooming)
        msk = s > self.fwc
        s[msk] = self.fwc

        # start with parallel direction
        if parallel_cti:
            print('adding parallel')
            alpha_p = self.t * self.sigma_p * self.vth * self.fwc ** self.beta_p / 2. / self.vg
            g_p = self.nt_p * 2.0 * self.vg / self.fwc ** self.beta_p

            for i in range(ydim):
                print(i)
                gamm_p = g_p * i
                for k in range(zdim_p):
                    for j in range(xdim):
                        nc = 0.

                        if s[i,  j] > 0.01:
                            nc = max((gamm_p[k] * s[i, j] ** self.beta_p - no[j, k]) /
                                     (gamm_p[k] * s[i, j] ** (self.beta_p - 1.) + 1.) *
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

            for j in range(xdim):
                print(j)
                gamm_s = g_s * j
                for k in range(zdim_s):
                    if self.tr_s[k] < self.t:
                        for i in range(ydim):
                            nc = 0.

                            if s[i, j] > 0.01:
                                nc = max((gamm_s[k] * s[i, j] ** self.beta_s-sno[i, k]) /
                                         (gamm_s[k] * s[i, j] ** (self.beta_s-1.)+1.) *
                                         (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - self.beta_s))), 0.)

                            sno[i, k] += nc
                            nr = sno[i, k] * (1. - np.exp(-self.st/self.tr_s[k]))
                            s[i, j] += -1 * nc + nr
                            sno[i, k] -= nr

        for i in range(ydim):
            for j in range(xdim):
                sout[i + iflip * (xdim + 1 - 2 * i), j + jflip * (ydim + 1 - 2 * j)] = s[i, j]

        return sout


if __name__ == '__main__':
    main()
