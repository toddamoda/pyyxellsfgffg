#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Model for brighter-fatter-effect."""

import numba
import numpy as np
import xarray as xr
from astropy.convolution import Gaussian2DKernel, convolve_fft
from datatree import DataTree

from pyxel.detectors import Detector


@numba.njit(fastmath=False)
def get_gaussian_kernel(size, sigma):
    center = size // 2
    x, y = np.mgrid[0:size, 0:size]
    x = x - center
    y = y - center
    kernel = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    return kernel / np.sum(kernel)


def simple_bfe(
    detector: Detector,
    a: float,
    b: float,
    c: float,
    alpha: float,
    beta: float,
    normalize_kernel: bool = True,
) -> None:
    """Get BFE for charge array and convolve the charge array with the varying input signal.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    a: float
        First coefficient in polynomial function.
    b: float
        Second coefficient in polynomial function.
    c: float
        Third coefficient in polynomial function.
    alpha: float
        Coefficient that defines where PTC curve starts.
    beta: float
        Coefficient that defines where the PTC curve breaks.
    normalize_kernel : bool
        Normalize kernel.
    """
    signal = detector.charge.array

    mean = np.mean(detector.charge.array)
    theta = a + b * signal + c * signal**2

    theta_fwc = (
        a
        + b * detector.characteristics.full_well_capacity
        + c * detector.characteristics.full_well_capacity**2
    )

    norm_sigma = alpha + beta * ((1 / theta_fwc) * theta)

    std = np.mean(norm_sigma)  # just for now in pyxel
    # print(std)

    # calculate 2D Gaussian kernel
    kernel = Gaussian2DKernel(x_stddev=std, x_size=9)  # , y_size=3)

    # calculate convolution of charge array with kernel
    conv = convolve_fft(
        signal,
        kernel=kernel,
        boundary="fill",
        fill_value=mean,
        normalize_kernel=normalize_kernel,
    )
    # Get current absolute time
    absolute_time = xr.DataArray(
        [detector.absolute_time],
        dims=["time"],
        attrs={"units": "s"},
    )
    dataset = xr.Dataset()
    dataset["sigma"] = xr.DataArray(std)
    dataset = dataset.expand_dims(dim="time").assign_coords(time=absolute_time)

    key = "kernel"
    key_partial = "kernel_partial"

    try:
        _ = detector.data[key_partial]
    except KeyError:
        has_key_partial = False
    else:
        has_key_partial = True

    if not has_key_partial:
        data_tree: DataTree = DataTree(dataset)
    else:
        # Concatenate data
        previous_datatree = detector.data[key_partial]
        data_tree = previous_datatree.combine_first(dataset)  # type: ignore

    if detector.pipeline_count == (detector.num_steps - 1):
        detector.data[key] = data_tree
    else:
        detector.data[key_partial] = data_tree

    # This is the last step and there is at least two steps
    if detector.num_steps > 1 and (detector.pipeline_count == (detector.num_steps - 1)):
        detector.data[key_partial].orphan()

    detector.charge.add_charge_array(conv)


@numba.njit(fastmath=False)
def bfe(data_2d, full_well_capacity, a, b, c, alpha: float, beta: float) -> np.ndarray:
    new_data_2d = np.zeros_like(data_2d)
    num_y, num_x = new_data_2d.shape

    # sigma_array = a + b * data_2d + c * data_2d**2
    theta = a + b * data_2d + c * data_2d**2
    theta_fwc = a + b * full_well_capacity + c * full_well_capacity**2
    # norm_sigma = (1 / np.max(sigma_array)) * sigma_array
    norm_sigma = alpha + beta * ((1 / theta_fwc) * theta)
    # std = np.mean(norm_sigma)

    for col in range(num_x):
        for row in range(num_y):
            sigma = norm_sigma[row, col]

            size = 3
            # gaussian_2d = np.asarray(Gaussian2DKernel(x_stddev=sigma, x_size=3))
            kernel = np.zeros((size, size))
            for m in range(size):
                for n in range(size):
                    x = n - (size // 2)
                    y = m - (size // 2)
                    kernel[m, n] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
            gaussian_2d = kernel / np.sum(kernel)

            # gaussian_2d = np.asarray(get_gaussian_kernel(size=3, sigma=sigma))
            # print(kernel, gaussian_2d)
            # Do this with 2 new for-loops
            # for k, l in range(x):
            #     for l in range(y):
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

    return data_2d + new_data_2d


def get_bfe(
    detector: Detector,
    a: float,
    b: float,
    c: float,
    alpha: float,
    beta: float,
    normalize_kernel: bool = True,
) -> None:
    """Get BFE for charge array and convolve the charge array with the BFE.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    a: float
        First coefficient in polynomial function.
    b: float
        Second coefficient in polynomial function.
    c: float
        Third coefficient in polynomial function.
    alpha: float
        Coefficient that defines where PTC curve starts.
    beta: float
        Coefficient that defines where the PTC curve breaks.
    normalize_kernel : bool
        Normalize kernel.
    """

    data_2d = detector.charge.array
    conv = bfe(
        data_2d=data_2d,
        full_well_capacity=detector.characteristics.full_well_capacity,
        a=a,
        b=b,
        c=c,
        alpha=alpha,
        beta=beta,
    )

    detector.charge.add_charge_array(conv)


# @numba.njit(fastmath=False)
# def apply_bfe(signal: np.ndarray, coefficients: Sequence[float]) -> np.ndarray:
#     """Get BFE for charge array and convolve the charge array with the BFE.
#
#     Parameters
#     ----------
#     signal
#     coefficients : list of float
#         Coefficient of the polynomial function.
#     """
#
#     a = coefficients[0]
#     b = coefficients[1]
#     c = coefficients[2]
#
#
#     mean = np.mean(signal)
#     sigma_array = a + b * signal + c * signal**2
#     norm_sigma = (1 / np.max(sigma_array)) * sigma_array
#     num_y, num_x = signal.shape
#     data_2d = np.ones(signal.shape)
#     new_data_2d = signal.copy()
#     for k in range(num_x):
#         for l in range(num_y):
#             # take sigma from sigma array at this pixel
#             sigma = norm_sigma[k, l]
#             size = 3
#             # gaussian_2d = np.asarray(Gaussian2DKernel(x_stddev=sigma, x_size=3))
#             kernel = np.zeros((size, size))
#             for m in range(size):
#                 for n in range(size):
#                     x = n - (size // 2)
#                     y = m - (size // 2)
#                     kernel[m, n] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
#             gaussian_2d = kernel / np.sum(kernel)
#             for i in range(1, num_x - 1):
#                 for j in range(1, num_y - 1):
#                     new_data_2d[i - 1, j - 1] += (
#                         gaussian_2d[0, 0] * data_2d[i - 1, j - 1]
#                     )
#                     new_data_2d[i, j - 1] += gaussian_2d[0, 1] * data_2d[i, j - 1]
#                     new_data_2d[i + 1, j - 1] += (
#                         gaussian_2d[0, 2] * data_2d[i + 1, j - 1]
#                     )
#                     new_data_2d[i - 1, j] += gaussian_2d[1, 0] * data_2d[i - 1, j]
#                     new_data_2d[i, j] += (
#                         gaussian_2d[1, 1] * data_2d[i, j]
#                     )  # Note: this is the blue X
#                     new_data_2d[i + 1, j] += gaussian_2d[1, 2] * data_2d[i + 1, j]
#                     new_data_2d[i - 1, j + 1] += (
#                         gaussian_2d[2, 0] * data_2d[i - 1, j + 1]
#                     )
#                     new_data_2d[i, j + 1] += gaussian_2d[2, 1] * data_2d[i, j + 1]
#                     new_data_2d[i + 1, j + 1] += (
#                         gaussian_2d[2, 2] * data_2d[i + 1, j + 1]
#                     )
#
#     new_signal = data_2d + new_data_2d
#
#     return new_signal


# def brighter_fatter(detector: Detector, coefficients: Sequence[float]) -> None:
#     # signal = detector.charge.array
#     new_signal = apply_bfe(signal=detector.charge.array, coefficients=coefficients)
#
#     detector.charge.array = new_signal

# print(df)
# i j raussuchen und dann convoluted images ineinander stacken.
# polynomial_function = np.polynomial.polynomial.Polynomial(coefficients)
# sigma_array = polynomial_function(detector.charge.array)
# list = []
# for sigma in sigma_array:
#     kernel = Gaussian2DKernel(x_stddev=sigma)
#     mean = np.mean(detector.charge.array)
#
#     array_2d = convolve_fft(
#         detector.charge.array,
#         kernel=kernel,
#         boundary="fill",
#         fill_value=mean,
#         normalize_kernel=normalize_kernel,
#     )
#     list.append(array_2d)
# print(list)
# sigma = np.max(detector.charge.array)

# detector.charge.array = apply_bfe(
#     array=detector.charge.array, sigma=sigma, normalize_kernel=normalize_kernel
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
