#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! CCD full well models."""
# import copy

from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_registry import registry


@registry.decorator('charge_collection', name='full_well')
def simple_pixel_full_well(detector: Detector) -> Detector:
    """Simply removing charges from pixels due to full well.

    :return:
    """
    new_detector = detector

    fwc = new_detector.characteristics.fwc
    if fwc is None:
        raise ValueError('Full Well Capacity is not defined')

    charge_array = new_detector.pixels.array
    mask = charge_array > fwc
    charge_array[mask] = fwc

    return new_detector


# def mc_full_well(detector: Detector) -> Detector:
#     """
#     Moving charges to random neighbour pixels due to full well which depends on pixel location
#     :return:
#     """
#
#
#     return new_detector
