"""
Charge Distortion Model for CCDs
============================

This is a function to run the upgraded CDM CTI model developed by Alex Short (ESA).

:requires: NumPy

:author: Alex Short
:author: Sami-Matias Niemi
:author: David Lucsanyi
"""

# import os
# import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt
import numba

#
# def main():
#     """
#     Main function to run CDM with defined arguments.
#
#     The readout node is always next to the (0, 0) index element of the 2d array!
#     When you load in the image you should rotate it relatively to the (0, 0) element with n parameter
#
#     """
#     print('CDM')
#
#     # absolute trap density which should be scaled according to radiation dose
#     # (nt=1.5e10 gives approx fit to GH data for a dose of 8e9 10MeV equiv. protons)
#
#     # # ###########
#     # y = 1500
#     # x = 1500
#     # fullframe = np.zeros((y, x), dtype=float)
#     #
#     # # image
#     # # yimgpos = 100   # image position relative to readout node (0, 0)
#     # # ximgpos = 150
#     # # image_file = 'data/01.fits'
#     # # image = fits.getdata(image_file)
#     # # n = 0
#     # # image = np.rot90(image, n)
#     # # yimage, ximage = image.shape
#     # # fullframe[yimgpos:yimgpos+yimage, ximgpos:ximgpos+ximage] += image
#     #
#     # fullframe = injection(fullframe)
#     #
#     # # CTI window
#     # para_transfers = 0   # CTI window position relative to readout node (0, 0)
#     # seri_transfers = 0
#     # ydim = 700              # CTI window dimensions
#     # xdim = 500
#     ###################
#
#     ####################
#     # # CTI window
#     para_transfers = 1553  # 1552    # full dimensions of camera
#     seri_transfers = 0
#     # ydim = 2052   # CTI window dimensions (either time in case of charge inj. or pixel dim. in case of image)
#     xdim = 1
#     #### TODO
#
#     charge_inj_flag = True
#     injection_profile = np.loadtxt('data/cdm-input.txt')
#     ydim = len(injection_profile)
#     injection_profile = injection_profile.reshape((ydim, 1))
#     fullframe = injection_profile
#
#     # ylength = len(injection_profile)
#     # injection_profile = injection_profile.reshape((ylength, 1))
#     # fullframe = np.zeros((ylength + para_transfers, 1), dtype=float)
#     # fullframe[para_transfers: para_transfers + ylength, 0] += injection_profile[:, 0]
#
#
#
#     # original_cti_profile = np.loadtxt('data/cdm-output-pCTI-1trapspecies.txt')
#     # ylength2 = len(original_cti_profile)
#     # original_cti_profile = original_cti_profile.reshape((ylength2, 1))
#     # original_output = np.zeros((ylength2 + para_transfers, 1), dtype=float)
#     # original_output[para_transfers: para_transfers + ylength2, 0] += original_cti_profile[:, 0]
#     #
#     # original_cti_profile = np.loadtxt('data/cdm-output-pCTI-2trapspecies_David.txt')
#     original_cti_profile = np.loadtxt('data/cdm-output-pCTI-3trapspecies_David.txt')
#     original_output = original_cti_profile.reshape((len(original_cti_profile), 1))
#     #####################
#
#     # ptp = 947.22e-6 #sec (parallel transfer period)
#     # CCD temperature = 203 K
#     # iLevel = 0
#     # iDur = 0
#     # iPer = 1000000
#     # tCi = 0
#     # Beta = 0.3
#     # Dob = 0
#     # TDI mode = false(imaging)
#     # Fwc = 1e6
#     # Volume definition: 18e-6 * 18e-6 / 2 * 1e-6;
#
#     # Trap species # 0:
#     # volume = 1.62E-16 m^-3
#     # temperature = 203.0 K
#     # energy(eV) = 0.40852255
#     # release time constant(s) = 0.09472207122546614
#     # density(traps / pixel) = 10.0
#     # capture cross section(m2) = 5.0E-20
#     # i.e.tau = 10 * ptp
#
#     # Parallel CTI only
#     # ###################
#
#     t = 947.22e-6       # 0.9828e-3
#     fwc = 1.e6          # 900000.
#     vg = 1.62e-10       # 1.4e-10   # cm-3
#
#     beta_p = 0.3        # 0.5        ### ????????????
#     # beta_p = 0.5
#
#     # sigma_p = np.array([5.0e-16])                         # cm**2
#     sigma_p = np.array([5.0e-16, 5.0e-16, 8.0e-16])                  # cm**2
#     # tr_p = np.array([0.09472207122546614])                # sec
#     tr_p = np.array([0.09472207122546614, 0.0112425, 0.22342])       # sec
#     # nt_p = np.array([10.])                                # traps / pixel
#     nt_p = np.array([10., 20., 30.])                             # traps / pixel
#
#     dob = 0.
#     # rdose = 1.
#     vth = 1.2175e7       # # ??????????
#
#     st = 0.9828e-3  # 1.e-7
#     sfwc = 900000.  # 1800000.
#     svg = 1.4e-10   # 2.25e-10
#
#     beta_s = 0.3
#     # sigma_s = np.array([1., 1., 1.])
#     # tr_s = np.array([0.03, 0.002, 1.e-6])
#     sigma_s = np.array([1.])
#     tr_s = np.array([0.03])
#     nt_s = nt_p
#
#     result = cdm(s=fullframe,
#                  y_start=None,
#                  x_start=None,
#                  ydim=None,
#                  xdim=None,
#                  # rdose=rdose,
#                  dob=dob,
#                  beta_p=beta_p,
#                  beta_s=beta_s,
#                  vg=vg,
#                  svg=svg,
#                  t=t,
#                  st=st,
#                  fwc=fwc,
#                  sfwc=sfwc,
#                  vth=vth,
#                  charge_injection=charge_inj_flag,
#                  all_parallel_trans=para_transfers,
#                  all_serial_trans=None,
#                  # parallel_trap_file= ,
#                  # serial_trap_file= ,
#                  sigma_p=sigma_p, sigma_s=sigma_s,
#                  tr_p=tr_p, tr_s=tr_s,
#                  nt_p=nt_p, nt_s=nt_s)
#
#     # Add noise:
#     np.random.seed(12421351)
#     sigma = 30
#     sigma_array = sigma * np.ones((len(result), 1))
#     result = np.random.normal(loc=result, scale=sigma_array)
#     np.clip(result, 0., None, result)  # full well capacity
#
#     # np.savetxt('data/cdm-output-pCTI-2trapspecies_David.txt', result)
#     np.savetxt('data/cdm-output-pCTI-3trapspecies_NOISE_sigma'+str(sigma)+'_David.txt', result)
#
#     # plt.figure()    # SERIAL PROFILE
#     # plot_serial_profile(data=fullframe, data2=result, row=250)
#     # plt.ylim(0, 25e3)
#     #
#     # plt.figure()    # PARALLEL PROFILE
#     # plot_parallel_profile(data=fullframe, data2=result, col=250)
#     # plt.ylim(0, 25e3)
#     #
#     # plt.figure()
#     # plot_image(result)
#     #
#     plt.figure()
#     plot_1d_profile(fullframe)
#     plot_1d_profile(original_output)
#     plot_1d_profile(result)
#
#     plt.figure()
#     plot_residuals(data=result, data2=original_output)
#
#     plt.show()
#
#
# def injection(image):  # TODO finish
#     """Inject charge
#
#     :return:
#     """
#     image[:, 50:60] = 10000.
#     image[:, 150:160] = 10000.
#     image[:, 300:310] = 10000.
#
#     image[50:60, :] = 10000.
#     image[150:160, :] = 10000.
#     image[300:310, :] = 10000.
#     # y_start1 = 50
#     # y_stop1 = 55
#     # x_start1 = 50
#     # x_stop1 = 55
#     # charge_injected = 100.
#     # # add horizontal charge injection lines
#     # image[y_start1:y_stop1, :] = charge_injected
#     # # add vertical charge injection lines
#     # image[:, x_start1:x_stop1] = charge_injected
#     return image


@numba.jit
def cdm(s: np.ndarray = None,
        # y_start: int = None,
        # x_start: int = None,
        # ydim: int = None,
        # xdim: int = None,
        # rdose: float = None,
        dob: float = None,
        beta_p: float = None,
        beta_s: float = None,
        vg: float = None,
        svg: float = None,
        t: float = None,
        st: float = None,
        fwc: float = None,
        sfwc: float = None,
        vth: float = None,
        charge_injection: bool = False,
        all_parallel_trans: int = None,
        all_serial_trans: int = None,
        # parallel_trap_file: str = None,
        # serial_trap_file: str = None,
        sigma_p: np.ndarray = None, sigma_s: np.ndarray = None,
        tr_p: np.ndarray = None, tr_s: np.ndarray = None,
        nt_p: np.ndarray = None, nt_s: np.ndarray = None
        ):
    """ CDM model.

    :param s:
    # :param y_start:
    # :param x_start:
    # :param ydim:
    # :param xdim:
    # :param rdose:
    :param dob:
    :param beta_p: electron cloud expansion coefficient (parallel)
    :param beta_s: electron cloud expansion coefficient (serial)
    :param vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
    :param svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
    :param t: constant TDI period (parallel)
    :param st: constant TDI period (serial)
    :param fwc:
    :param sfwc:
    :param vth:
    # :param parallel_trap_file: ascii file with absolute trap densities (nt),
    #     trap capture cross-sections (σ), trap release time constants (τr)
    # :param serial_trap_file: ascii file with absolute trap densities (nt),
    #     trap capture cross-sections (σ), trap release time constants (τr)
    :param charge_injection:
    :param all_parallel_trans:
    :param all_serial_trans:
    :param sigma_p:
    :param sigma_s:
    :param tr_p:
    :param tr_s:
    :param nt_p: number of traps per electron cloud (and not pixel!) in parallel direction
    :param nt_s: number of traps per electron cloud (and not pixel!) in serial direction
    :return:

    Ne - number of electrons in a pixel
    ne - electron density in the vicinity of the trap
    Vc - volume of the charge cloud

    nt - number of traps per pixel (and not vol density anymore)
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

    parallel_cti = True
    serial_cti = False

    # read in the absolute trap density [per cm**3]     # todo: fix this
    # if parallel_trap_file is not None:
    #     trapdata = np.loadtxt(parallel_trap_file)
    #     if trapdata.ndim > 1:
    #         nt_p = trapdata[:, 0]
    #         sigma_p = trapdata[:, 1]
    #         tr_p = trapdata[:, 2]
    #     else:
    #         raise ValueError('Trap data can not be read')

    # read in the absolute trap density [per cm**3]     # todo: fix this
    # if serial_trap_file is not None:
    #     trapdata = np.loadtxt(serial_trap_file)
    #     if trapdata.ndim > 1:
    #         nt_s = trapdata[:, 0]
    #         sigma_s = trapdata[:, 1]
    #         tr_s = trapdata[:, 2]
    #     else:
    #         raise ValueError('Trap data can not be read')

    ydim, xdim = s.shape        # full signal array we want to apply cdm for

    kdim_p = len(nt_p)
    kdim_s = len(nt_s)

    # if y_start is None:
    #     y_start = 0
    # if x_start is None:
    #     x_start = 0
    # if ydim is None:
    #     ydim = y_total_dim
    # if xdim is None:
    #     xdim = x_total_dim

    s = s + dob                 # diffuse optical background
    np.clip(s, 0., fwc, s)      # full well capacity

    nt_p = nt_p / vg            # parallel trap density (traps / cm**3)
    nt_s = nt_s / svg           # serial trap density (traps / cm**3)

    # no = np.zeros((x_total_dim, kdim_p), float)
    # sno = np.zeros((y_total_dim, kdim_s), float)
    no = np.zeros((xdim, kdim_p), float)
    sno = np.zeros((ydim, kdim_s), float)

    # nt_p *= rdose             # absolute trap density [per cm**3]
    # nt_s *= rdose             # absolute trap density [per cm**3]

    # if charge_injection:
    #     y_start = 0
    #     # in this case ydim is the charge injection profile in function of time (and not in func of pixel pos)

    # IMAGING (non-TDI) MODE
    # Parallel direction
    if parallel_cti:
        # print('adding parallel CTI')
        alpha_p = t * sigma_p * vth * fwc ** beta_p / (2. * vg)
        g_p = 2. * nt_p * vg / fwc ** beta_p
        # for i in range(y_start, y_start+ydim):
        for i in range(0, ydim):
            # print('i=', i)
            if charge_injection:
                gamma_p = g_p * all_parallel_trans            # number of all transfers in parallel dir.
            else:
                gamma_p = g_p * i
                # i -= y_start
            for k in range(kdim_p):
                # for j in range(x_start, x_start+xdim):
                for j in range(0, xdim):
                    nc = 0.
                    if s[i, j] > 0.01:
                        nc = max((gamma_p[k] * s[i, j] ** beta_p - no[j, k]) /
                                 (gamma_p[k] * s[i, j] ** (beta_p - 1.) + 1.) *
                                 (1. - np.exp(-alpha_p[k] * s[i, j] ** (1. - beta_p))), 0.)
                        no[j, k] += nc

                    nr = no[j, k] * (1. - np.exp(-t/tr_p[k]))
                    s[i, j] += -1 * nc + nr
                    no[j, k] -= nr
                    if s[i, j] < 0.01:
                        s[i, j] = 0.

    # IMAGING (non-TDI) MODE
    # Serial direction
    if serial_cti:
        # print('adding serial CTI')
        alpha_s = st * sigma_s * vth * sfwc ** beta_s / (2. * svg)
        g_s = 2. * nt_s * svg / sfwc ** beta_s
        # for j in range(x_start, x_start+xdim):
        for j in range(0, xdim):
            # print('j=', j)
            gamma_s = g_s * j
            for k in range(kdim_s):
                # if tr_s[k] < t:
                # for i in range(y_start, y_start+ydim):
                for i in range(0, ydim):
                    nc = 0.
                    if s[i, j] > 0.01:
                        nc = max((gamma_s[k] * s[i, j] ** beta_s - sno[i, k]) /
                                 (gamma_s[k] * s[i, j] ** (beta_s - 1.) + 1.) *
                                 (1. - np.exp(-alpha_s[k] * s[i, j] ** (1. - beta_s))), 0.)
                        sno[i, k] += nc

                    nr = sno[i, k] * (1. - np.exp(-st/tr_s[k]))
                    s[i, j] += -1 * nc + nr
                    sno[i, k] -= nr
                    if s[i, j] < 0.01:
                        s[i, j] = 0.

    return s


def plot_serial_profile(data, row, data2=None):
    """TBW.

    :param data:
    :param row:
    :param data2:
    :return:
    """
    ydim, xdim = data.shape
    profile_x = list(range(ydim))
    profile_y = data[row, :]
    plt.title('Serial profile')
    plt.plot(profile_x, profile_y, color='blue')
    if data2 is not None:
        profile_y_2 = data2[row, :]
        plt.plot(profile_x, profile_y_2, color='red')


def plot_parallel_profile(data, col, data2=None):
    """TBW.

    :param data:
    :param col:
    :param data2:
    :return:
    """
    ydim, xdim = data.shape
    profile_x = list(range(xdim))
    profile_y = data[:, col]
    plt.title('Parallel profile')
    plt.plot(profile_x, profile_y, color='blue')
    if data2 is not None:
        profile_y_2 = data2[:, col]
        plt.plot(profile_x, profile_y_2, color='red')


def plot_1d_profile(array, offset=0, label='', m='-'):
    """plot profile on log scale

    :param array:
    :param offset:
    :param label:
    :param m:
    :return:
    """
    x = list(range(offset, offset + len(array)))
    # plt.title('Parallel profile, charge injection')
    plt.semilogy(x, array, m, label=label)
    if label:
        plt.legend()


def plot_1d_profile_lin(array, offset=0, label='', m='-', col=None):
    """TBW.

    :param array:
    :param offset:
    :param label:
    :param m:
    :param col:
    :return:
    """
    x = list(range(offset, offset + len(array)))
    # plt.title('Parallel profile, charge injection')
    plt.plot(x, array, m, label=label, color=col)
    if label:
        plt.legend()


def plot_1d_profile_with_err(array, error, offset=0, label=''):
    """TBW.

    :param array:
    :param error:
    :param offset:
    :param label:
    :return:
    """
    x = list(range(offset, offset + len(array)))
    plt.title('Parallel profile with error, charge injection')
    plt.errorbar(x, array, error, label=label, linestyle='None', marker='.')
    if label:
        plt.legend()


def plot_residuals(data, data2, label=''):  # col='magenta',
    """TBW.

    :param data:
    :param data2:
    # :param col:
    :param label:
    :return:
    """
    x = list(range(len(data)))
    # plt.title('Residuals of fitted and target parallel CTI profiles')
    residuals = np.around(data-data2, decimals=5)
    # residuals = data-data2
    # plt.plot(x, residuals, '.', color=col, label=label)
    plt.plot(x, residuals, '.', label=label)
    plt.legend()


def plot_image(data):
    """TBW.

    :param data:
    :return:
    """
    plt.imshow(data, cmap=plt.gray())  # , interpolation='nearest')
    plt.xlabel('x - serial direction')
    plt.ylabel('y - parallel direction')
    plt.title('CCD image with CTI')
    plt.colorbar()


# def write_fits_file(data, output, unsigned16bit=True):
#     """Write out FITS files using PyFITS.
#
#     :param data: data to write to a FITS file
#     :type data: ndarray
#     :param output: name of the output file
#     :type output: string
#     :param unsigned16bit: whether to scale the data using bzero=32768
#     :type unsigned16bit: bool
#
#     :return: None
#     """
#     if os.path.isfile(output):
#         os.remove(output)
#
#     # create a new FITS file, using HDUList instance
#     ofd = fits.HDUList(fits.PrimaryHDU())
#
#     # new image HDU
#     hdu = fits.ImageHDU(data=data)
#
#     # convert to unsigned 16bit int if requested
#     if unsigned16bit:
#         hdu.scale('int16', '', bzero=32768)
#         hdu.header.add_history('Scaled to unsigned 16bit integer!')
#
#     # update and verify the header
#     # hdu.header.add_history('If questions, please contact Sami-Matias Niemi (s.niemi at ucl.ac.uk).')
#     # hdu.header.add_history('This file has been created with the VISsim Python Package at %s'
#     #                        % datetime.datetime.isoformat(datetime.datetime.now()))
#     # hdu.verify('fix')
#
#     ofd.append(hdu)
#
#     # write the actual file
#     ofd.writeto(output)
#
#
# if __name__ == '__main__':
#     main()
