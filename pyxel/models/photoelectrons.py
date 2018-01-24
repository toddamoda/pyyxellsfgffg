#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" Simple model to convert photons into photo-electrons inside detector
"""

import copy
import numpy as np
import random

from pyxel.detectors.ccd import CCD


def simple_conversion(detector: CCD) -> CCD:
    """
    Generate charges from incident photons via photoelectric effect
    :param detector:
    :return:
    """
    new_detector = copy.deepcopy(detector)

    # photon_number = detector.photons.get_photon_numbers()
    # size = len(photon_number)

    # Calc the average charge numbers per pixel
    # qe and eta should be a single float number
    # charge_number = photon_number

    # detector.qe <= 1
    # detector.eta <= 1

    # if np.random.rand(size) <= detector.qe:
    #     pass    # 1 e
    # else:
    #     pass
    # if np.random.rand(size) <= detector.eta:
    #     pass    # 1 e
    # else:
    #     pass

    # Convert to int
    # charge_number = np.rint(charge_number).astype(int)

    return new_detector


def random_pos(detector):
    """
    Generate random position for photoelectric effect inside detector
    :param detector:
    :return:
    """
    pos1 = detector.vert_dimension * random.random()
    pos2 = detector.horz_dimension * random.random()
    pos3 = -1 * detector.total_thickness * random.random()
    return np.array([pos1, pos2, pos3])
