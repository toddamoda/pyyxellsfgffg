import numpy as np

from astropy import units as u
from astropy.units import cds
import pandas as pd

cds.enable()


class Charge:
    """
    Charged particle class defining an electron/hole with its properties like charge, mass, position, velocity(?)
    """

    def __init__(self,
                 detector=None,
                 ):

        self.detector = detector

        self.frame = pd.DataFrame(columns=['number',
                                           'initial energy',
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

    def create_charge(self,
                      particle_type='e',
                      particles_per_cluster=1,
                      initial_energy=0.0,
                      initial_position=np.array([0., 0., 0.]),
                      initial_velocity=np.array([0., 0., 0.])
                      ):

        if isinstance(initial_position, np.ndarray):
            if 0.0 <= initial_position[0] <= self.detector.vert_dimension:
                if 0.0 <= initial_position[1] <= self.detector.horz_dimension:
                    if -1 * self.detector.total_thickness <= initial_position[2] <= 0.0:
                        pass
                    else:
                        raise ValueError
                else:
                    raise ValueError
            else:
                raise ValueError
        else:
            raise ValueError

        # if isinstance(initial_position[0], int) or isinstance(initial_position[0], float):
        #     if 0.0 <= initial_position[0] <= self.detector.vert_dimension:
        #         initial_position_vertical = initial_position[0]
        #     else:
        #         raise ValueError('Vertical position of charge is outside the detector')
        # else:
        #     raise ValueError('Vertical position of charge is not a number')
        #
        # if isinstance(initial_position[1], int) or isinstance(initial_position[1], float):
        #     if 0.0 <= initial_position[1] <= self.detector.horz_dimension:
        #         initial_position_horizontal = initial_position[1]
        #     else:
        #         raise ValueError('Horizontal position of charge is outside the detector')
        # else:
        #     raise ValueError('Horizontal position of charge is not a number')
        #
        # if isinstance(initial_position[2], int) or isinstance(initial_position[2], float):
        #     if -1 * self.detector.total_thickness <= initial_position[2] <= 0.0:
        #         initial_position_z = initial_position[2]
        #     else:
        #         raise ValueError('Z position of charge is outside the detector')
        # else:
        #     raise ValueError('Z position of charge is not a number')

        # initial_position = np.array([initial_position_vertical,
        #                              initial_position_horizontal,
        #                              initial_position_z])
        # position = np.copy(initial_position)

        # trajectory = np.copy(initial_position)

        # pixel = np.array([0, 0])
        # which pixel contains this charge at the end of charge collection phase
        # and after charge transfer

        # Velocity - Maybe later we will need this as well:
        # alpha = 2 * math.pi * random.random()
        # beta = 2. * math.pi * random.random()
        # v_z = v_abs * -1 * math.sin(alpha) #?????
        # v_ver = v_abs * math.cos(alpha) * math.cos(beta)
        # v_hor = v_abs * math.cos(alpha) * math.sin(beta)

        # self.type = particle_type
        if particle_type == 'e':
            particle_type = -1 * cds.e
        elif particle_type == 'h':
            particle_type = +1 * cds.e
        else:
            raise ValueError('Given charged particle type can not be simulated')

        # Energy - Maybe later we will need this as well:
        energy = 0. * u.eV
        if isinstance(initial_energy, int) or isinstance(initial_energy, float):
            energy = initial_energy * u.eV
        else:
            raise ValueError('Given charge (electron/hole) energy could not be read')

        number = particles_per_cluster * u.electron
        # TODO: what if it is a class for holes? should we count them with negative numbers?
        # number of particles per cluster (it is called cluster if there are more than 1 charge)

        # mass = 1.0 * cds.me

        # dict
        new_charge = {'number': number,                                      # int
                      'initial energy': energy,                             # float
                      'energy': energy,                                     # float
                      'init pos ver': initial_position[0],
                      'init pos hor': initial_position[1],
                      'init pos z': initial_position[2],
                      'position ver': initial_position[0],
                      'position hor': initial_position[1],
                      'position z': initial_position[2],
                      'velocity ver': initial_velocity[0],
                      'velocity hor': initial_velocity[1],
                      'velocity z': initial_velocity[2]}
        new_charge_df = pd.DataFrame(new_charge, index=[0])
        self.frame = pd.concat([self.frame, new_charge_df], ignore_index=True)

    # def _plot_trajectory_xy_(self):
    #     plt.figure()
    #     # self.trajectory[:, 0] - VERTICAL COORDINATE
    #     # self.trajectory[:, 1] - HORIZONTAL COORDINATE
    #     # plt.plot(self.trajectory[:, 1], self.trajectory[:, 0], '.')
    #     plt.xlabel('horizontal ($\mu$m)')
    #     plt.ylabel('vertical ($\mu$m)')
    #     plt.title('charge (e/h) trajectory in detector')
    #     plt.axis([0, self.detector.horz_dimension, 0, self.detector.vert_dimension])
    #     plt.grid(True)
    #     plt.draw()
    #
    # def _plot_trajectory_xz_(self):
    #     plt.figure()
    #     # self.trajectory[:, 2] - Z COORDINATE
    #     # self.trajectory[:, 1] - HORIZONTAL COORDINATE
    #     # plt.plot(self.trajectory[:, 1], self.trajectory[:, 2], '.')
    #     plt.xlabel('horizontal ($\mu$m)')
    #     plt.ylabel('z ($\mu$m)')
    #     plt.title('charge (e/h) trajectory in detector')
    #     plt.axis([0, self.detector.horz_dimension, -1*self.detector.total_thickness, 0])
    #     plt.grid(True)
    #     plt.draw()
