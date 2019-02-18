#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel charge collection model."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector
import numba


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_collection', name='simple_collection')
def simple_collection(detector: Detector):
    """Associate charges with the closest pixel."""
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    array = np.zeros((geo.row, geo.col))

    charge_per_pixel = detector.charges.get_values(quantity='number')
    charge_pos_ver = detector.charges.get_values(quantity='position_ver')
    charge_pos_hor = detector.charges.get_values(quantity='position_hor')

    pixel_index_ver = np.floor_divide(charge_pos_ver, geo.pixel_vert_size).astype(int)
    pixel_index_hor = np.floor_divide(charge_pos_hor, geo.pixel_horz_size).astype(int)

    detector.pixels.array = df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor)


@numba.jit(nopython=True)
def df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor):
    for i, charge_value in enumerate(charge_per_pixel):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_value
    return array
