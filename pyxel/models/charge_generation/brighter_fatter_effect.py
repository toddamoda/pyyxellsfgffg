#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Model for brighter-fatter-effect."""
from typing import Sequence

import numba
import numpy as np
from astropy.convolution import Gaussian2DKernel, convolve_fft

from pyxel.detectors import Detector

# @numba.njit(fastmath=False)
# def get_gaussian_kernel(size, sigma):
#     center = size // 2
#     x, y = np.mgrid[0:size, 0:size]
#     x = x - center
#     y = y - center
#     kernel = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
#     return kernel / np.sum(kernel)


def simple_bfe(
    detector: Detector,
    a,
    b,
    c,
    alpha: float,
    beta: float,
    normalize_kernel: bool = True,
) -> None:
    """Get BFE for photon array and convolve the photon array with the BFE.
    coefficients: Sequence[float]
        Parameters
        ----------
        detector : Detector
            Pyxel Detector object.
        coefficients : list of float
            Coefficient of the polynomial function.
        normalize_kernel : bool
            Normalize kernel.
    """
    # a = coefficients[0]
    # b = coefficients[1]
    # c = coefficients[2]

    signal = detector.photon.array

    mean = np.mean(detector.photon.array)
    theta = a + b * signal + c * signal**2

    theta_fwc = (
        a
        + b * detector.characteristics.full_well_capacity
        + c * detector.characteristics.full_well_capacity**2
    )

    ###
    # signal_max = np.max(signal)
    # sigma_max = a + b * signal_max + c * signal_max ** 2
    # norm = (1 / np.max(sigma_max)) * sigma
    # std = np.sqrt(np.mean(norm))
    ###
    # norm_sigma = 1 + (sigma / sigma_fwc)
    norm_sigma = alpha + beta * ((1 / np.max(theta_fwc)) * theta)
    # 0.27 * (1.2+(1 / np.max(theta_fwc)) * theta)
    # 3 # alpha + beta*(
    # 2a # alpha * (beta +
    std = np.mean(norm_sigma)  # just for now in pyxel
    # sigma_array = polynomial_function(signal)
    kernel = Gaussian2DKernel(x_stddev=std, x_size=9)  # , y_size=3)
    # n1_list = []
    # n2_list = []
    # center = kernel.array[1][1]
    # n1 = kernel.array[0][1]
    # n2 = kernel.array[0][0]
    # fraction1 = n1 / center
    # n1_list.append(fraction1)
    # fraction2 = n2 / center
    # n2_list.append(fraction2)
    conv = convolve_fft(
        signal,
        kernel=kernel,
        boundary="fill",
        fill_value=mean,
        normalize_kernel=normalize_kernel,
    )

    detector.photon.array = conv
    # return n1_list, n2_list


@numba.njit(fastmath=False)
def apply_bfe(signal: np.ndarray, coefficients: Sequence[float]) -> np.ndarray:
    """Get BFE for photon array and convolve the photon array with the BFE.

    Parameters
    ----------
    signal
    coefficients : list of float
        Coefficient of the polynomial function.
    """

    a = coefficients[0]
    b = coefficients[1]
    c = coefficients[2]

    mean = np.mean(signal)
    sigma_array = a + b * signal + c * signal**2
    norm_sigma = (1 / np.max(sigma_array)) * sigma_array
    num_y, num_x = signal.shape
    data_2d = np.ones(signal.shape)
    new_data_2d = signal.copy()
    for k in range(num_x):
        for l in range(num_y):
            # take sigma from sigma array at this pixel
            sigma = norm_sigma[k, l]
            size = 3
            # gaussian_2d = np.asarray(Gaussian2DKernel(x_stddev=sigma, x_size=3))
            kernel = np.zeros((size, size))
            for m in range(size):
                for n in range(size):
                    x = n - (size // 2)
                    y = m - (size // 2)
                    kernel[m, n] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
            gaussian_2d = kernel / np.sum(kernel)
            for i in range(1, num_x - 1):
                for j in range(1, num_y - 1):
                    new_data_2d[i - 1, j - 1] += (
                        gaussian_2d[0, 0] * data_2d[i - 1, j - 1]
                    )
                    new_data_2d[i, j - 1] += gaussian_2d[0, 1] * data_2d[i, j - 1]
                    new_data_2d[i + 1, j - 1] += (
                        gaussian_2d[0, 2] * data_2d[i + 1, j - 1]
                    )
                    new_data_2d[i - 1, j] += gaussian_2d[1, 0] * data_2d[i - 1, j]
                    new_data_2d[i, j] += (
                        gaussian_2d[1, 1] * data_2d[i, j]
                    )  # Note: this is the blue X
                    new_data_2d[i + 1, j] += gaussian_2d[1, 2] * data_2d[i + 1, j]
                    new_data_2d[i - 1, j + 1] += (
                        gaussian_2d[2, 0] * data_2d[i - 1, j + 1]
                    )
                    new_data_2d[i, j + 1] += gaussian_2d[2, 1] * data_2d[i, j + 1]
                    new_data_2d[i + 1, j + 1] += (
                        gaussian_2d[2, 2] * data_2d[i + 1, j + 1]
                    )

    new_signal = data_2d + new_data_2d

    return new_signal


def brighter_fatter(detector: Detector, coefficients: Sequence[float]) -> None:
    # signal = detector.photon.array
    new_signal = apply_bfe(signal=detector.photon.array, coefficients=coefficients)

    detector.photon.array = new_signal

    # print(df)
    # i j raussuchen und dann convoluted images ineinander stacken.
    # polynomial_function = np.polynomial.polynomial.Polynomial(coefficients)
    # sigma_array = polynomial_function(detector.photon.array)
    # list = []
    # for sigma in sigma_array:
    #     kernel = Gaussian2DKernel(x_stddev=sigma)
    #     mean = np.mean(detector.photon.array)
    #
    #     array_2d = convolve_fft(
    #         detector.photon.array,
    #         kernel=kernel,
    #         boundary="fill",
    #         fill_value=mean,
    #         normalize_kernel=normalize_kernel,
    #     )
    #     list.append(array_2d)
    # print(list)
    # sigma = np.max(detector.photon.array)

    # detector.photon.array = apply_bfe(
    #     array=detector.photon.array, sigma=sigma, normalize_kernel=normalize_kernel
    # )
    # polynomial_function = np.polynomial.polynomial.Polynomial(coefficients)

    # convolutions = []
    # i = 0
    # for row in norm_sigma:
    #     for val in row:
    #         i += 1
    #         kernel = Gaussian2DKernel(x_stddev=val, x_size=3)  # , y_size=3)
    #         conv = convolve_fft(
    #             signal,
    #             kernel=kernel,
    #             boundary="fill",
    #             fill_value=mean,
    #             normalize_kernel=normalize_kernel,
    #         )
    #         convolutions.append(conv)
    # for value, j in zip(convolutions, range(0, len(convolutions))):
    #     print("value: ", value)#df[f'{j}'] = value
    #     print(j)
