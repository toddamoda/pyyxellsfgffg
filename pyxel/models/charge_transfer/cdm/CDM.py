"""Charge Distortion Model for CCDs.

============================
This is a function to run the upgraded CDM CTI model developed by Alex Short (ESA).

:requires: NumPy

:author: Alex Short
:author: Sami-Matias Niemi
:author: David Lucsanyi
"""
import numpy as np
try:
    import matplotlib.pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')
    pass
import numba
from typing import cast
from pyxel.detectors.ccd import CCD
from pyxel.detectors.ccd_characteristics import CCDCharacteristics  # noqa: F401
from pyxel.pipelines.model_registry import registry


@registry.decorator('charge_transfer', name='cdm', detector='ccd')
def cdm(detector: CCD,
        beta_p: float = None, beta_s: float = None,
        chg_inj: bool = None,
        parallel_cti: bool = None, serial_cti: bool = None,
        para_transfers: int = None,
        tr_p: float = None, tr_s: float = None,
        nt_p: float = None, nt_s: float = None,
        sigma_p: float = None, sigma_s: float = None,
        parallel_trap_file: str = None,
        serial_trap_file: str = None
        ) -> CCD:
    """
    CDM model wrapper.

    :param detector: PyXel CCD detector object
    :param beta_p: electron cloud expansion coefficient (parallel)
    :param beta_s: electron cloud expansion coefficient (serial)
    # :param vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
    # :param svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
    # :param t: constant TDI period (parallel)
    # :param st: constant TDI period (serial)
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

    if isinstance(tr_p, list):
        tr_p = np.array(tr_p)
    if isinstance(tr_s, list):
        tr_s = np.array(tr_s)
    if isinstance(nt_p, list):
        nt_p = np.array(nt_p)
    if isinstance(nt_s, list):
        nt_s = np.array(nt_s)
    if isinstance(sigma_p, list):
        sigma_p = np.array(sigma_p)
    if isinstance(sigma_s, list):
        sigma_s = np.array(sigma_s)

    new_detector.pixels.array = run_cdm(s=new_detector.pixels.array,   # self.fullframe[dataset],
                                        beta_p=beta_p, beta_s=beta_s,
                                        vg=char.vg, svg=char.svg,
                                        t=char.t, st=char.st,
                                        fwc=char.fwc, sfwc=char.fwc_serial,
                                        vth=new_detector.e_thermal_velocity,
                                        parallel_cti=parallel_cti, serial_cti=serial_cti,
                                        charge_injection=chg_inj,
                                        all_parallel_trans=para_transfers,
                                        sigma_p=sigma_p, sigma_s=sigma_s,
                                        tr_p=tr_p, tr_s=tr_s,
                                        nt_p=nt_p, nt_s=nt_s)

    return new_detector


@numba.jit
def run_cdm(s: np.ndarray,
            # y_start: int,
            # x_start: int,
            # ydim: int,
            # xdim: int,
            # rdose: float,
            # dob: float,
            beta_p: float,
            beta_s: float,
            vg: float,
            svg: float,
            t: float,
            st: float,
            fwc: float,
            sfwc: float,
            vth: float,
            tr_p: np.ndarray, tr_s: np.ndarray,
            nt_p: np.ndarray, nt_s: np.ndarray,
            sigma_p: np.ndarray, sigma_s: np.ndarray,
            charge_injection: bool = False,
            all_parallel_trans: int = 0,
            parallel_cti: bool = True,
            serial_cti: bool = True,
            ):
    """CDM model.

    :param s: np.ndarray
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
    :param sigma_p:
    :param sigma_s:
    :param tr_p:
    :param tr_s:
    :param nt_p: number of traps per electron cloud (and not pixel!) in parallel direction
    :param nt_s: number of traps per electron cloud (and not pixel!) in serial direction
    :param parallel_cti:
    :param serial_cti:
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

    # s = s + dob                 # diffuse optical background
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
        alpha_p = t * sigma_p * vth * fwc ** beta_p / (2. * vg)     # type: np.ndarray
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
                                 (1. - np.exp(-1 * alpha_p[k] * s[i, j] ** (1. - beta_p))), 0.)
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
        alpha_s = st * sigma_s * vth * sfwc ** beta_s / (2. * svg)      # type: np.ndarray
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
                                 (1. - np.exp(-1 * alpha_s[k] * s[i, j] ** (1. - beta_s))), 0.)
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
    """Plot profile on log scale.

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
