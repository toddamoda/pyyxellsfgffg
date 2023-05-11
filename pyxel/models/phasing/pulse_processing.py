#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase-pulse processing model."""


import numpy as np

from pyxel.detectors import MKID

# import scipy.constants as const


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
    from pyxel.models.phasing.mkid_models import SC as sclib
    from pyxel.models.phasing.mkid_models import SCtheory as sctheory

    if not wavelength > 0:
        raise ValueError("Only positive values accepted for wavelength.")
    if not scaling_factor > 0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0:
        raise ValueError("Only positive values accepted for responsivity.")

    # Tc = 1.2  # Critical temperature, for Aluminium [K]
    # TD = 433  # Debye temperature, for Aluminium [K]
    # N0 = 1.72e4  # Electronic density of states at Fermi surface, for Aluminium [µeV^-1 µm^-3]
    # lbd0 = 0.092  # Penetration depth at T = 0 [µm] (0.092 for Aluminium, by default)
    kbT0 = 86.17 * 0.2  # Boltzmann's constant * bath temperature [µeV]
    kbT = 86.17 * 0.2  # Boltzmann's constant * quasi-particle temperature [µeV]
    hw0 = (
        0.6582 * 5 * 2 * np.pi
    )  # Reduced Planck’s constant * angular resonance frequency at T0
    ak = 0.0268  # Kinetic inductance fraction
    beta = 2  # = 2 in the thin-film limit (= 1 in the bulk) [CHECK FUNCTION BELOW]
    Qc = 2e4  # Coupling quality factor
    SCvol = sclib.Vol(SC=sclib.Al, d=0.05, V=15.0)
    SC = SCvol.SC
    # d = SCvol.d  # Film thickness [µm]
    V = SCvol.V  # Superconductor's volume [µm]

    # kbTc = Tc * const.Boltzmann / const.e * 1e6  # Critical temperature [µeV]
    # kbTD = TD * const.Boltzmann / const.e * 1e6  # Debye's energy [µeV]
    # D0 = 1.76 * kbTc  # BSC relation for the energy gap at
    D_0 = sctheory.D(kbT, SC)
    hwread: float = sctheory.hwread(
        hw0=hw0, kbT0=kbT0, ak=ak, kbT=kbT, D=D_0, SCvol=SCvol
    )  # Gives the read frequency such that it is equal to the resonance frequency

    s_0: tuple[float, float] = sctheory.cinduct(hw=hwread, D=D_0, kbT=kbT)
    Qi_0 = 2 * s_0[1] / (ak * beta * s_0[0])
    Q = Qi_0 * Qc / (Qi_0 + Qc)

    row_of_pixels, column_of_pixels = array.shape
    linearised_DeltaA = np.zeros((row_of_pixels, column_of_pixels))
    linearised_theta = np.zeros((row_of_pixels, column_of_pixels))

    for row_idx in range(row_of_pixels):
        for col_idx in range(column_of_pixels):
            Nqp = array[row_idx, col_idx]

            kbTeff = sctheory.kbTeff(nqp=Nqp / V, SC=SC)
            D = sctheory.D(kbTeff, SC)  # Energy gap
            s1, s2 = sctheory.cinduct(hw=hwread, D=D, kbT=kbTeff)

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
