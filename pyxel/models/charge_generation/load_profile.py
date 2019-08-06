#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to load charge profiles."""
import logging
import numpy as np
from pyxel.detectors.detector import Detector
from pyxel.util import validators, checkers, config


@validators.validate
@config.argument(name='txt_file', label='file path', units='', validate=checkers.check_path)
def charge_profile(detector: Detector,
                   txt_file: str,
                   fit_profile_to_det: bool = False,
                   profile_position: list = None):
    """Load charge profile from txt file for detector, mostly for but not limited to CCDs.

    :param detector: Pyxel Detector object
    :param txt_file: file path
    :param fit_profile_to_det: bool
    :param profile_position: list
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry

    # All pixels has zero charge by default
    detector_charge = np.zeros((geo.row, geo.col))
    # Load 2d charge profile (which can be smaller or larger in dimensions than detector imaging area)
    charge_from_file = np.loadtxt(txt_file, ndmin=2)
    if fit_profile_to_det:
        # Crop 2d charge profile, so it is not larger in dimensions than detector imaging area)
        charge_from_file = charge_from_file[slice(0, geo.row), slice(0, geo.col)]
    profile_rows, profile_cols = charge_from_file.shape
    if profile_position is None:
        profile_position = [0, 0]
    detector_charge[slice(profile_position[0], profile_position[0] + profile_rows),
                    slice(profile_position[1], profile_position[1] + profile_cols)] = charge_from_file
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
