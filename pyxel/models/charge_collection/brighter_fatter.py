#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#

import numpy as np

import numba
import typing as t
from pathlib import Path
from pyxel.inputs_outputs import load_table

# if t.TYPE_CHECKING:
from pyxel.detectors import Detector


@numba.njit
def bf_convolve(a: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve the input array with the kernel of shift coefficients.

    Parameters
    ----------
    a: ndarray
    kernel: ndarray

    Returns
    -------
    result: ndarray
    """
    k = kernel.shape[0] // 2
    rows = a.shape[0]
    cols = a.shape[1]

    result = np.zeros(a.shape)

    for i in range(rows):
        for j in range(cols):
            array_slice_y = slice(max(0, i - k), min(rows, i + k + 1))
            array_slice_x = slice(max(0, j - k), min(rows, j + k + 1))
            kernel_slice_y = slice(max(0, k - i), min(2 * k + 1, k + rows - i))
            kernel_slice_x = slice(max(0, k - j), min(2 * k + 1, k + cols - j))

            out[array_slice_y, array_slice_x] += np.multiply(
                kernel[kernel_slice_y, kernel_slice_x],
                a[array_slice_y, array_slice_x],
            )

    return result


def bf_antilogus(
    charge: np.ndarray,
    a_R: np.ndarray,
    a_L: np.ndarray,
    a_T: np.ndarray,
    a_B: np.ndarray,
) -> np.ndarray:
    """Apply the Antilogus et al 2014 brighter-fatter model on the input array using shift coefficients.

    Parameters
    ----------
    charge: ndarray
    a_R: ndarray
        Shift coefficients array for the right border.
    a_L: ndarray
        Shift coefficients array for the left border.
    a_T: ndarray
        Shift coefficients array for the top border.
    a_B: ndarray
        Shift coefficients array for the bottom border.

    Returns
    -------
    charge: ndarray
        Updated array
    """
    ch = charge.copy()

    avg_right = border_avg(ch, border="right")
    avg_left = border_avg(ch, border="left")
    avg_top = border_avg(ch, border="top")
    avg_bottom = border_avg(ch, border="bottom")

    charge += (
        avg_right * bf_convolve(ch, a_R)
        + avg_left * bf_convolve(ch, a_L)
        + avg_top * bf_convolve(ch, a_T)
        + avg_bottom * bf_convolve(ch, a_B)
    )

    return charge


def border_avg(a: np.ndarray, border: str) -> np.ndarray:
    """Calculate average charge on the pixel borders.

    Parameters
    ----------
    a: ndarray
    border: str

    Returns
    -------
    out: ndarray
    """
    if border == "right":
        result = (a + np.concatenate((a[:, 1:], np.zeros((a.shape[0], 1))), axis=1)) / 2
    elif border == "left":
        result = (a + np.concatenate((np.zeros((a.shape[0], 1)), a[:, :-1]), axis=1)) / 2
    elif border == "top":
        result = (a + np.concatenate((np.zeros((1, a.shape[1])), a[:-1]), axis=0)) / 2
    elif border == "bottom":
        result = (a + np.concatenate((a[1:], np.zeros((1, a.shape[1]))), axis=0)) / 2
    else:
        raise ValueError("Unknown border.")
    return result


def calc_a_r(a: np.ndarray) -> np.ndarray:
    """TBW.

    Parameters
    ----------
    a

    Returns
    -------

    """
    n, m = a.shape

    if a.size < 2:
        raise ValueError("Input a_R too small.")
    if n != m + 1:
        raise ValueError("Wrong shape of input a_R")

    top_half = np.concatenate((-np.flip(a, axis=1), a), axis=1)
    zeros = np.zeros((n, 1))
    top_half_zeros = np.concatenate((zeros, top_half), axis=1)
    out = np.concatenate((top_half_zeros, np.flip(top_half_zeros, axis=0)[1:]), axis=0)
    return out


def calc_a_l(a: np.ndarray) -> np.ndarray:
    """TBW.

    Parameters
    ----------
    a

    Returns
    -------

    """
    return np.flip(calc_a_r(a), axis=1)


def calc_a_t(a: np.ndarray) -> np.ndarray:
    """TBW.

    Parameters
    ----------
    a

    Returns
    -------

    """
    n, m = a.shape

    if a.size < 2:
        raise ValueError("Input a_R too small.")
    if n + 1 != m:
        raise ValueError("Wrong shape of input a_R")

    right_half = np.concatenate((a, -np.flip(a, axis=0)), axis=0)
    zeros = np.zeros((1, m))
    right_half_zeros = np.concatenate((right_half, zeros), axis=0)
    out = np.concatenate(
        (np.flip(right_half_zeros, axis=1)[:, :-1], right_half_zeros), axis=1
    )
    return out


def calc_a_b(a: np.ndarray) -> np.ndarray:
    """TBW.

    Parameters
    ----------
    a

    Returns
    -------

    """
    return np.flip(calc_a_t(a), axis=0)


def get_matrix(matrix: t.Union[str, Path, list]) -> np.ndarray:
    """Get the coefficient matrix either from configuration input or a file.

    Parameters
    ----------
    matrix

    Returns
    -------
    ndarray
    """
    if isinstance(matrix, list):
        return np.array(matrix)
    else:
        return np.array(load_table(matrix))


def brighter_fatter(
    detector: Detector,
    right_coeff: t.Union[t.List, str, Path],
    top_coeff: t.Union[t.List, str, Path],
) -> None:
    """TBW.

    Parameters
    ----------
    detector
    right_coeff
    top_coeff

    Returns
    -------
    None
    """

    a_R_input = get_matrix(right_coeff)  # type: np.ndarray
    a_T_input = get_matrix(top_coeff)  # type: np.ndarray

    if a_R_input.shape != a_R_input.T.shape:
        raise ValueError("Input input shape does not match.")

    a_R = calc_a_r(a_R_input)
    a_L = calc_a_l(a_R_input)
    a_T = calc_a_t(a_T_input)
    a_B = calc_a_b(a_T_input)

    _ = bf_antilogus(charge=detector.pixel.array, a_R=a_R, a_L=a_L, a_T=a_T, a_B=a_B)


if __name__ == "__main__":

    import time

    a_R_input = np.array([[0.02, 0.01], [0.05, 0.03], [0.1, 0.05]])
    a_T_input = np.array([[0.05, 0.03, 0.01], [0.1, 0.05, 0.02]])

    a_R = calc_a_r(a_R_input)
    a_L = calc_a_l(a_R_input)
    a_T = calc_a_t(a_T_input)
    a_B = calc_a_b(a_T_input)

    array = np.ones((512, 512))
    start = time.time()
    out = bf_antilogus(charge=array, a_R=a_R, a_L=a_L, a_T=a_T, a_B=a_B)
    end = time.time()
    print("Elapsed (before compilation) = %s" % (end - start))

    #array = np.ones((512, 512))
    #start = time.time()
    #out = bf_antilogus(charge=array, a_R=a_R, a_L=a_L, a_T=a_T, a_B=a_B)
    #end = time.time()
    #print("Elapsed (after compilation) = %s" % (end - start))
