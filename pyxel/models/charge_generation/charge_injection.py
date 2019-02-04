#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel charge injection functions for CCDs."""
import logging
import typing as t
import numpy as np
# import pyxel
from pyxel.detectors.ccd import CCD


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def charge_blocks(detector: CCD,
                  charge_level: int,
                  columns: t.List[int],
                  number_of_blocks: int = 1,
                  block_start: int = 0,
                  block_length: int = 0,
                  pause_length: int = 0):
    """TBW.

    :param detector:
    :param charge_level:
    :param columns:
    :param number_of_blocks:
    :param block_start:
    :param block_length:
    :param pause_length:

    :return:
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    injection_columns = np.array(columns, dtype=float)
    if block_length == 0:
        block_length = geo.row
    if block_start + number_of_blocks * (block_length + pause_length) > geo.row:
        raise ValueError('Too many/long charge block(s).')

    init_ver_position = np.array([])
    for i in range(number_of_blocks):
        block_pos = block_start + i * (block_length + pause_length)
        init_ver_position = np.append(init_ver_position, np.arange(block_pos, block_pos + block_length))
    init_hor_position = np.tile(injection_columns, number_of_blocks * block_length)
    init_ver_position = np.repeat(init_ver_position, injection_columns.size)
    init_ver_position *= geo.pixel_vert_size
    init_hor_position *= geo.pixel_horz_size
    size = init_ver_position.size
    init_ver_position += np.random.rand(size) * geo.pixel_vert_size     # random position within pixel
    init_hor_position += np.random.rand(size) * geo.pixel_horz_size     # random position within pixel

    detector.charges.add_charge(particle_type='e',
                                particles_per_cluster=[charge_level] * size,
                                init_energy=[0.] * size,
                                init_ver_position=init_ver_position,
                                init_hor_position=init_hor_position,
                                init_z_position=[0.] * size,
                                init_ver_velocity=[0.] * size,
                                init_hor_velocity=[0.] * size,
                                init_z_velocity=[0.] * size)
