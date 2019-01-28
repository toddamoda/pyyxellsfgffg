#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel util functions for Particle classes."""
import math
import numpy as np


def check_energy(initial_energy):
    """Check energy of the particle if it is a float or int.

    :param initial_energy:
    :return:
    """
    if isinstance(initial_energy, int) or isinstance(initial_energy, float):
        pass
    else:
        raise ValueError('Given particle energy could not be read')


def check_position(detector, initial_position):
    """Check position of the particle if it is a numpy array and inside the detector.

    :param detector:
    :param initial_position:
    :return:
    """
    if isinstance(initial_position, np.ndarray):
        if 0.0 <= initial_position[0] <= detector.vert_dimension:
            if 0.0 <= initial_position[1] <= detector.horz_dimension:
                if -1 * detector.total_thickness <= initial_position[2] <= 0.0:
                    pass
                else:
                    raise ValueError('Z position of particle is outside the detector')
            else:
                raise ValueError('Horizontal position of particle is outside the detector')
        else:
            raise ValueError('Vertical position of particle is outside the detector')
    else:
        raise ValueError('Position of particle is not a numpy array (int or float)')


def random_direction(v_abs=1.0):    # TODO check random angles and direction
    """Generate random direction for a photon.

    :param v_abs:
    :return:
    """
    alpha = 2 * math.pi * np.random.random()
    beta = 2. * math.pi * np.random.random()
    v_z = v_abs * math.sin(alpha)
    v_ver = v_abs * math.cos(alpha) * math.cos(beta)
    v_hor = v_abs * math.cos(alpha) * math.sin(beta)
    return np.array([v_ver, v_hor, v_z])
