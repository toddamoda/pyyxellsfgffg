#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   Written by B. Serra
#   --------------------------------------------------------------------------
"""Pyxel persistence model."""
import logging
from pyxel.detectors.cmos import CMOS
# import numpy as np


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def simple_persistence(detector: CMOS,
                       trap_timeconstant: list,
                       trap_density: list):
    """Trapping/detrapping charges."""
    logger = logging.getLogger('pyxel')
    logger.info('')

    # TODO: NOT FINISHED AND NOT WORKING YET

    # if detector.time == detector.start_time:
    #     trapped_charge = np.zeros((len(trap_timeconstant), detector.geometry.row, detector.geometry.col))
    # else:
    #     trapped_charge = detector.material.trapped_charge
    #
    # trap_density_array = np.ones((len(trap_timeconstant), detector.geometry.row, detector.geometry.col))
    #
    # for idx, tc in enumerate(trap_timeconstant):
    #     # trapped_charge[idx] += (detector.time / tc) *
    #     # (detector.pixels.array * trap_density[idx] - trapped_charge[idx])
    #
    #     trap_density_array[idx] *= trap_density[idx]
    #     max_charge_could_be_trapped = np.clip(detector.pixels.array, 0, trap_density_array[idx])
    #     trapped_charge[idx] += (detector.time / tc) * (max_charge_could_be_trapped - trapped_charge[idx])
    #
    # detector.material.trapped_charge = trapped_charge
    #
    # # detector.pixels.array = trapped_charge[0]    # TODO
    #
    # # for i in range(len(trap_timeconstant)):
    # #     detector.pixels.array -= trapped_charge[i, :, :]
    #
    #
    # pass
