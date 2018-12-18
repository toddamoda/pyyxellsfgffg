#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel charge collection model."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_collection', name='simple_collection')
def simple_collection(detector: Detector) -> Detector:
    """Simply associate charges with a pixel.

    :return:
    """
    logging.info('')
    geo = detector.geometry
    array = np.zeros((geo.row, geo.col), int)

    charge_per_pixel = detector.charges.get_numbers()
    charge_pos_ver = detector.charges.get_positions_ver()
    charge_pos_hor = detector.charges.get_positions_hor()

    pixel_index_ver = np.floor_divide(charge_pos_ver, geo.pixel_vert_size).astype(int)
    pixel_index_hor = np.floor_divide(charge_pos_hor, geo.pixel_horz_size).astype(int)

    for i in range(len(charge_per_pixel)):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_per_pixel[i]

    detector.pixels.array = array

    return detector
