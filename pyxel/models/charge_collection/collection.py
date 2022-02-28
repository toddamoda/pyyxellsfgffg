#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge collection model."""
import typing as t

import numba
import numpy as np
import pandas

from pyxel.detectors import Detector


@numba.jit(nopython=True)
def df_to_array(
    array: np.ndarray,
    charge_per_pixel: list,
    pixel_index_ver: list,
    pixel_index_hor: list,
) -> np.ndarray:
    """Assign charge in dataframe to nearest pixel.

    Parameters
    ----------
    array: ndarray
    charge_per_pixel: list
    pixel_index_ver: list
    pixel_index_hor:list

    Returns
    -------
    ndarray
    """
    for i, charge_value in enumerate(charge_per_pixel):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_value
    return array


def simple_collection(detector: Detector) -> None:
    """Associate charge with the closest pixel.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    """
    if not detector.charge.frame_empty():

        shape = (detector.geometry.row, detector.geometry.col)
        pixel_vert_size = detector.geometry.pixel_vert_size
        pixel_horz_size = detector.geometry.pixel_horz_size

        array = np.zeros(shape)

        charge_per_pixel = detector.charge.get_frame_values(quantity="number")
        charge_pos_ver = detector.charge.get_frame_values(quantity="position_ver")
        charge_pos_hor = detector.charge.get_frame_values(quantity="position_hor")

        pixel_index_ver = np.floor_divide(charge_pos_ver, pixel_vert_size).astype(int)
        pixel_index_hor = np.floor_divide(charge_pos_hor, pixel_horz_size).astype(int)

        final_array = df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor)

    else:
        final_array = detector.charge.array

    detector.pixel.array += final_array
