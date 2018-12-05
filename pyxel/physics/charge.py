#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Charge class to generate electrons or holes inside detector."""
import math
import numpy as np
import pandas as pd
# from astropy import units as u
from astropy.units import cds
# from pyxel.util.util import round_convert_to_int    # , convert_to_int

cds.enable()


def check_energy(initial_energy):
    """Check energy of the particle if it is a float or int.

    :param initial_energy:
    :return:
    """
    if isinstance(initial_energy, int) or isinstance(initial_energy, float):
        pass
    else:
        raise ValueError('Given charge (electron/hole) energy could not be read')


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
                    raise ValueError('Z position of charge is outside the detector')
            else:
                raise ValueError('Horizontal position of charge is outside the detector')
        else:
            raise ValueError('Vertical position of charge is outside the detector')
    else:
        raise ValueError('Position of charge is not a numpy array (int or float)')


def random_direction(v_abs=1.0):    # TODO check random angles and direction
    """Generate random direction for charge.

    :param v_abs:
    :return:
    """
    alpha = 2 * math.pi * np.random.random()
    beta = 2. * math.pi * np.random.random()
    v_z = v_abs * math.sin(alpha)
    v_ver = v_abs * math.cos(alpha) * math.cos(beta)
    v_hor = v_abs * math.cos(alpha) * math.sin(beta)
    return np.array([v_ver, v_hor, v_z])


class Charge:
    """Charged particle class defining and storing information of all electrons and holes.

    Properties stored are: charge, position, velocity, energy.
    """

    def __init__(self,
                 detector=None):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.nextid = 0
        self.frame = pd.DataFrame(columns=['id',
                                           'charge',
                                           'number',
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
                                           'velocity_z',
                                           'pixel_ver',
                                           'pixel_hor'])

    def add_charge(self,
                   particle_type,
                   particles_per_cluster,
                   init_energy,
                   init_ver_position,
                   init_hor_position,
                   init_z_position,
                   init_ver_velocity,
                   init_hor_velocity,
                   init_z_velocity):
        """Create new charge or group of charges inside the detector stored in a pandas DataFrame.

        :param particle_type:
        :param particles_per_cluster:
        :param init_energy:
        :param init_ver_position:
        :param init_hor_position:
        :param init_z_position:
        :param init_ver_velocity:
        :param init_hor_velocity:
        :param init_z_velocity:
        :return:
        """
        if len(particles_per_cluster) == len(init_energy) == len(init_ver_position) == len(init_ver_velocity):
            elements = len(init_energy)
        else:
            raise ValueError('List arguments have different lengths')

        # check_position(self.detector, init_ver_position, init_hor_position, init_z_position)
        # check_energy(init_energy)

        if particle_type == 'e':
            charge = [-1] * elements            # * cds.e
        elif particle_type == 'h':
            charge = [+1] * elements            # * cds.e
        else:
            raise ValueError('Given charged particle type can not be simulated')

        # if all(init_ver_velocity) == 0 and all(init_hor_velocity) == 0 and all(init_z_velocity) == 0:
        #     random_direction(1.0)

        # Rounding and converting to integer
        # charge = round_convert_to_int(particles_per_cluster)      # TODO

        # dict
        new_charge = {'id': range(self.nextid, self.nextid + elements),
                      'charge': charge,
                      'number': particles_per_cluster,
                      'init_energy': init_energy,
                      'energy': init_energy,
                      'init_pos_ver': init_ver_position,
                      'init_pos_hor': init_hor_position,
                      'init_pos_z': init_z_position,
                      'position_ver': init_ver_position,
                      'position_hor': init_hor_position,
                      'position_z': init_z_position,
                      'velocity_ver': init_ver_velocity,
                      'velocity_hor': init_hor_velocity,
                      'velocity_z': init_z_velocity}

        new_charge_df = pd.DataFrame(new_charge)
        self.nextid = self.nextid + elements

        # Adding new particles to the DataFrame
        try:
            self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True, sort=False)
        except TypeError:
            self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True)

    def remove_charges(self, id_list='all'):
        """Remove list of charges from DataFrame if they are not needed, tracked anymore.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            self.frame.drop(self.frame.id[:], inplace=True)
        else:
            self.frame.query('id not in %s' % id_list, inplace=True)

    def get_numbers(self, id_list='all'):
        """Get number of charges per DataFrame row.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.number.values
        else:
            array = self.frame.query('id in %s' % id_list).number.values
        return array

    def get_positions(self, id_list='all'):
        """Get all 3 positions of a list of charges as a numpy array.

        :param id_list:
        :return:
        """
        return np.stack((self.get_positions_ver(id_list),
                         self.get_positions_hor(id_list),
                         self.get_positions_z(id_list)), axis=1)

    def get_positions_ver(self, id_list='all'):
        """Get vertical positions of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).position_ver.values
        return array

    def get_positions_hor(self, id_list='all'):
        """Get horizontal positions of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).position_hor.values
        return array

    def get_positions_z(self, id_list='all'):
        """Get z positions (height) of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_z.values
        else:
            array = self.frame.query('id in %s' % id_list).position_z.values
        return array

    def get_velocities(self, id_list='all'):
        """Get all 3 velocities of a list of charges as a numpy array.

        :param id_list:
        :return:
        """
        return np.stack((self.get_velocities_ver(id_list),
                         self.get_velocities_hor(id_list),
                         self.get_velocities_z(id_list)), axis=1)

    def get_velocities_ver(self, id_list='all'):
        """Get vertical velocities of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_ver.values
        return array

    def get_velocities_hor(self, id_list='all'):
        """Get horizontal velocities of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_hor.values
        return array

    def get_velocities_z(self, id_list='all'):
        """Get z velocities (height) of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_z.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_z.values
        return array

    def get_energies(self, id_list='all'):
        """Get energies of a list of charges.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.energy.values
        else:
            array = self.frame.query('id in %s' % id_list).energy.values
        return array

    def change_all_number(self, new_number_list):
        """Update number of charges in each row.

        :param new_number_list:
        :return:
        """
        new_df = pd.DataFrame({'number': new_number_list})
        self.frame.update(new_df)
        # TODO: update all rows with given ids in list (id_list can be a 2nd optional arg)
        # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.update.html

    def change_positions(self, id_pos, new_positions):
        """Update positions of one charge.

        :param id_pos:
        :param new_positions:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_ver'] = new_positions[0]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_hor'] = new_positions[1]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_z'] = new_positions[2]

    def change_velocities(self, id_vel, new_velocities):
        """Update velocities of one charge.

        :param id_vel:
        :param new_velocities:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_ver'] = new_velocities[0]
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_hor'] = new_velocities[1]
        self.frame.at[self.frame.index[self.frame['id'] == id_vel], 'velocity_z'] = new_velocities[2]

    def change_energy(self, id_en, new_energy):
        """Update energy of one charge.

        :param id_en:
        :param new_energy:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_en], 'energy'] = new_energy
