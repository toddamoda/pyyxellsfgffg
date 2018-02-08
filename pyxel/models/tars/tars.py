#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! TARS model for charge generation by ionization
"""
import logging
import copy
import math
from os import path

import numpy as np
from numpy import pi
from tqdm import tqdm
# from astropy import units as u

from pyxel.detectors.ccd import CCD
from pyxel.models.tars.simulation import Simulation
from pyxel.models.tars.util import read_data, interpolate_data

# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

TARS_DIR = path.dirname(path.abspath(__file__))


def run_tars(ccd: CCD,
             particle_type: str = 'proton',
             initial_energy: float = 100.0,
             particle_number: int = 1,
             incident_angles: tuple = (pi/10, pi/4),
             starting_position: tuple = (500.0, 500.0, 0.0),
             stepping_length: float = 1.0) -> CCD:

    new_ccd = copy.deepcopy(ccd)

    cosmics = TARS(new_ccd)

    cosmics.set_particle_type(particle_type)        # MeV
    cosmics.set_initial_energy(initial_energy)      # MeV
    cosmics.set_particle_number(particle_number)
    cosmics.set_incident_angles(*incident_angles)     # rad
    # z=0. -> cosmic ray events, z='random' -> snowflakes (radioactive decay inside ccd)
    cosmics.set_starting_position(*starting_position)      # um
    cosmics.set_stepping_length(stepping_length)   # um !

    spectrum_file = TARS_DIR + '/data/inputs/proton_L2_solarMax_11mm_Shielding.txt'
    cosmics.set_particle_spectrum(spectrum_file)

    cosmics.run()

    return new_ccd


class TARS:
    def __init__(self, pyxel_ccd_obj=None):

        self.ccd = pyxel_ccd_obj

        self.part_type = None
        self.init_energy = None
        self.particle_number = None
        self.angle_alpha = None
        self.angle_beta = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None
        self.step_length = None

        # self.data_folder = TARS_DIR + r'\data'
        # self.results_folder = self.data_folder + r'\results'

        self.sim_obj = Simulation(self.ccd)
        self.charge_obj = self.ccd.charges
        self.log = logging.getLogger(__name__)

    def set_particle_type(self, particle_type):
        self.part_type = particle_type

    def set_initial_energy(self, energy):
        self.init_energy = energy

    def set_particle_number(self, number):
        self.particle_number = number

    def set_incident_angles(self, alpha, beta):
        self.angle_alpha = alpha
        self.angle_beta = beta

    def set_starting_position(self, position_vertical, position_horizontal, position_z):
        self.position_ver = position_vertical
        self.position_hor = position_horizontal
        self.position_z = position_z

    def set_stepping_length(self, stepping):
        self.step_length = stepping  # um

    def run(self):
        print("TARS - simulation processing...\n")

        self.sim_obj.parameters(self.part_type,
                                self.init_energy,
                                self.position_ver, self.position_hor, self.position_z,
                                self.angle_alpha, self.angle_beta,
                                self.step_length)

        for _ in tqdm(range(0, self.particle_number)):
            dep = self.sim_obj.event_generation()
            self.log.debug('total deposited E: %4.2f keV', dep)

        size = len(self.sim_obj.e_num_lst)
        self.sim_obj.e_vel0_lst = [0.] * size
        self.sim_obj.e_vel1_lst = [0.] * size
        self.sim_obj.e_vel2_lst = [0.] * size

        self.charge_obj.add_charge('e',
                                   self.sim_obj.e_num_lst,
                                   self.sim_obj.e_energy_lst,
                                   self.sim_obj.e_pos0_lst,
                                   self.sim_obj.e_pos1_lst,
                                   self.sim_obj.e_pos2_lst,
                                   self.sim_obj.e_vel0_lst,
                                   self.sim_obj.e_vel1_lst,
                                   self.sim_obj.e_vel2_lst)

        # np.save('orig2_edep_per_step_10k', self.sim_obj.edep_per_step)
        # np.save('orig2_edep_per_particle_10k', self.sim_obj.total_edep_per_particle)

        # self.plot_edep_per_step()
        # self.plot_edep_per_particle()
        # self.plot_charges_3d()
        # plt.show()

    # def plot_edep_per_step(self):
    #     plt.figure()
    #     n, bins, patches = plt.hist(self.sim_obj.edep_per_step, 300, facecolor='b')
    #     plt.xlabel('E_dep (keV)')
    #     plt.ylabel('Counts')
    #     plt.title('Histogram of E deposited per step')
    #     # plt.axis([0, 0.003, 0, 1.05*max(n)])
    #     plt.grid(True)
    #     plt.draw()
    #     return n, bins, patches
    #
    # def plot_edep_per_particle(self):
    #     plt.figure()
    #     n, bins, patches = plt.hist(self.sim_obj.total_edep_per_particle, 200, facecolor='g')
    #     plt.xlabel('E_dep (keV)')
    #     plt.ylabel('Counts')
    #     plt.title('Histogram of total E deposited per particle')
    #     # plt.axis([0, 0.4, 0, 1.05*max(n)])
    #     plt.grid(True)
    #     plt.draw()
    #     return n, bins, patches

    # def set_stopping_power(self, stopping_file):
    #     self.sim_obj.stopping_power_function = read_data(stopping_file)
    #     self.sim_obj.energy_max_limit = self.sim_obj.stopping_power_function[-1, 0]

    def set_particle_spectrum(self, file_name):
        """
        Setting up the particle specs according to a spectrum

        :param string file_name: path of the file containing the spectrum
        """
        spectrum = read_data(file_name)  # nuc/m2*s*sr*MeV

        ccd_area = self.ccd.vert_dimension * self.ccd.horz_dimension * 1.0e-8  # cm2

        spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * ccd_area  # nuc/s*MeV

        spectrum_function = interpolate_data(spectrum)

        lin_energy_range = np.arange(np.min(spectrum[:, 0]), np.max(spectrum[:, 0]), 0.01)
        flux_dist = spectrum_function(lin_energy_range)

        cum_sum = np.cumsum(flux_dist)
        cum_sum /= np.max(cum_sum)
        self.sim_obj.spectrum_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

        # plt.figure()
        # plt.loglog(lin_energy_range, flux_dist)
        # plt.draw()

        # plt.figure()
        # plt.semilogx(lin_energy_range, cum_sum)
        # plt.draw()

        # plt.show()

    # def plot_charges_3d(self):
    #
    #     # set up a figure twice as wide as it is tall
    #     fig = plt.figure(figsize=plt.figaspect(0.5))
    #     ax = fig.add_subplot(1, 2, 1, projection='3d')
    #
    #     # generator expression
    #     # sum(c.A for c in c_list)
    #     # asc = self.sim_obj.all_charge_clusters[0].position
    #
    #     ############################### need to be fixed
    #     # init_pos0 = [cluster.initial_position[0] for cluster in self.sim_obj.all_charge_clusters]
    #     # init_pos1 = [cluster.initial_position[1] for cluster in self.sim_obj.all_charge_clusters]
    #     # init_pos2 = [cluster.initial_position[2] for cluster in self.sim_obj.all_charge_clusters]
    #     # cluster_size = [cluster.number.value for cluster in self.sim_obj.all_charge_clusters]
    #     #
    #     # ax.scatter(init_pos0, init_pos1, init_pos2, c='b', marker='.', s=cluster_size)
    #     #
    #     # ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    #     #
    #     # pos0 = [cluster.position[0] for cluster in self.sim_obj.all_charge_clusters]
    #     # pos1 = [cluster.position[1] for cluster in self.sim_obj.all_charge_clusters]
    #     # pos2 = [cluster.position[2] for cluster in self.sim_obj.all_charge_clusters]
    #     #
    #     # ax2.scatter(pos0, pos1, 0, c=r', marker='.', s=cluster_size)
    #     #
    #     # ax.set_xlim(0, self.ccd.vert_dimension)
    #     # ax.set_ylim(0, self.ccd.horz_dimension)
    #     # ax.set_zlim(-1*self.ccd.total_thickness, 0)
    #     # ax.set_xlabel('vertical ($\mu$m)')
    #     # ax.set_ylabel('horizontal ($\mu$m)')
    #     # ax.set_zlabel('z ($\mu$m)')
    #     #
    #     # ax2.set_xlim(0, self.ccd.vert_dimension)
    #     # ax2.set_ylim(0, self.ccd.horz_dimension)
    #     # ax2.set_zlim(-1*self.ccd.total_thickness, 0)
    #     # ax2.set_xlabel('vertical ($\mu$m)')
    #     # ax2.set_ylabel('horizontal ($\mu$m)')
    #     # ax2.set_zlabel('z ($\mu$m)')
    #     ##################################
    #     # plt.show()
