
# import math
# import random
import numpy as np
# import matplotlib.pyplot as plt

from astropy import units as u
from astropy.units import cds
cds.enable()

class Charge:
    """
    Charged particle class defining an electron/hole with its properties like charge, mass, position, velocity(?)
    """

    def __init__(self,
                 detector=None,
                 particle_type='e',
                 starting_pos_ver=0.0, starting_pos_hor=0.0, starting_pos_z=0.0,
                 particles_per_cluster=1,
                 initial_energy=0.0
                 ):
        '''
        Creation of a charged particle (electron or hole) with its parameters

        :param detector: CCD in which the charges are being tracked (collected, transferd, measured)
        :param particle_type:
        :param starting_pos_ver:
        :param starting_pos_hor:
        :param starting_pos_z:
        '''

        self.detector = detector

        starting_position_vertical = None
        starting_position_horizontal = None
        starting_position_z = None
        if isinstance(starting_pos_ver, int) or isinstance(starting_pos_ver, float):
            if 0.0 <= starting_pos_ver <= self.detector.ver_dimension:
                starting_position_vertical = starting_pos_ver
            else:
                raise ValueError('Vertical position of charge is outside the detector')
        else:
            raise ValueError('Vertical position of charge is not a number')

        if isinstance(starting_pos_hor, int) or isinstance(starting_pos_hor, float):
            if 0.0 <= starting_pos_hor <= self.detector.hor_dimension:
                starting_position_horizontal = starting_pos_hor
            else:
                raise ValueError('Horizontal position of charge is outside the detector')
        else:
            raise ValueError('Horizontal position of charge is not a number')

        if isinstance(starting_pos_z, int) or isinstance(starting_pos_z, float):
            if -1 * self.detector.total_thickness <= starting_pos_z <= 0.0:
                starting_position_z = starting_pos_z
            else:
                raise ValueError('Z position of charge is outside the detector')
        else:
            raise ValueError('Z position of charge is not a number')

        self.initial_position = np.array([starting_position_vertical,
                                          starting_position_horizontal,
                                          starting_position_z])
        self.position = np.copy(self.initial_position)
        self.trajectory = np.copy(self.initial_position)

        # self.pixel = np.array([0, 0])
        # which pixel contains this charge at the end of charge collection phase
        # and after charge transfer

        # Velocity - Maybe later we will need this as well:
        # alpha = 2 * math.pi * random.random()
        # beta = 2. * math.pi * random.random()
        # self.v_z = v_abs * -1 * math.sin(alpha) #?????
        # self.v_ver = v_abs * math.cos(alpha) * math.cos(beta)
        # self.v_hor = v_abs * math.cos(alpha) * math.sin(beta)

        # Energy - Maybe later we will need this as well:
        if isinstance(initial_energy, int) or isinstance(initial_energy, float):
            self.energy = initial_energy * u.eV
        else:
            raise ValueError('Given charge (electron/hole) energy could not be read')

        self.type = particle_type
        if self.type == 'e':
            self.charge = -1 * cds.e
        elif self.type == 'h':
            self.charge = +1 * cds.e
        else:
            raise ValueError('Given charged particle type can not be simulated')

        self.number = particles_per_cluster * u.electron
        # number of particles per cluster (it is called cluster if there are more than 1 charge)

        self.mass = 1.0 * cds.me

    def _plot_trajectory_xy_(self):
        plt.figure()
        # self.trajectory[:, 0] - VERTICAL COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(self.trajectory[:, 1], self.trajectory[:, 0], '.')
        plt.xlabel('horizontal ($\mu$m)')
        plt.ylabel('vertical ($\mu$m)')
        plt.title('charge (e/h) trajectory in detector')
        plt.axis([0, self.detector.hor_dimension, 0, self.detector.ver_dimension])
        plt.grid(True)
        plt.draw()

    def _plot_trajectory_xz_(self):
        plt.figure()
        # self.trajectory[:, 2] - Z COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(self.trajectory[:, 1], self.trajectory[:, 2], '.')
        plt.xlabel('horizontal ($\mu$m)')
        plt.ylabel('z ($\mu$m)')
        plt.title('charge (e/h) trajectory in detector')
        plt.axis([0, self.detector.hor_dimension, -1*self.detector.total_thickness, 0])
        plt.grid(True)
        plt.draw()
