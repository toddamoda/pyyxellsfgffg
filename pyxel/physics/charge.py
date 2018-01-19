#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! Charge class to generate electrons or holes inside detector
"""
import numpy as np

from astropy import units as u
from astropy.units import cds
import pandas as pd

cds.enable()


def check_energy(initial_energy):
    """
    Checking energy of the particle if it is a float or int
    :param initial_energy:
    :return:
    """
    if isinstance(initial_energy, int) or isinstance(initial_energy, float):
        pass
    else:
        raise ValueError('Given charge (electron/hole) energy could not be read')


def check_position(detector, initial_position):
    """
    Checking position of the particle if it is a numpy array and inside the detector
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
                    raise ValueError('Z position of charge is outside the detector')
            else:
                raise ValueError('Horizontal position of charge is outside the detector')
        else:
            raise ValueError('Vertical position of charge is outside the detector')
    else:
        raise ValueError('Position of charge is not a numpy array (int or float)')


def random_direction(v_abs):
    """
    Generating random direction for charge
    Not used yet.
    :param v_abs:
    :return:
    """
    # alpha = 2 * math.pi * random.random()
    # beta = 2. * math.pi * random.random()
    # v_z = v_abs * -1 * math.sin(alpha)
    # v_ver = v_abs * math.cos(alpha) * math.cos(beta)
    # v_hor = v_abs * math.cos(alpha) * math.sin(beta)
    # vel_array = np.array([0., 0., 0.])
    # return vel_array
    pass


class Charge:
    """
    Charged particle class defining an electron/hole with its properties like charge, position, velocity
    """

    def __init__(self,
                 detector=None,
                 ):

        self.detector = detector

        self.frame = pd.DataFrame(columns=['id',
                                           'number',
                                           'charge',
                                           'init_energy',
                                           'energy',
                                           'init pos ver',
                                           'init pos hor',
                                           'init pos z',
                                           'position ver',
                                           'position hor',
                                           'position z',
                                           'velocity ver',
                                           'velocity hor',
                                           'velocity z'])
        self.nextid = 0

    def create_charge(self,
                      particle_type='e',
                      particles_per_cluster=1,
                      initial_energy=0.0,
                      initial_position=np.array([0., 0., 0.]),
                      initial_velocity=np.array([0., 0., 0.])
                      ):
        """
        Creating new charge (electron or hole) inside the detector
        :param particle_type:
        :param particles_per_cluster:
        :param initial_energy:
        :param initial_position:
        :param initial_velocity:
        :return:
        """

        check_position(self.detector, initial_position)
        check_energy(initial_energy)

        if particle_type == 'e':
            charge = -1 * cds.e
            number = +1 * particles_per_cluster * u.electron
        elif particle_type == 'h':
            charge = +1 * cds.e
            number = -1 * particles_per_cluster * u.electron
        else:
            raise ValueError('Given charged particle type can not be simulated')

        # Energy - Maybe later we will need this as well:
        energy = initial_energy * u.eV

        # dict
        new_charge = {'id': self.nextid,
                      'number': number,
                      'charge': charge,
                      'init_energy': energy,
                      'energy': energy,
                      'init pos ver': initial_position[0],
                      'init pos hor': initial_position[1],
                      'init pos z': initial_position[2],
                      'position ver': initial_position[0],
                      'position hor': initial_position[1],
                      'position z': initial_position[2],
                      'velocity ver': initial_velocity[0],
                      'velocity hor': initial_velocity[1],
                      'velocity z': initial_velocity[2]}

        # new_charge_df = pd.DataFrame(new_charge, index=[self.nextid])
        new_charge_df = pd.DataFrame(new_charge, index=[0])
        self.nextid += 1

        # Adding new particle to the DataFrame
        self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True)

    def remove_charges(self, ids_to_delete):

        if ids_to_delete == 'all':
            self.frame.drop(self.frame.id[:], inplace=True)
        else:
            self.frame.query('id not in %s' % ids_to_delete, inplace=True)

    def move_charges(self, id):  # TODO update a position in df
        # user should choose if want to update only one or more or all positions
        pass

    def change_velocities(self, id):  # TODO update a velocity in df
        pass

    def change_energies(self, id):  # TODO update an energy in df
        pass

    # def collide(self, id):  # TODO ???
    #     pass
