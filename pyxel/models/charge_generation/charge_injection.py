#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel charge injection functions for CCDs."""
import logging
import numpy as np
from pyxel.detectors.ccd import CCD
from pyxel.util import validators, config, checkers


@validators.validate
@config.argument(name='detector', label='', units='', validate=checkers.check_type(CCD))
def charge_blocks(detector: CCD,
                  charge_level: int,
                  block_start: int = 0,
                  block_end: int = None):
    """TBW.

    :param detector:
    :param charge_level:
    :param block_start:
    :param block_end:
    # :param columns:
    # :param profile_length:
    # :param number_of_blocks:
    # :param block_length:
    # :param pause_length:

    :return:
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    if block_end is None:
        block_end = geo.row

    # all pixels has zero charge by default
    detector_charge = np.zeros((geo.row, geo.col))
    detector_charge[slice(block_start, block_end), :] = charge_level
    charge_number = detector_charge.flatten()
    where_non_zero = np.where(charge_number > 0.)
    charge_number = charge_number[where_non_zero]
    size = charge_number.size

    init_ver_pix_position = geo.vertical_pixel_center_pos_list()[where_non_zero]
    init_hor_pix_position = geo.horizontal_pixel_center_pos_list()[where_non_zero]

    detector.charge.add_charge(particle_type='e',
                               particles_per_cluster=charge_number,
                               init_energy=[0.] * size,
                               init_ver_position=init_ver_pix_position,
                               init_hor_position=init_hor_pix_position,
                               init_z_position=[0.] * size,
                               init_ver_velocity=[0.] * size,
                               init_hor_velocity=[0.] * size,
                               init_z_velocity=[0.] * size)
