#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel full well models."""
import logging
import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
@pyxel.register(group='charge_collection', name='full_well')
def simple_pixel_full_well(detector: Detector) -> Detector:
    """Simply removing charges from pixels due to full well.

    :return:
    """
    logging.info('')
    fwc = detector.characteristics.fwc
    if fwc is None:
        raise ValueError('Full Well Capacity is not defined')

    charge_array = detector.pixels.array
    mask = charge_array > fwc
    charge_array[mask] = fwc

    return detector


# def mc_full_well(detector: Detector) -> Detector:
#     """
#     Moving charges to random neighbour pixels due to full well which depends on pixel location
#     :return:
#     """
#
#
#     return detector
