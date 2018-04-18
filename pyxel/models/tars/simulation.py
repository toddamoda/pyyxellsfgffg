#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! Simulation code for TARS model to generate charges by ionization."""

import typing as t  # noqa: F401
import numpy as np
from bisect import bisect
import subprocess
from pathlib import Path

from pyxel.models.tars.particle import Particle
from pyxel.models.tars.util import sampling_distribution, load_histogram_data, read_data
from pyxel.detectors.detector import Detector


class Simulation:
    """Main class of the program, Simulation contain all the methods to set and run a simulation."""

    def __init__(self, detector: Detector) -> None:
        """Initialize the simulation.

        :param Detector detector: Detector object(from CCD/CMSO library) containing all the simulated detector specs
        """
        self.detector = detector
        self.simulation_mode = None

        self.flux_dist = None
        self.spectrum_cdf = None

        self.energy_loss_data = None

        self.elec_number_dist = None
        self.elec_number_cdf = np.zeros((1, 2))
        self.step_size_dist = None
        self.step_cdf = np.zeros((1, 2))
        self.kin_energy_dist = None
        self.kin_energy_cdf = np.zeros((1, 2))

        self.data_library = None

        self.stopping_power = None

        self.particle = None

        self.particle_type = None
        self.initial_energy = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None
        self.angle_alpha = None
        self.angle_beta = None
        self.step_length = 1.0          # fix, all the other data/parameters should be adjusted to this
        self.energy_cut = 1.0e-5        # MeV

        self.e_num_lst_per_step = []    # type: t.List[int]
        self.e_energy_lst = []          # type: t.List[float]
        self.e_pos0_lst = []            # type: t.List[float]
        self.e_pos1_lst = []            # type: t.List[float]
        self.e_pos2_lst = []            # type: t.List[float]
        self.e_vel0_lst = []            # type: t.List[float]
        self.e_vel1_lst = []            # type: t.List[float]
        self.e_vel2_lst = []            # type: t.List[float]

        self.track_length_lst_per_event = []         # type: t.List[float]
        self.e_num_lst_per_event = []       # type: t.List[int]
        self.sec_lst_per_event = []         # type: t.List[int]
        self.ter_lst_per_event = []         # type: t.List[int]
        self.edep_per_step = []             # type: t.List[float]
        self.total_edep_per_particle = []   # type: t.List[float]
        self.p_energy_lst_per_event = []    # type: t.List[float]
        self.alpha_lst_per_event = []       # type: t.List[float]
        self.beta_lst_per_event = []        # type: t.List[float]

    def parameters(self, sim_mode, part_type, init_energy, pos_ver, pos_hor, pos_z, alpha, beta):
        """TBW.

        :param sim_mode:
        :param part_type:
        :param init_energy:
        :param pos_ver:
        :param pos_hor:
        :param pos_z:
        :param alpha:
        :param beta:
        :return:
        """
        self.simulation_mode = sim_mode
        self.particle_type = part_type
        self.initial_energy = init_energy
        self.position_ver = pos_ver
        self.position_hor = pos_hor
        self.position_z = pos_z
        self.angle_alpha = alpha
        self.angle_beta = beta

    def find_smaller_neighbor(self, column, value):
        """TBW.

        :return:
        """
        sorted_list = sorted(self.data_library[column].unique())
        index = bisect(sorted_list, value) - 1
        if index < 0:
            index = 0
        return sorted_list[index]

    def find_larger_neighbor(self, column, value):
        """TBW.

        :return:
        """
        sorted_list = sorted(self.data_library[column].unique())
        index = bisect(sorted_list, value)
        if index > len(sorted_list) - 1:
            index = len(sorted_list) - 1
        return sorted_list[index]

    def find_closest_neighbor(self, column, value):
        """TBW.

        :return:
        """
        sorted_list = sorted(self.data_library[column].unique())
        index_smaller = bisect(sorted_list, value) - 1
        index_larger = bisect(sorted_list, value)

        if index_larger >= len(sorted_list):
            return sorted_list[-1]
        elif (sorted_list[index_larger]-value) < (value-sorted_list[index_smaller]):
            return sorted_list[index_larger]
        else:
            return sorted_list[index_smaller]

    def select_stepsize_data(self, p_type, p_energy, p_track_length):
        """TBW.

        :param p_type: str
        :param p_energy: float (MeV)
        :param p_track_length: float (um)
        :return:
        """
        df = self.data_library

        distance = self.find_larger_neighbor('thickness', p_track_length)
        energy = self.find_closest_neighbor('energy', p_energy)

        return df[(df.type == p_type) & (df.energy == energy) & (df.thickness == distance)].path.values[0]

    def set_stepsize_distribution(self, step_size_file):
        """TBW.

        :param step_size_file:
        :return:
        .. warning:: EXPERIMENTAL - NOT FINSHED YET
        """
        # # step size distribution in um
        self.step_size_dist = load_histogram_data(step_size_file, hist_type='step_size',
                                                  skip_rows=4, read_rows=10000)

        cum_sum = np.cumsum(self.step_size_dist['counts'])
        cum_sum /= np.max(cum_sum)
        self.step_cdf = np.stack((self.step_size_dist['step_size'], cum_sum), axis=1)

        # # tertiary electron numbers created by secondary electrons
        self.elec_number_dist = load_histogram_data(step_size_file, hist_type='electron',
                                                    skip_rows=10008, read_rows=10000)

        cum_sum_2 = np.cumsum(self.elec_number_dist['counts'])
        cum_sum_2 /= np.max(cum_sum_2)
        self.elec_number_cdf = np.stack((self.elec_number_dist['electron']-0.5, cum_sum_2), axis=1)

        # # secondary electron spectrum in keV
        # self.kin_energy_dist = load_histogram_data(step_size_file, hist_type='energy', skip_rows=10008, read_rows=200)
        #
        # cum_sum = np.cumsum(self.kin_energy_dist['counts'])
        # cum_sum /= np.max(cum_sum)
        # self.kin_energy_cdf = np.stack((self.kin_energy_dist['energy'], cum_sum), axis=1)

    def event_generation(self):
        """Generate an event.

        :return:
        """
        track_left = False
        electron_number_per_event = 0
        secondary_per_event = 0
        tertiary_per_event = 0
        geo = self.detector.geometry
        mat = self.detector.material
        ioniz_energy = mat.ionization_energy   # eV

        self.particle = Particle(self.detector,
                                 self.simulation_mode,
                                 self.particle_type,
                                 self.initial_energy, self.spectrum_cdf,
                                 self.position_ver, self.position_hor, self.position_z
                                 # self.angle_alpha, self.angle_beta)
                                 )
        particle = self.particle
        self.track_length_lst_per_event += [particle.track_length()]

        if self.energy_loss_data == 'stepsize':
            data_filename = self.select_stepsize_data(particle.type, particle.energy, particle.track_length())
            self.set_stepsize_distribution(data_filename)
            # TODO make a stack of stepsize cdfs and do not load them more than once!!!
        # elif self.energy_loss_data == 'geant4':
        #     pass
        elif self.energy_loss_data == 'stopping':
            raise NotImplementedError  # TODO: implement this

        while True:
            if particle.energy <= self.energy_cut:
                break

            # particle.energy is in MeV !
            # particle.deposited_energy is in keV !

            if self.energy_loss_data == 'stepsize':
                current_step_size = sampling_distribution(self.step_cdf)        # um
                # e_kin_energy = sampling_distribution(self.kin_energy_cdf)     # keV   TODO
            # elif self.energy_loss_data == 'geant4':
            #     pass
            elif self.energy_loss_data == 'stopping':
                raise NotImplementedError   # TODO: implement this

            e_kin_energy = 1.   # TODO
            particle.deposited_energy = e_kin_energy + ioniz_energy * 1e-3  # keV

            # UPDATE POSITION OF IONIZING PARTICLES
            particle.position[0] += particle.dir_ver * current_step_size    # um
            particle.position[1] += particle.dir_hor * current_step_size    # um
            particle.position[2] += particle.dir_z * current_step_size      # um

            # check if p is still inside detector and have enough energy:
            if particle.position[0] <= 0.0 or particle.position[0] >= geo.vert_dimension:
                break
            if particle.position[1] <= 0.0 or particle.position[1] >= geo.horz_dimension:
                break
            if particle.position[2] <= -1 * geo.total_thickness or particle.position[2] >= 0.0:
                break
            if particle.deposited_energy >= particle.energy * 1e3:
                break

            track_left = True

            particle.energy -= particle.deposited_energy * 1e-3     # MeV

            if self.energy_loss_data == 'stepsize':
                # the +1 is the original secondary electron
                electron_number = int(sampling_distribution(self.elec_number_cdf)) + 1
                # electron_number = int(e_kin_energy * 1e3 / ioniz_energy) + 1
            # elif self.energy_loss_data == 'geant4':
            #     electron_number = electron_number_vector[g4_j]
            #     g4_j += 1
            elif self.energy_loss_data == 'stopping':
                raise NotImplementedError

            secondary_per_event += 1
            tertiary_per_event += electron_number - 1
            electron_number_per_event += electron_number
            self.e_num_lst_per_step += [electron_number]

            self.e_energy_lst += [e_kin_energy * 1e3]   # eV
            self.e_pos0_lst += [particle.position[0]]   # um
            self.e_pos1_lst += [particle.position[1]]   # um
            self.e_pos2_lst += [particle.position[2]]   # um

            self.edep_per_step.append(particle.deposited_energy)    # keV
            particle.total_edep += particle.deposited_energy        # keV

            # save particle trajectory
            particle.trajectory = np.vstack((particle.trajectory, particle.position))
        # END of loop

        if track_left:
            self.total_edep_per_particle.append(particle.total_edep)  # keV
            self.e_num_lst_per_event += [electron_number_per_event]
            self.sec_lst_per_event += [secondary_per_event]
            self.ter_lst_per_event += [tertiary_per_event]

        return False

    def event_generation_geant4(self):
        """Generate an event running a geant4 app directly.

        :return:
        """
        # error = None
        electron_number_per_event = 0
        secondary_per_event = 0
        tertiary_per_event = 0

        self.particle = Particle(self.detector,
                                 self.simulation_mode,
                                 self.particle_type,
                                 self.initial_energy, self.spectrum_cdf,
                                 self.position_ver, self.position_hor, self.position_z
                                 # self.angle_alpha, self.angle_beta
                                 )
        particle = self.particle
        if particle.track_length < 1.:
            return True

        self.track_length_lst_per_event += [particle.track_length]
        self.p_energy_lst_per_event += [particle.energy]
        self.alpha_lst_per_event += [particle.alpha]
        self.beta_lst_per_event += [particle.beta]

        error = subprocess.call(['./pyxel/models/tars/data/geant4/TestEm18',
                                 'Silicon', particle.type,
                                 str(particle.energy), str(particle.track_length)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if error != 0:
            return True

        # mat = self.detector.material
        # subprocess.call(['./TestEm18', mat.xxx, particle.type,
        # str(particle.energy), str(particle.track_length)'])

        g4_data_path = Path(__file__).parent.joinpath('data', 'geant4', 'tars_geant4.data')
        g4data = read_data(g4_data_path)            # mm (!)
        if g4data.shape == (2,):
            step_size_vector = [g4data[0] * 1E3]       # um
            electron_number_vector = [g4data[1].astype(int)]
        else:
            step_size_vector = g4data[:, 0] * 1E3       # um
            electron_number_vector = g4data[:, 1].astype(int)

        if np.any(electron_number_vector):
            for j in range(len(step_size_vector)):

                # UPDATE POSITION OF IONIZING PARTICLES
                particle.position[0] += particle.dir_ver * step_size_vector[j]    # um
                particle.position[1] += particle.dir_hor * step_size_vector[j]    # um
                particle.position[2] += particle.dir_z * step_size_vector[j]      # um

                secondary_per_event += 1
                tertiary_per_event += electron_number_vector[j] - 1
                electron_number_per_event += electron_number_vector[j]

                self.e_num_lst_per_step += [electron_number_vector[j]]
                self.e_pos0_lst += [particle.position[0]]   # um
                self.e_pos1_lst += [particle.position[1]]   # um
                self.e_pos2_lst += [particle.position[2]]   # um

                e_kin_energy = 1.
                self.e_energy_lst += [e_kin_energy]   # eV

                # self.edep_per_step.append(particle.deposited_energy)    # keV
                # particle.total_edep += particle.deposited_energy        # keV

                # save particle trajectory
                particle.trajectory = np.vstack((particle.trajectory, particle.position))

            # END of loop

            # self.total_edep_per_particle.append(particle.total_edep)  # keV
            self.e_num_lst_per_event += [electron_number_per_event]
            self.sec_lst_per_event += [secondary_per_event]
            self.ter_lst_per_event += [tertiary_per_event]

        print('p energy: ', particle.energy, '\ttrack length: ', particle.track_length,
              '\telectrons/event: ', electron_number_per_event,
              '\tsteps: ', len(step_size_vector), '\terror: ', error)

        return False

    # def _ionization_(self, particle):
    #     """TBW.
    #
    #     :param particle:
    #     :return:
    #     """
    #     geo = self.detector.geometry
    #     ioniz_energy = geo.ionization_energy
    #     let_value = None
    #
    #     # particle.energy is in MeV !
    #     # particle.deposited_energy is in keV !
    #     if self.energy_loss_data == 'let':
    #         let_value = sampling_distribution(self.let_cdf)  # keV/um
    #     elif self.energy_loss_data == 'stopping':
    #         stopping_power = get_yvalue_with_interpolation(self.stopping_power, particle.energy)  # MeV*cm2/g
    #         let_value = 0.1 * stopping_power * geo.material_density  # keV/um
    #
    #     particle.deposited_energy = let_value * self.step_length  # keV
    #
    #     if particle.deposited_energy >= particle.energy * 1e3:
    #         particle.deposited_energy = particle.energy * 1e3
    #
    #     e_kin_energy = 0.1  # eV
    #     electron_number = int(particle.deposited_energy * 1e3 / (ioniz_energy + e_kin_energy))  # eV/eV = 1
    #
    #     self.e_num_lst += [electron_number]
    #     self.e_energy_lst += [e_kin_energy]
    #     self.e_pos0_lst += [particle.position[0]]
    #     self.e_pos1_lst += [particle.position[1]]
    #     self.e_pos2_lst += [particle.position[2]]
    #
    #     # keV
    #     particle.deposited_energy = electron_number * (e_kin_energy + ioniz_energy) * 1e-3
    #     particle.energy -= particle.deposited_energy * 1e-3     # MeV
    #
    #     self.edep_per_step.append(particle.deposited_energy)    # keV
    #     particle.total_edep += particle.deposited_energy        # keV
