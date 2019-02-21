#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   Written by B. Serra
#   --------------------------------------------------------------------------
"""Pyxel persitence model."""
import logging
# import pyxel
from pyxel.detectors.detector import Detector
import numpy as np


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_collection', name='full_well')
def simple_persistence(detector: Detector,
                       trap_timeconstant: list,
                       trap_density: list):
    """Trapping/detrapping charges."""
    logger = logging.getLogger('pyxel')
    logger.info('')
    charge_array = detector.pixels.array
    # trapped_charge = np.load('outputs/trappedcharges.npy')
    trapped_charge = np.zeros((len(trap_timeconstant), detector.geometry.row, detector.geometry.col))
    for idx, tc in enumerate(trap_timeconstant):
        trapped_charge[idx] = trapped_charge[idx] + \
                              (detector.time/tc) * (charge_array * trap_density[idx]-trapped_charge[idx])

    np.save('outputs/trappedcharges.npy', trapped_charge)
