#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel full well models."""
import logging
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_collection', name='full_well')
def simple_full_well(detector: Detector):
    """Limiting the amount of charges in pixels due to full well capacity."""
    logger = logging.getLogger('pyxel')
    logger.info('')
    fwc = detector.characteristics.fwc
    if fwc is None:
        raise ValueError('Full Well Capacity is not defined')
    charge_array = detector.pixels.array
    charge_array[charge_array > fwc] = fwc
    detector.pixels.array = charge_array
