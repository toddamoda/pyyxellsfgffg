#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! CCD full well models
"""
import copy
# import numpy as np

from pyxel.detectors.ccd import CCD


def simple_full_well(detector: CCD) -> CCD:
    """
    Removing charges from pixels due to full well
    :return:
    """

    new_detector = copy.deepcopy(detector)

    # detector.charges
    # detector.pixels

    # full = .frame['charge'] > self.detector.fwc

    # self.frame.at[self.frame.index[self.frame['charge'] > self.detector.fwc],
    #               'charge'] = self.detector.fwc

    return new_detector
