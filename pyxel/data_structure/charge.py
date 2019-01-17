#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Charge class to generate electrons or holes inside detector."""
import pandas as pd
import numpy as np
from astropy.units import cds
from pyxel.data_structure.particle import Particle

cds.enable()


class Charge(Particle):
    """Charged particle class defining and storing information of all electrons and holes.

    Properties stored are: charge, position, velocity, energy.
    """

    def __init__(self) -> None:
        """TBW."""
        super().__init__()
        self.nextid = 0

        self.columns = ['id',        # todo do we need id or not ???
                        'charge',
                        'number',    # todo use this list
                        'init_energy', 'energy',
                        'init_pos_ver', 'init_pos_hor', 'init_pos_z',
                        'position_ver', 'position_hor', 'position_z',
                        'velocity_ver', 'velocity_hor', 'velocity_z',
                        'pixel_ver', 'pixel_hor']           # todo do we need these columns really ???????

        self.EMPTY_FRAME = pd.DataFrame(columns=self.columns,
                                        dtype=np.float)         # todo is it ok to define float for all column????

        self.frame = self.EMPTY_FRAME.copy()

        # self.frame = pd.DataFrame(columns=['id',
        #                                    'charge',
        #                                    'number',
        #                                    'init_energy',
        #                                    'energy',
        #                                    'init_pos_ver',
        #                                    'init_pos_hor',
        #                                    'init_pos_z',
        #                                    'position_ver',
        #                                    'position_hor',
        #                                    'position_z',
        #                                    'velocity_ver',
        #                                    'velocity_hor',
        #                                    'velocity_z',
        #                                    'pixel_ver',
        #                                    'pixel_hor'])

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

        # check_position(self.detector, init_ver_position, init_hor_position, init_z_position)      # TODO
        # check_energy(init_energy)         # TODO
        # Check if particle number is integer:
        # check_type(particles_per_cluster)      # TODO

        if particle_type == 'e':
            charge = [-1] * elements            # * cds.e
        elif particle_type == 'h':
            charge = [+1] * elements            # * cds.e
        else:
            raise ValueError('Given charged particle type can not be simulated')

        # if all(init_ver_velocity) == 0 and all(init_hor_velocity) == 0 and all(init_z_velocity) == 0:
        #     random_direction(1.0)

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
        # try:
        #     self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True, sort=False)
        # except TypeError:
        #     self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True)
        # #

        self.frame = self.frame.append(new_charge_df, sort=False)
