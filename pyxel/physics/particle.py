#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel general particle class to track particles like photons and electrons, holes."""
# import math
import numpy as np
import pandas as pd
# from astropy import units as u
# from astropy.units import cds

# cds.enable()


class Particle:
    """Class defining and storing information of all particles with their position, velocity, energy."""

    def __init__(self, detector=None):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.nextid = 0
        self.frame = pd.DataFrame(columns=['id',
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
                                           'velocity_z'])

    # def get_photon_numbers(self, id_list='all'):
    #     """Get number of photons per DataFrame row.
    #
    #     :param id_list:
    #     :return:
    #     """
    #     if id_list == 'all':
    #         array = self.frame.number.values
    #     else:
    #         array = self.frame.query('id in %s' % id_list).number.values
    #     return array
    #
    # def remove_photons(self, id_list='all'):
    #     """Remove list of photons from DataFrame if they are not needed, tracked anymore.
    #
    #     :param id_list:
    #     :return:
    #     """
    #     if id_list == 'all':
    #         self.frame.drop(self.frame.id[:], inplace=True)
    #     else:
    #         self.frame.query('id not in %s' % id_list, inplace=True)

    def get_positions(self, id_list='all'):
        """Get all 3 positions of a list of photons as a numpy array.

        :param id_list:
        :return:
        """
        return np.stack((self.get_positions_ver(id_list),
                         self.get_positions_hor(id_list),
                         self.get_positions_z(id_list)), axis=1)

    def get_positions_ver(self, id_list='all'):
        """Get vertical positions of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).position_ver.values
        return array

    def get_positions_hor(self, id_list='all'):
        """Get horizontal positions of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).position_hor.values
        return array

    def get_positions_z(self, id_list='all'):
        """Get z positions (height) of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.position_z.values
        else:
            array = self.frame.query('id in %s' % id_list).position_z.values
        return array

    def get_velocities(self, id_list='all'):
        """Get all 3 velocities of a list of photons as a numpy array.

        :param id_list:
        :return:
        """
        return np.stack((self.get_velocities_ver(id_list),
                         self.get_velocities_hor(id_list),
                         self.get_velocities_z(id_list)), axis=1)

    def get_velocities_ver(self, id_list='all'):
        """Get vertical velocities of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_ver.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_ver.values
        return array

    def get_velocities_hor(self, id_list='all'):
        """Get horizontal velocities of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_hor.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_hor.values
        return array

    def get_velocities_z(self, id_list='all'):
        """Get z velocities (height) of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.velocity_z.values
        else:
            array = self.frame.query('id in %s' % id_list).velocity_z.values
        return array

    def get_energies(self, id_list='all'):
        """Get energies of a list of photons.

        :param id_list:
        :return:
        """
        if id_list == 'all':
            array = self.frame.energy.values
        else:
            array = self.frame.query('id in %s' % id_list).energy.values
        return array

    def change_position(self, id_pos, new_positions):
        """Update positions of one charge.

        :param id_pos:
        :param new_positions:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_ver'] = new_positions[0]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_hor'] = new_positions[1]
        self.frame.at[self.frame.index[self.frame['id'] == id_pos], 'position_z'] = new_positions[2]

    def change_velocity(self, id_vel, new_velocities):
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

    def change_all_number(self, new_number_list):
        """Update number of photons in each row.

        :param new_number_list:
        :return:
        """
        new_df = pd.DataFrame({'number': new_number_list})
        self.frame.update(new_df)
        # TODO: update all rows with given ids in list (id_list can be a 2nd optional arg)
        # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.update.html

    def change_number(self, id_num, new_number):
        """Update number of photons in one row.

        :param id_num:
        :param new_number:
        :return:
        """
        self.frame.at[self.frame.index[self.frame['id'] == id_num], 'number'] = new_number
