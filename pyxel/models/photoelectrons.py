#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to convert photons into photo-electrons inside detector."""

# import copy
# import numpy as np

from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_registry import registry


@registry.decorator('charge_generation', name='photoelectrons')
def simple_conversion(detector: Detector) -> Detector:
    """Generate charges from incident photons via photoelectric effect, simple statistical model.

    :param detector:
    :return new_detector:
    """
    new_detector = detector
    ch = new_detector.characteristics
    ph = new_detector.photons
    photon_number = ph.get_photon_numbers()
    size = len(photon_number)
    # Calculate the average charge numbers per pixel
    charge_number = photon_number * ch.qe * ch.eta
    # Adding new charge to Charge data frame
    new_detector.charges.add_charge(particle_type='e',
                                    particles_per_cluster=charge_number,
                                    init_energy=[0.] * size,
                                    init_ver_position=ph.get_positions_ver(),
                                    init_hor_position=ph.get_positions_hor(),
                                    init_z_position=ph.get_positions_z(),
                                    init_ver_velocity=[0.] * size,
                                    init_hor_velocity=[0.] * size,
                                    init_z_velocity=[0.] * size)
    # Removing all the photons because they have either created some photoelectrons or got lost
    ph.remove_photons()
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
