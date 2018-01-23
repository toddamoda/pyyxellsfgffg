#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! Simulation code for TARS model to generate charges by ionization
"""

from os import path
import numpy as np
# from pyxel.models.tars.tars import TARS_DIR
from pyxel.models.tars.particle import Particle
from pyxel.models.tars.util import sampling_distribution, read_data
# import matplotlib.pyplot as plt


class Simulation:
    """
    Main class of the program, Simulation contain all the methods to set and run a simulation
    """

    def __init__(self, ccd_sim):
        """
        Initialisation of the simulation

        :param CCD ccd_sim: CCD object(from CCD library) containing all the simulated CCD specs
        """

        self.ccd = ccd_sim

        self.spectrum_cdf = None
        self.let_cdf = np.zeros((1, 2))

        self.processing_time = 0

        # self.event_counter = 0
        self.total_charge_array = np.zeros((self.ccd.row, self.ccd.col), int)
        self.ver_limit, self.hor_limit = self.total_charge_array.shape

        self.clusters_per_track = []
        self.all_charge_clusters = []

        self.particle_type = None
        self.initial_energy = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None
        self.angle_alpha = None
        self.angle_beta = None
        self.step_length = None
        self.energy_cut = 1.0e-5        # MeV

        # self.electron_clusters = Charge(self.ccd)
        self.electron_clusters = self.ccd.charge

        self.edep_per_step = []
        self.total_edep_per_particle = []

    def parameters(self, part_type, init_energy, pos_ver, pos_hor, pos_z, alpha, beta, step_length):
        self.particle_type = part_type
        self.initial_energy = init_energy
        self.position_ver = pos_ver
        self.position_hor = pos_hor
        self.position_z = pos_z
        self.angle_alpha = alpha
        self.angle_beta = beta
        self.step_length = step_length

    def set_let_distribution(self):
        """
        Read/generate a Linear Energy Transport distribution from Geant4 data
        for each new particle based on its initial energy (from input spectrum)
        and track length inside the detector
        :return:

        .. warning:: EXPERIMENTAL - NOT FINSHED YET
        """

        TARS_DIR = path.dirname(path.abspath(__file__))
        # particle_let_file = TARS_DIR + '../data/inputs/let_proton_12GeV_100um_geant4.ascii'
        particle_let_file = TARS_DIR + '/data/inputs/let_proton_1GeV_100um_geant4_HighResHist.ascii'

        let_histo = read_data(particle_let_file)  # counts in function of keV

        # TODO: THE DATA NEED TO BE EXTRACTED FROM G4: DEPOSITED ENERGY PER UNIT LENGTH (keV/um)
        # THIS 2 LINE IS TEMPORARY, DO NOT USE THIS!
        data_det_thickness = 100.0    # um
        let_histo[:, 1] /= data_det_thickness   # keV/um

        self.let_cdf = np.stack((let_histo[:, 1], let_histo[:, 2]), axis=1)
        cum_sum = np.cumsum(self.let_cdf[:, 1])
        # cum_sum = np.cumsum(let_dist_interpol)
        cum_sum /= np.max(cum_sum)
        self.let_cdf = np.stack((self.let_cdf[:, 0], cum_sum), axis=1)
        # self.sim_obj.let_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

        # plt.figure()
        # plt.plot(let_histo[:, 1], let_histo[:, 2], '.')
        # plt.draw()
        #
        # plt.figure()
        # plt.plot(self.sim_obj.let_cdf[:, 0], self.sim_obj.let_cdf[:, 1], '.')
        # plt.draw()
        # plt.show()

    def event_generation(self):
        """
        Generation of an event on the CCD due to an incident particle taken according to the simulation configuration
        file

        :return:
        """

        self.clusters_per_track = []

        track_left = False

        p = Particle(self.ccd,
                     self.particle_type,
                     self.initial_energy, self.spectrum_cdf,
                     self.position_ver, self.position_hor, self.position_z,
                     self.angle_alpha, self.angle_beta)

        self.set_let_distribution()

        # main loop : electrons generation and collection at each step while the particle is in the CCD and
        # have enough energy to spread

        # p.position is inside CCD, ionization can not happen in this first step
        p.position[0] += p.dir_ver * self.step_length * 0.1
        p.position[1] += p.dir_hor * self.step_length * 0.1
        p.position[2] += p.dir_z * self.step_length * 0.1

        while True:
            # check if p is still inside CCD and have enough energy:
            if p.position[0] < 0.0 or p.position[0] > self.ccd.vert_dimension:
                break
            if p.position[1] < 0.0 or p.position[1] > self.ccd.horz_dimension:
                break
            if p.position[2] < -1 * self.ccd.total_thickness or p.position[2] > 0.0:
                break
            if p.energy <= self.energy_cut:
                break

            track_left = True

            # IONIZATION
            self._ionization_(p)

            # UPDATE POSITION OF IONIZING PARTICLES
            p.position[0] += p.dir_ver * self.step_length
            p.position[1] += p.dir_hor * self.step_length
            p.position[2] += p.dir_z * self.step_length

            # save particle trajectory
            p.trajectory = np.vstack((p.trajectory, p.position))
        # END of loop

        if track_left:
            self.total_edep_per_particle.append(p.total_edep)  # keV

    def _ionization_(self, particle):

        # particle.energy is in MeV !
        # particle.deposited_energy is in keV !
        particle.deposited_energy = sampling_distribution(self.let_cdf) * self.step_length  # keV

        if particle.deposited_energy >= particle.energy * 1e3:
            particle.deposited_energy = particle.energy * 1e3

        e_kin_energy = 0.1  # eV
        particle.electrons = int(particle.deposited_energy * 1e3 /
                                 (self.ccd.material_ionization_energy + e_kin_energy))     # eV/eV = 1

        self.electron_clusters.create_charge('e',
                                             particle.electrons,
                                             e_kin_energy,
                                             particle.position,
                                             np.array([0., 0., 0.]))
        # self.electron_clusters.create_charge('h',
        #                                      particle.electrons,
        #                                      e_kin_energy,
        #                                      particle.position,
        #                                      np.array([0., 0., 0.]))

        # keV
        particle.deposited_energy = particle.electrons * (e_kin_energy + self.ccd.material_ionization_energy) * 1e-3
        particle.energy -= particle.deposited_energy * 1e-3     # MeV

        self.edep_per_step.append(particle.deposited_energy)    # keV
        particle.total_edep += particle.deposited_energy        # keV
