"""Pyxel charge collection model."""
import logging
import numpy as np
from pyxel.detectors.detector import Detector
import numba


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def simple_collection(detector: Detector):
    """Associate charge with the closest pixel."""
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    array = np.zeros((geo.row, geo.col))

    charge_per_pixel = detector.charge.get_values(quantity='number')
    charge_pos_ver = detector.charge.get_values(quantity='position_ver')
    charge_pos_hor = detector.charge.get_values(quantity='position_hor')

    pixel_index_ver = np.floor_divide(charge_pos_ver, geo.pixel_vert_size).astype(int)
    pixel_index_hor = np.floor_divide(charge_pos_hor, geo.pixel_horz_size).astype(int)

    detector.pixel.array = df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor)


@numba.jit(nopython=True)
def df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor):
    """TBW."""
    for i, charge_value in enumerate(charge_per_pixel):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_value
    return array
