#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase-pulse processing model."""

import numpy as np

import scipy.integrate as integrate

import scipy.constants as const

from pyxel.detectors import MKID


def convert_to_phase(
    array: np.ndarray,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> np.ndarray:
    """Convert an array of charge into phase.

    Parameters
    ----------
    array : ndarray
    wavelength : float
    responsivity : float
    scaling_factor : float

    Returns
    -------
    ndarray
    """
    if not wavelength > 0:
        raise ValueError("Only positive values accepted for wavelength.")
    if not scaling_factor > 0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0:
        raise ValueError("Only positive values accepted for responsivity.")
    
    Tc = 1.2 # Critical temperature, for Aluminium [K]
    TD = 433 # Debye temperature, for Aluminium [K]
    N0 = 1.72e4 # Electronic density of states at Fermi surface, for Aluminium [µeV^-1 µm^-3]
    lbd0 = 0.092 # Penetration depth at T = 0 [µm] (0.092 for Aluminium, by default)
    kbT0 = 86.17 * 0.2 # Boltzmann's constant * bath temperature [µeV]
    kbT = 86.17 * 0.2 # Boltzmann's constant * quasi-particle temperature [µeV]
    hw0 = 0.6582 * 5 * 2 * np.pi # Reduced Planck’s constant * angular resonance frequency at T0
    ak = 0.0268 # Kinetic inductance fraction
    beta = 2 # = 2 in the thin-film limit (= 1 in the bulk) [CHECK FUNCTION BELOW]
    Qc = 2e4 # Coupling quality factor
    SCvol = SC.Vol(SC.Al(), .05, 15.)
    SC = SCvol.SC
    d = SCvol.d # Film thickness [µm]
    V = SCvol.V # Superconductor's volume [µm]

    kbTc = Tc * const.Boltzmann / const.e * 1e6  # Critical temperature [µeV]
    kbTD = TD * const.Boltzmann / const.e * 1e6  # Debye's energy [µeV]
    D0 = 1.76 * kbTc # BSC relation for the energy gap at
    D_0 = D(kbT, SC)
    hwread = hwread(hw0, kbT0, ak, kbT, D_0, SCvol) # Gives the read frequency such that it is equal to the resonance frequency

    s_0 = cinduct(hwread, D_0, kbT)
    Qi_0 = 2 * s_0[1] / (ak * beta * s_0[0])
    Q = Qi_0 * Qc / (Qi_0 + Qc)

    row_of_pixels, column_of_pixels = array.shape
    linearised_DeltaA = np.zeros((row_of_pixels, column_of_pixels))
    linearised_theta = np.zeros((row_of_pixels, column_of_pixels))

    for row_idx in range(row_of_pixels):
        for col_idx in range(column_of_pixels):
            
            Nqp = array[row_idx, col_idx]
                     
            kbTeff = kbTeff(Nqp / V, SC)
            D = D(kbTeff, SC) # Energy gap
            s1, s2 = cinduct(hwread, D, kbTeff)

            # Calculate changes in amplitude and phase
            linearised_DeltaA[row_idx, col_idx] = ak * beta * Q * (s1 - s_0[0]) / s_0[1]
            linearised_theta[row_idx, col_idx] = -ak * beta * Q * (s2 - s_0[1]) / s_0[1]

    output = linearised_theta * scaling_factor

    return output.astype("float64")


def pulse_processing(
    detector: MKID,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> None:
    """TBW.

    Parameters
    ----------
    detector : MKID
        Pyxel :term:`MKID` detector object.
    wavelength : float
        Wavelength.
    responsivity : float
        Responsivity of the pixel.
    scaling_factor : float
        Scaling factor taking into account the missing pieces of superconducting physics,
        as well as the resonator quality factor, the bias power,
        the quasi-particle losses, etc.
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting a MKID object for the detector.")

    detector.phase.array = convert_to_phase(
        array=detector.charge.array,
        wavelength=wavelength,
        responsivity=responsivity,
        scaling_factor=scaling_factor,
    )


"""
.......... From https://github.com/sahderooij/
"""


def cinduct(hw, D, kbT):
    '''Mattis-Bardeen equations.'''

    def integrand11(E, hw, D, kbT):
        nume = 2 * (f(E, kbT) - f(E + hw, kbT)) * np.abs(E ** 2 + D ** 2 + hw * E)
        deno = hw * ((E ** 2 - D ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno

    def integrand12(E, hw, D, kbT):
        nume = (1 - 2 * f(E + hw, kbT)) * np.abs(E ** 2 + D ** 2 + hw * E)
        deno = hw * ((E ** 2 - D ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno

    def integrand2(E, hw, D, kbT):
        nume = (1 - 2 * f(E + hw, kbT)) * np.abs(E ** 2 + D ** 2 + hw * E)
        deno = hw * ((D ** 2 - E ** 2) * ((E + hw) ** 2 - D ** 2)) ** 0.5
        return nume / deno

    s1 = integrate.quad(integrand11, D, np.inf, args = (hw, D, kbT))[0]
    if hw > 2 * D:
        s1 += integrate.quad(integrand12, D - hw, -D, args = (hw, D, kbT))[0]
    s2 = integrate.quad(integrand2, np.max([D - hw, -D]), D, args = (hw, D, kbT))[0]
    return s1, s2


def hwread(hw0, kbT0, ak, kbT, D, SCvol):
    '''Calculates at which frequency, one probes at resonance. 
    This must be done iteratively, as the resonance frequency is 
    dependent on the complex conductivity, which in turn depends on the
    read frequency.'''
    
    s20 = cinduct(hw0, D, kbT0)[1]

    def minfuc(hw, hw0, s20, ak, kbT, D, SCvol):
        s1, s2 = cinduct(hw, D, kbT)
        return np.abs(hwres(s2, hw0, s20, ak, kbT, D, SCvol) - hw)
   
    res = minisc(
        minfuc,
        bracket=(0.5 * hw0, hw0, 2 * hw0),
        args=(hw0, s20, ak, kbT, D, SCvol),
        method="brent",
        options={"xtol": 1e-21},
    )
    if res.success:
        return res.x


def hwres(s2, hw0, s20, ak, kbT, D, SCsheet):
    '''Gives the resonance frequency in µeV, from the sigma2,
    from a linearization from point hw0,sigma20. See PdV PhD eq. (2.24).'''

    b = beta(kbT, D, SCsheet)
    return hw0 * (1 + ak * b / 4 / s20 * (s2 - s20))  # (linearized)


def D(kbT, SC):
    '''Calculates the thermal average energy gap, Delta. Tries to load Ddata,
    but calculates from scratch otherwise. Then, it cannot handle arrays.'''

    Ddata = SC.Ddata
    if Ddata is not None:
        Dspl = interpolate.splrep(Ddata[0, :], Ddata[1, :], s=0)
        return np.clip(interpolate.splev(kbT, Dspl), 0, None)
    else:
        warnings.warn(
            "D calculation takes long.. \n Superconductor={}\n N0={}\n kbTD={}\n Tc={}".format(
                SC.name, SC.N0, SC.kbTD, SC.kbTc / (const.Boltzmann / const.e * 1e6)
            )
        )

        def integrandD(E, D, kbT, SC):
            return SC.N0 * SC.Vsc * (1 - 2 * f(E, kbT)) / np.sqrt(E ** 2 - D ** 2)

        def dint(D, kbT, SC):
            return np.abs(
                integrate.quad(integrandD, D, SC.kbTD, args=(D, kbT, SC), points=(D,))[
                    0
                ]
                - 1
            )

        res = minisc(dint, args=(kbT, SC), method="bounded", bounds=(0, SC.D0))
        if res.success:
            return np.clip(res.x, 0, None)


def kbTeff(nqp, SC):
    '''Calculates the effective temperature (in µeV) at a certain 
   quasiparticle density.'''

    Ddata = SC.Ddata
    if Ddata is not None:
        kbTspl = interpolate.splrep(Ddata[2, :], Ddata[0, :],
                                   s=0, k=1)
        return interpolate.splev(nqp, kbTspl)
    else:
        def minfunc(kbT, nqp, SC):
            Dt = D(kbT, SC)
            return np.abs(nqp(kbT, Dt, SC) - nqp)
        res = minisc(
            minfunc,
            bounds=(0, 0.9 * SC.kbTc),
            args=(nqp, SC),
            method="bounded",
            options={"xatol": 1e-15},
        )
        if res.success:
            return res.x


def nqp(kbT, D, SC):
    '''Thermal average quasiparticle denisty. It can handle arrays 
    and uses a low temperature approximation, if kbT < Delta/100.'''

    if np.array(kbT < D / 100).all():
        return 2 * SC.N0 * np.sqrt(2 * np.pi * kbT * D) * np.exp(-D / kbT)
    else:

        def integrand(E, kbT, D, SC):
            return 4 * SC.N0 * E / np.sqrt(E ** 2 - D ** 2) * f(E, kbT)

        if any(
            [
                type(kbT) is float,
                type(D) is float,
                type(kbT) is np.float64,
                type(D) is np.float64,
            ]
        ):  # make sure it can deal with kbT,D arrays
            return integrate.quad(integrand, D, np.inf, args=(kbT, D, SC))[0]
        else:
            assert kbT.size == D.size, "kbT and D arrays are not of the same size"
            result = np.zeros(len(kbT))
            for i in range(len(kbT)):
                result[i] = integrate.quad(
                    integrand, D[i], np.inf, args=(kbT[i], D[i], SC)
                )[0]
            return result


def beta(lbd0, d, D, D0, kbT):
    '''Calculates beta, a measure for how thin the film is, 
    compared to the penetration depth.'''

    lbd = lbd0 * 1 / np.sqrt(D / D0 * np.tanh(D / (2 * kbT)))
    return 1 + 2 * d / (lbd * np.sinh(2 * d / lbd))


class Vol(Sheet):
    '''A superconducting sheet of volume V, width w and lenght l.'''

    def __init__(self, SC, d, V, w=np.nan, l=np.nan, tesc=1e-12, tescerr=0):
        super().__init__(SC, d, tesc, tescerr)
        self.V = V
        self.w = w
        self.l = l

    def checkV(self):
        return self.w * self.l * self.d == self.V

    @property
    def Ic(self):
        return self.SC.jc * self.w * self.d


class Sheet(object):
    '''A superconducting sheet with a certain thickness d and phonon escape
    time tesc.'''

    def __init__(self, SC, d, tesc=1e-12, tescerr=0):
        self.SC = SC
        self.d = d
        self.tesc = tesc
        self.tescerr = tescerr

    @property
    def Rs(self):
        '''Returns the sheet resistance in µOhm/sq'''
        return self.SC.rhon / (self.d * 1e-4)

    @property
    def Lks(self):
        '''Returns the sheet inductance in pH/sq'''
        return const.hbar * 1e12 / const.e * self.Rs / (np.pi * self.SC.D0)

    def set_tesc(self, Chipnum, KIDnum, **kwargs):
        """sets the tesc attribute to a value calculated from the kidcalc.calc.tesc function,
        which uses GR noise lifetimes at high temperatures."""
        import kidata
