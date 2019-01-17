#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to convert photons into photo-electrons inside detector."""
import logging
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_generation', name='photoelectrons')
def simple_conversion(detector: Detector):
    """Generate charges from incident photons via photoelectric effect, simple statistical model.

    :param detector: Pyxel Detector object
    """
    logging.info('')
    ch = detector.characteristics
    ph = detector.photons
    photon_number = ph.get_values(quantity='number')
    size = len(photon_number)
    # Calculate the average charge numbers per pixel
    charge_number = photon_number * ch.qe * ch.eta
    # Adding new charge to Charge data frame
    detector.charges.add_charge(particle_type='e',
                                particles_per_cluster=charge_number,
                                init_energy=[0.] * size,
                                init_ver_position=ph.get_values(quantity='position_ver'),
                                init_hor_position=ph.get_values(quantity='position_hor'),
                                init_z_position=ph.get_values(quantity='position_z'),
                                init_ver_velocity=[0.] * size,
                                init_hor_velocity=[0.] * size,
                                init_z_velocity=[0.] * size)
    # Removing all the photons because they have either created some photoelectrons or got lost
    ph.remove()


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_generation', name='monte_carlo_photoelectrons')
def monte_carlo_conversion(detector: Detector):
    """Generate charges from incident photons via photoelectric effect, more exact, stochastic (Monte Carlo) model.

    :param detector: Pyxel Detector object
    """
    logging.info('')

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


def random_pos(detector: Detector):
    """Generate random position for photoelectric effect inside detector.

    :param detector: Pyxel Detector object
    """
    # pos1 = detector.vert_dimension * np.random.random()
    # pos2 = detector.horz_dimension * np.random.random()

    # size = 0
    # pos3 = -1 * detector.total_thickness * np.random.rand(size)
    # return pos3
    raise NotImplementedError
