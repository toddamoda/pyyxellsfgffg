"""TBW.

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
import datetime
import os

import astropy.io.fits as fits
# import numba
import numpy as np
from typing import cast

from pyxel.detectors.ccd import CCD
from pyxel.detectors.ccd_characteristics import CCDCharacteristics  # noqa: F401
from pyxel.pipelines.model_registry import registry


@registry.decorator('charge_transfer', name='cdm', detector='ccd')
def cdm(detector: CCD,
        beta_p: float = None, beta_s: float = None,
        vg: float = None, svg: float = None,
        t: float = None, st: float = None,
        parallel_trap_file: str = None,
        serial_trap_file: str = None) -> CCD:
    """
    CDM model wrapper.

    :param detector: PyXel CCD detector object
    :param beta_p: electron cloud expansion coefficient (parallel)
    :param beta_s: electron cloud expansion coefficient (serial)
    :param vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
    :param svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
    :param t: constant TDI period (parallel)
    :param st: constant TDI period (serial)
    :param parallel_trap_file: ascii file with absolute trap densities (nt),
        trap capture cross-sections (σ), trap release time constants (τr)
    :param serial_trap_file: ascii file with absolute trap densities (nt),
        trap capture cross-sections (σ), trap release time constants (τr)

    :return:

    Ne - number of electrons in a pixel
    ne - electron density in the vicinity of the trap
    Vc - volume of the charge cloud

    nt - trap density
    σ - trap capture cross-section
    τr - trap release time constant
    Pr - the probability that the trap will release the electron into the sample
    τc - capture time constant
    Pc - capture probability (per vacant trap) as a function of the number of sample electrons Ne

    NT - number of traps in the column,
        NT = 2*nt*Vg*x  where x is the number of TDI transfers or the column length in pixels.
    Nc - number of electrons captured by a given trap species during the transit of an integrating signal packet
    N0 - initial trap occupancy
    Nr - number of electrons released into the sample during a transit along the column

    fwc: Full Well Capacity in electrons (parallel)
    sfwc: Full Well Capacity in electrons (serial)
    """
    new_detector = detector  # type: CCD
    char = cast(CCDCharacteristics, new_detector.characteristics)  # type: CCDCharacteristics

    # Charge injection:     # todo make a new function from this
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

    cdm_obj = CDM03Python(
                          # rdose=1.5e3,
                          fwc=char.fwc,
                          sfwc=char.fwc_serial,
                          vth=new_detector.e_thermal_velocity,
                          beta_p=beta_p, beta_s=beta_s,
                          vg=vg, svg=svg,
                          t=t, st=st,
                          parallel_trap_file=parallel_trap_file,
                          serial_trap_file=serial_trap_file)

    new_detector.pixels.array = cdm_obj.apply_cti(new_detector.pixels.array)

    return new_detector


class CDM03Python:
    """Class to run CDM03 CTI model, class Fortran routine to perform the actual CDM03 calculations."""

    def __init__(self,
                 rdose: float = None,
                 vth: float = None,
                 beta_p: float = None, beta_s: float = None,
                 vg: float = None, svg: float = None,
                 t: float = None, st: float = None,
                 fwc: int = None, sfwc: int = None,
                 parallel_trap_file: str = None,
                 serial_trap_file: str = None) -> None:
        """Class constructor.

        :param vth:
        :param beta_p:
        :param beta_s:
        :param vg:
        :param svg:
        :param t:
        :param st:
        :param fwc:
        :param sfwc:
        :param parallel_trap_file:
        :param serial_trap_file:
        """
        # read in the absolute trap density [per cm**3]
        if parallel_trap_file is not None:
            trapdata = np.loadtxt(parallel_trap_file)
            if trapdata.ndim > 1:
                self.nt_p = trapdata[:, 0]
                self.sigma_p = trapdata[:, 1]
                self.tr_p = trapdata[:, 2]
            else:
                raise ValueError('Trap data can not be read')

        # read in the absolute trap density [per cm**3]
        if serial_trap_file is not None:
            trapdata = np.loadtxt(serial_trap_file)
            if trapdata.ndim > 1:
                self.nt_s = trapdata[:, 0]
                self.sigma_s = trapdata[:, 1]
                self.tr_s = trapdata[:, 2]
            else:
                raise ValueError('Trap data can not be read')

        if rdose:
            self.rdose = rdose
        else:
            self.rdose = 1.

        # self.dob = dob
        self.vth = vth

        self.beta_p = beta_p
        self.beta_s = beta_s

        self.vg = vg
        self.svg = svg

        self.t = t
        self.st = st

        self.fwc = fwc
        self.sfwc = sfwc

        self.parallel_cti = parallel_trap_file
        self.serial_cti = serial_trap_file

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
        """Apply radian damage based on FORTRAN CDM03 model.

        The method assumes that
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
        """
        # iflip = iquadrant % 2
        # jflip = iquadrant % 2

        image_with_cti = self._run_cdm_(image=data)

        return np.asanyarray(image_with_cti)

    # @numba.jit
    def _run_cdm_(self,
                  image=None):
        """Electron trapping in imaging mode (non-TDI).

        :param image:
        :return:
        """
        # absolute trap density which should be scaled according to radiation dose
        # (nt=1.5e10 gives approx fit to GH data for a dose of 8e9 10MeV equiv. protons)

        ####################################
        # Alex new CDM version and parameters
        ydim = 500   # jdim = 300    ## COLUMNS
        xdim = 500   # idim = 300    ## ROWS

        kdim = 3

        # I think Plato has 4510 rows right?
        x = 2000.  # 4510.
        y = 2000.
        # ydim, xdim = image.shape

        # FWC is 900k?
        self.fwc = 900000.
        self.vth = 1.2175e7
        # Below you should put (Plato CCD readout time)/4510
        self.t = 0.9828e-3
        self.vg = 1.4e-10
        # Below you should put 1/(Plato readout frequency)
        self.st = 1.e-7
        # Serial FWC?
        self.sfwc = 1800000.
        self.svg = 2.25e-10
        # dob = 0.

        # I have no idea what trapping parameters you people use these days so I just put arbitrary place-holders :-)
        self.beta_p = 0.5
        self.beta_s = 0.5

        self.sigma_p = np.array([1., 1., 1.])
        self.sigma_s = np.array([1., 1., 1.])

        self.tr_p = np.array([0.03, 0.002, 1.e-6])
        self.tr_s = np.array([0.03, 0.002, 1.e-6])

        self.nt_p = np.array([1., 1., 1.])
        self.nt_p = self.nt_p * 9.e11
        self.nt_s = self.nt_p

        # Here is a test image with 4 injection blocks (10000 electrons injected)
        s = image
        # s = np.zeros((xdim, ydim), float)
        # s[:, 50:60] = 5000.
        # s[:, 150:160] = 5000.
        # s[:, 250:260] = 5000.
        # s = s + dob
        # np.clip(s, 0., self.fwc, s)

        no = np.zeros((xdim, kdim), float)
        sno = np.zeros((ydim, kdim), float)
        ####################################

        # idim == ydim
        # jdim == xdim

        # array sizes
        #############
        # ydim, xdim = image.shape
        # s = image
        #############

        # add background electrons (diffuse optical background level)
        # s += self.dob

        # apply FWC (anti-blooming) - not needed we apply this model elsewhere
        # msk = s > self.fwc
        # s[msk] = self.fwc

        # start with parallel direction
        if self.parallel_cti:
            print('adding parallel')

            #########
            # no = np.zeros_like(image, dtype=np.float64)
            # self.nt_p *= self.rdose             # absolute trap density [per cm**3]
            # zdim_p = len(self.nt_p)
            #########

            alpha_p = self.t * self.sigma_p * self.vth * self.fwc ** self.beta_p / (2. * self.vg)
            g_p = 2. * self.nt_p * self.vg / self.fwc ** self.beta_p

            # gamma_p = g_p * (np.arange(ydim).reshape((ydim, 1)) + x)
            # gamma_p = g_p * x

            for i in range(ydim):
                print(i)
                gamma_p = g_p * (x + i)
                # gamma_p = g_p * x
                #######
                # for k in range(zdim_p):
                #######
                for k in range(kdim):
                    for j in range(xdim):
                        nc = 0.

                        # if s[j, i] > 0.:
                        if s[i, j] > 0.:
                            # nc = max((gamma_p[i, k] * s[i, j] ** self.beta_p - no[j, k]) /
                            #          (gamma_p[i, k] * s[i, j] ** (self.beta_p - 1.) + 1.) *
                            #          (1. - np.exp(-alpha_p[k] * s[i, j] ** (1. - self.beta_p))), 0.)
                            # nc = max((gamma_p[k] * s[i, j] ** self.beta_p - no[j, k]) /
                            #          (gamma_p[k] * s[i, j] ** (self.beta_p - 1.) + 1.) *
                            #          (1. - np.exp(-alpha_p[k] * s[i, j] ** (1. - self.beta_p))), 0.)
                            nc = max((gamma_p[k] * s[i, j] ** self.beta_p - no[j, k]) /
                                     (gamma_p[k] * s[i, j] ** (self.beta_p - 1.) + 1.) *
                                     (1. - np.exp(-alpha_p[k] * s[i, j] ** (1. - self.beta_p))), 0.)
                            no[j, k] += nc
                        # no[j, k] += nc
                        nr = no[j, k] * (1. - np.exp(-self.t/self.tr_p[k]))
                        s[i, j] += -1 * nc + nr
                        no[j, k] -= nr

        # now serial direction
        if self.serial_cti:
            print('adding serial')

            ##########
            #  sno = np.zeros_like(image, dtype=np.float64)
            # self.nt_s *= self.rdose             # absolute trap density [per cm**3]
            # zdim_s = len(self.nt_s)
            ##########
            alpha_s = self.st * self.sigma_s * self.vth * self.sfwc ** self.beta_s / (2. * self.svg)
            g_s = 2. * self.nt_s * self.svg / self.sfwc ** self.beta_s

            # gamma_s = g_s * (np.arange(xdim).reshape((xdim, 1)) + y)

            for j in range(xdim):
                print(j)
                gamma_s = g_s * (j + y)
                ########
                #  for k in range(zdim_s):
                ########
                for k in range(kdim):
                    # if self.tr_s[k] < self.t:
                    for i in range(ydim):
                        nc = 0.

                        # if s[j, i] > 0.:
                        if s[i, j] > 0.:
                            # nc = max((gamma_s[j, k] * s[i, j] ** self.beta_s - sno[i, k]) /
                            #          (gamma_s[j, k] * s[i, j] ** (self.beta_s - 1.) + 1.) *
                            #          (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - self.beta_s))), 0.)
                            # nc = max((gamma_s[k] * s[i, j] ** self.beta_s - sno[i, k]) /
                            #          (gamma_s[k] * s[i, j] ** (self.beta_s - 1.) + 1.) *
                            #          (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - self.beta_s))), 0.)
                            nc = max((gamma_s[k] * s[i, j] ** self.beta_s - sno[i, k]) /
                                     (gamma_s[k] * s[i, j] ** (self.beta_s - 1.) + 1.) *
                                     (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - self.beta_s))), 0.)
                            sno[i, k] += nc
                        # sno[i, k] += nc
                        nr = sno[i, k] * (1. - np.exp(-self.st/self.tr_s[k]))
                        s[i, j] += -1 * nc + nr
                        # s[j, i] += -1 * nc + nr
                        sno[i, k] -= nr

        ######################
        # make pretty picture
        # plt.subplot(2, 1, 1)
        # plt.imshow(s, cmap=plt.cm.bone, interpolation='nearest')
        # plt.xlabel('x')
        # plt.ylabel('y')
        # plt.colorbar()
        # x = np.zeros(ydim, float)
        # y = np.zeros(ydim, float)
        # for i in range(0, ydim):
        #     x[i] = i
        #     y[i] = s[100, i]
        # plt.subplot(2, 1, 2)
        # plt.plot(x, y)
        # plt.show()
        ######################
        return s


def write_fits_file(data, output, unsigned16bit=True):
    """Write out FITS files using PyFITS.

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
