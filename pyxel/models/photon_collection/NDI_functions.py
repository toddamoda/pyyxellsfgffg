# Copyright (c) 2023 Alejandro Camazon Pinilla, University of Florida, ARRAKIHS Mission Consortium
#
# acamazon@ufl.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Normalized Detector Irradiance functions to calculate the straylight in the detector."""

import numpy as np
from scipy import interpolate


def NDI_iSIM170(x: np.ndarray):
    """Compute NDI function of iSIM-170 Earth Observation.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    p_1 = np.array([105.44586205, 2.06647369])

    def g_1(x: np.ndarray):
        return np.log10(p_1[0] * 1 / (1 + (x / p_1[1]) ** 2))

    def f_1(x: np.ndarray):
        x_ndi = np.array([1e-6, 0.43, 0.7, 1])
        y_ndi = np.array([105.4458618, 102.4384568, 1, 0.03])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def h_1(x: np.ndarray):
        x_ndi = np.array([1, 2, 5, 10, 20, 40, 60, 80, 100, 120, 150, 180])
        y_ndi = np.array(
            [
                0.03,
                0.002194029,
                0.000301812,
                0.0000386146,
                0.00000276223,
                0.00000001,
                0.000000001,
                0.0000000001,
                1e-12,
                1e-14,
                1e-18,
                1e-20,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 1), (x >= 1)],
        [lambda x: g_1(x), lambda x: f_1(x), lambda x: h_1(x)],
    )


def NDI_GOAL(x: np.ndarray):
    """Compute NDI function Goal for ARRAKIHS mission.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    p_2 = np.array([105.44586205, 2.06647369])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def f_2(x: np.ndarray):
        x_ndi = np.array([1e-6, 0.43, 0.7, 1])
        y_ndi = np.array([105.4458618, 102.4384568, 0.3, 4.5897136e-03])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 20])

        y_ndi = np.array(
            [
                4.5897136e-03,
                2.1940290e-04,
                8.00e-05,
                3.0181200e-05,
                4.72251e-06,
                1.18907e-06,
                2.22085e-07,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([20, 25, 30, 35, 40, 45, 50, 55, 60, 65])
        y_ndi = np.array(
            [
                2.22085e-07,
                4.99547e-10,
                1.03640e-10,
                3.72823e-11,
                1.84191e-11,
                9.79344e-12,
                4.45596e-12,
                2.07647e-12,
                7.98019e-13,
                1.41697e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([65, 80, 100, 120, 150, 180])
        y_ndi = np.array(
            [
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [
            x < 0.43,
            (x >= 0.43) & (x < 1),
            (x >= 1) & (x < 20),
            (x >= 20) & (x < 65),
            (x >= 65),
        ],
        [
            lambda x: g_2(x),
            lambda x: f_2(x),
            lambda x: h_2(x),
            lambda x: n_2(x),
            lambda x: k_2(x),
        ],
    )


def NDI_CONOPS_C_90(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-C and zenith angle ≤ 90.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """

    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 3e-06, 2e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80])
        y_ndi = np.array(
            [
                1e-06,
                5.0e-8,
                1.03640e-9,
                3.72823e-10,
                1.84191e-10,
                9.79344e-11,
                4.45596e-11,
                2.07647e-11,
                7.98019e-12,
                2.0e-12,
                5e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array(
            [
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
                1.41697e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 21), (x >= 21) & (x < 85), (x >= 85)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def NDI_CONOPS_B_90(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-B and zenith angle ≤ 90.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """

    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 3e-06, 2e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 35, 45, 55, 60, 70, 80])
        y_ndi = np.array(
            [
                2.2e-06,
                3.0e-8,
                7.0e-10,
                2.0e-10,
                4.45596e-11,
                9.0e-12,
                5e-12,
                1.0e-12,
                1e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array([1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 21), (x >= 21) & (x < 80), (x >= 80)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def NDI_CONOPS_C_80(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-C and zenith angle ≤ 80.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 3e-06, 2e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 40, 50, 60, 70, 80, 90])
        y_ndi = np.array(
            [2e-06, 1.0e-7, 1.0e-8, 1e-9, 1.0e-10, 2.0e-11, 5.0e-12, 1e-12, 1e-13]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array([1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 21), (x >= 21) & (x < 90), (x >= 90)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def NDI_CONOPS_B_80(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-B and zenith angle ≤ 80.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """

    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 3e-06, 2e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 40, 50, 60, 70, 80, 90])
        y_ndi = np.array(
            [1.3e-06, 1.0e-7, 5.0e-9, 5e-10, 8.0e-11, 1.5e-11, 3.0e-12, 8e-13, 1e-13]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array([1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 21), (x >= 21) & (x < 90), (x >= 90)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def NDI_CONOPS_B_70(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-B and zenith angle ≤ 70.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 4e-06, 4e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 40, 50, 60, 70, 80, 90])
        y_ndi = np.array(
            [3e-06, 4.0e-7, 8.0e-8, 8.0e-9, 8.0e-10, 8.0e-11, 1.0e-11, 1e-12, 1e-13]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array([1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 20), (x >= 20) & (x < 90), (x >= 90)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def NDI_CONOPS_C_70(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-C and zenith angle ≤ 70.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def f_1(x: np.ndarray):
        x_ndi = np.array([1e-6, 0.43, 0.7, 1])
        y_ndi = np.array([0.291688896864177, 0.1, 0.05, 2e-2])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def h_1(x: np.ndarray):
        x_ndi = np.array([1, 2, 5, 10, 20, 40, 60, 100, 120, 150, 180])
        y_ndi = np.array(
            [
                0.02,
                0.002,
                0.0002,
                0.00002,
                2e-06,
                1e-8,
                3e-10,
                5e-13,
                1e-13,
                1e-13,
                1e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 1), (x >= 1)],
        [lambda x: g_2(x), lambda x: f_1(x), lambda x: h_1(x)],
    )


def NDI_moon(x: np.ndarray):
    """Compute NDI function for the Moon in the ARRAKIHS mission.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    f = np.full_like(x, 1.0e-06)
    return f


def NDI_outfield_stars(x: np.ndarray):
    """Compute NDI function for the outfield stars in the ARRAKIHS mission.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """

    def g_1(x: np.ndarray):
        x_ndi = np.array([1e-6, 0.43, 0.7, 1])
        y_ndi = np.array(
            [0.291688896864177, 0.291688896864177, 0.291688896864177, 0.291688896864177]
        )
        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def h_1(x: np.ndarray):
        x_ndi = np.array([1, 2, 5, 10, 20, 40, 60, 80, 100, 120, 150, 180])
        y_ndi = np.array(
            [
                0.18,
                0.045,
                0.0045,
                0.00045,
                0.000045,
                8e-7,
                3e-8,
                1e-9,
                1e-11,
                1e-13,
                1e-13,
                1e-13,
            ]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x, [x < 0.7, x >= 0.7], [lambda x: g_1(x), lambda x: h_1(x)]
    )


def final_ndi_70_indv(x: np.ndarray):
    """Compute final NDI requirement for the ARRAKIHS mission in CONOPS-C and zenith angle ≤ 70 (each contributions: mu >24.5 mag/arcsec2).

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    f = np.piecewise(
        x,
        [x < 15, (x >= 15) & (x < 23), (x >= 23)],
        [
            lambda x: NDI_outfield_stars(x),
            lambda x: NDI_moon(x),
            lambda x: NDI_CONOPS_C_70(x),
        ],
    )
    return f


def final_ndi_90_indv(x: np.ndarray):
    """Compute final NDI requirement for the ARRAKIHS mission in CONOPS-C and zenith angle ≤ 90 (each contributions: mu >24.5 mag/arcsec2).

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    f = np.piecewise(
        x,
        [x < 15, (x >= 15) & (x < 21), (x >= 21)],
        [
            lambda x: NDI_outfield_stars(x),
            lambda x: NDI_moon(x),
            lambda x: NDI_CONOPS_C_90(x),
        ],
    )
    return f


def final_ndi_70(x: np.ndarray):
    """Compute final NDI requirement for the ARRAKIHS mission in CONOPS-C and zenith angle ≤ 70 (all contributions: mu >24.5 mag/arcsec2).

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    f = np.piecewise(
        x,
        [x < 15, (x >= 15) & (x < 35), (x >= 35)],
        [
            lambda x: NDI_outfield_stars(x) / 1.9,
            lambda x: NDI_moon(x) / 50,
            lambda x: NDI_CONOPS_C_70(x) / 1.9,
        ],
    )
    return f


def final_ndi_90(x: np.ndarray):
    """Compute Final NDI requirement for the ARRAKIHS mission in CONOPS-C and zenith angle ≤ 90 (all contributions: mu >24.5 mag/arcsec2).

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """
    f = np.piecewise(
        x,
        [x < 15, (x >= 15) & (x < 26.5), (x >= 26.5)],
        [
            lambda x: NDI_outfield_stars(x) / 1.65,
            lambda x: NDI_moon(x) / 50,
            lambda x: NDI_CONOPS_C_90(x) / 1.65,
        ],
    )
    return f


def NDI_CONOPS_BASELINE_85(x: np.ndarray):
    """Compute NDI function for ARRAKIHS mission in CONOPS-BASELINE and zenith angle ≤ 85.

    Parameters
    ----------
    x: float.
        angular separation, theta.
    """

    p_2 = np.array([0.291688896864177, 0.28])

    def g_2(x: np.ndarray):
        return np.log10(p_2[0] * 1 / (1 + (x / p_2[1]) ** 2))

    def h_2(x: np.ndarray):
        x_ndi = np.array([1, 2, 3.5, 5, 10, 15, 24])

        y_ndi = np.array([7.5e-03, 5e-04, 1.00e-04, 5e-05, 8e-06, 3e-06, 2e-07])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def n_2(x: np.ndarray):
        x_ndi = np.array([19, 25, 30, 40, 50, 60, 70, 80, 90])
        y_ndi = np.array(
            [1.3e-06, 1.0e-7, 5.0e-9, 5e-10, 8.0e-11, 1.5e-11, 3.0e-12, 8e-13, 1e-13]
        )

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    def k_2(x: np.ndarray):
        x_ndi = np.array([70, 80, 100, 120, 150, 180])
        y_ndi = np.array([1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13, 1.0e-13])

        tck = interpolate.splrep(x_ndi, np.log10(y_ndi))
        return interpolate.splev(x, tck)

    return 10 ** np.piecewise(
        x,
        [x < 0.43, (x >= 0.43) & (x < 21), (x >= 21) & (x < 90), (x >= 90)],
        [lambda x: g_2(x), lambda x: h_2(x), lambda x: n_2(x), lambda x: k_2(x)],
    )


def requieremnt_ndi_baseline_85(x: np.ndarray):
    """Compute final NDI requirement for the ARRAKIHS mission in CONOPS-C and zenith angle ≤ 85 (all contributions: mu >24.5 mag/arcsec2) .

    Parameters
    ----------
    x: float
        angular separation, theta.
    """

    f = np.piecewise(
        x,
        [x < 24, (x >= 24)],
        [lambda x: NDI_outfield_stars(x), lambda x: NDI_CONOPS_BASELINE_85(x)],
    )
    return f / 2
