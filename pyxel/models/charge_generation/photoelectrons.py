#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to convert photons into photo-electrons inside detector."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.detector import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_generation', name='photoelectrons')
def simple_conversion(detector: Detector):
    """Generate charges from incident photons via photoelectric effect, simple statistical model.

    :param detector: Pyxel Detector object
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.geometry
    ch = detector.characteristics
    ph = detector.photons

    init_ver_position = np.arange(0.0, geo.row, 1.0) * geo.pixel_vert_size
    init_hor_position = np.arange(0.0, geo.col, 1.0) * geo.pixel_horz_size
    init_ver_position = np.repeat(init_ver_position, geo.col)
    init_hor_position = np.tile(init_hor_position, geo.row)

    charge_number = ph.array.flatten() * ch.qe * ch.eta         # the average charge numbers per pixel
    where_non_zero = np.where(charge_number > 0.)
    charge_number = charge_number[where_non_zero]
    init_ver_position = init_ver_position[where_non_zero]
    init_hor_position = init_hor_position[where_non_zero]
    size = charge_number.size
    init_ver_position += np.random.rand(size) * geo.pixel_vert_size
    init_hor_position += np.random.rand(size) * geo.pixel_horz_size

    detector.charges.add_charge(particle_type='e',
                                particles_per_cluster=charge_number,
                                init_energy=[0.] * size,
                                init_ver_position=init_ver_position,
                                init_hor_position=init_hor_position,
                                init_z_position=[0.] * size,
                                init_ver_velocity=[0.] * size,
                                init_hor_velocity=[0.] * size,
                                init_z_velocity=[0.] * size)


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_generation', name='monte_carlo_photoelectrons')
def monte_carlo_conversion(detector: Detector):
    """Generate charges from incident photons via photoelectric effect, more exact, stochastic (Monte Carlo) model.

    :param detector: Pyxel Detector object
    """
    logger = logging.getLogger('pyxel')
    logger.info('')

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
