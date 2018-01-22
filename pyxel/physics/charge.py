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
    Charged particle class defining and storing information of all electrons and holes with their properties
    like charge, position, velocity, energy
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
                                           'init_pos_ver',
                                           'init_pos_hor',
                                           'init_pos_z',
                                           'position_ver',
                                           'position_hor',
                                           'position_z',
                                           'velocity_ver',
                                           'velocity_hor',
                                           'velocity_z'])
        self.nextid = 0

    def create_charge(self,
                      particle_type='e',
                      particles_per_cluster=1,
                      initial_energy=0.0,
                      initial_position=np.array([0., 0., 0.]),
                      initial_velocity=np.array([0., 0., 0.])
                      ):
        """
        Creating new charge or group of charges (electron/hole) inside the detector stored in a pandas DataFrame
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
                      'init_pos_ver': initial_position[0],
                      'init_pos_hor': initial_position[1],
                      'init_pos_z': initial_position[2],
                      'position_ver': initial_position[0],
                      'position_hor': initial_position[1],
                      'position_z': initial_position[2],
                      'velocity_ver': initial_velocity[0],
                      'velocity_hor': initial_velocity[1],
                      'velocity_z': initial_velocity[2]}

        # new_charge_df = pd.DataFrame(new_charge, index=[self.nextid])
        new_charge_df = pd.DataFrame(new_charge, index=[0])
        self.nextid += 1

        # Adding new particle to the DataFrame
        self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True)

    def remove_charges(self, id_list='all'):
        """
        Remove list of charges from DataFrame if they are not needed, tracked anymore
        :param id_list:
        :return:
        """
        if id_list == 'all':
            self.frame.drop(self.frame.id[:], inplace=True)
        else:
            self.frame.query('id not in %s' % id_list, inplace=True)

    def get_positions(self, id_list='all'):
        """
        Get all 3 positions of a list of charges as a numpy array
        :param id_list:
        :return:
        """
        return np.stack((self.get_positions_ver(id_list),
                         self.get_positions_hor(id_list),
                         self.get_positions_z(id_list)), axis=1)

    def get_positions_ver(self, id_list='all'):
        """
        Get vertical positions of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).position_ver.values
        return array

    def get_positions_hor(self, id_list='all'):
        """
        Get horizontal positions of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).position_hor.values
        return array

    def get_positions_z(self, id_list='all'):
        """
        Get z positions (height) of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_z.values
        else:
            array = self.frame.query('id in %s' % id_list).position_z.values
        return array

    def get_velocities(self, id_list='all'):
        """
         Get all 3 velocities of a list of charges as a numpy array
         :param id_list:
         :return:
         """
        return np.stack((self.get_velocities_ver(id_list),
                         self.get_velocities_hor(id_list),
                         self.get_velocities_z(id_list)), axis=1)

    def get_velocities_ver(self, id_list='all'):
        """
        Get vertical velocities of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_ver.values
        return array

    def get_velocities_hor(self, id_list='all'):
        """
        Get horizontal velocities of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_hor.values
        return array

    def get_velocities_z(self, id_list='all'):
        """
        Get z velocities (height) of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_z.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_z.values
        return array

    def get_energies(self, id_list='all'):
        """
        Get energies of a list of charges
        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.energy.values
        else:
            array = self.frame.query('id in %s' % id_list).energy.values
        return array

    def change_positions(self, id_pos, new_positions):
        """
        Update positions of one charge
        :param id_pos:
        :param new_positions:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_ver'] = new_positions[0]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_hor'] = new_positions[1]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_z'] = new_positions[2]

    def change_velocities(self, id_vel, new_velocities):
        """
        Update velocities of one charge
        :param id_vel:
        :param new_velocities:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_ver'] = new_velocities[0]
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_hor'] = new_velocities[1]
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_z'] = new_velocities[2]

    def change_energy(self, id_en, new_energy):
        """
        Update energy of one charge
        :param id_en:
        :param new_energy:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_en], 'energy'] = new_energy
