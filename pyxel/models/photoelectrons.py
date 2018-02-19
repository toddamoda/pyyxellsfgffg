#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to convert photons into photo-electrons inside detector."""

# import copy
# import numpy as np

from pyxel.detectors.detector import Detector


def simple_conversion(detector: Detector) -> Detector:
    """Generate charges from incident photons via photoelectric effect, simple statistical model.

    :param detector:
    :return:
    """
    # new_detector = copy.deepcopy(detector)
    new_detector = detector

    photon_number = detector.photons.get_photon_numbers()
    size = len(photon_number)

    # Calc the average charge numbers per pixel
    # qe and eta should be a single float number OR list
    charge_number = photon_number * new_detector.characteristics.qe * new_detector.characteristics.eta

    # converting to int, TODO: do proper rounding or floor -> numpy object problem
    charge_number = charge_number.astype(int)

    new_detector.charges.add_charge('e',
                                    charge_number,
                                    [0.] * size,
                                    detector.photons.get_positions_ver(),
                                    detector.photons.get_positions_hor(),
                                    detector.photons.get_positions_z(),
                                    [0.] * size,
                                    [0.] * size,
                                    [0.] * size)

    # TODO remove photons!

    return new_detector


def monte_carlo_conversion(detector: Detector) -> Detector:
    """Generate charges from incident photons via photoelectric effect, more exact, stochastic (Monte Carlo) model.

    :param detector:
    :return:
    """
    # new_detector = copy.deepcopy(detector)
    new_detector = detector

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
    # TODO: random number for QE
    # TODO: random number for eta
    # TODO: energy threshold

    return new_detector


def random_pos(detector: Detector) -> Detector:
    """Generate random position for photoelectric effect inside detector.

    :param detector:
    :return:
    """
    # pos1 = detector.vert_dimension * random.random()
    # pos2 = detector.horz_dimension * random.random()

    # size = 0
    # pos3 = -1 * detector.total_thickness * np.random.rand(size)
    # return pos3
    raise NotImplementedError
