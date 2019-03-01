"""Pyxel TARS model to generate charge by ionization."""
import typing as t  # noqa: F401
import numpy as np
import subprocess
from pathlib import Path
from pyxel.detectors.detector import Detector
from .particle import Particle
from .util import read_data_library, read_data, load_histogram_data, \
    sampling_distribution, select_stepsize_data


class Simulation:
    """Main class of the program, Simulation contain all the methods to set and run a simulation."""

    def __init__(self, detector: Detector,
                 running_mode,
                 simulation_mode,
                 particle_type,
                 initial_energy,
                 starting_position,
                 # incident_angles,
                 spectrum=None) -> None:
        """Initialize the simulation.

        :param Detector detector:
        """
        self.detector = detector
        self.simulation_mode = simulation_mode
        self.particle_type = particle_type
        self.running_mode = running_mode                # type: t.Optional[str]
        self.data_library = None
        if running_mode == 'stepsize':
            self.data_library = read_data_library()
        self.energy_cut = 1.0e-5                        # type: float  # in MeV

        # if incident_angles is None:
        #     self.angle_alpha, self.angle_beta = 'random', 'random'
        # else:
        #     self.angle_alpha, self.angle_beta = incident_angles

        if starting_position is None:
            self.position_ver, self.position_hor, self.position_z = 'random', 'random', 'random'
        else:
            self.position_ver, self.position_hor, self.position_z = starting_position

        self.spectrum_cdf = None
        self.initial_energy = None
        if initial_energy == 0.:
            self.spectrum_cdf = spectrum
        else:
            self.initial_energy = initial_energy

        self.elec_number_dist = None
        self.elec_number_cdf = np.zeros((1, 2))
        self.step_size_dist = None
        self.step_cdf = np.zeros((1, 2))
        self.kin_energy_dist = None
        self.kin_energy_cdf = np.zeros((1, 2))

        self.e_num_lst_per_step = []             # type: t.List[int]
        self.e_energy_lst = []                   # type: t.List[float]
        self.e_pos0_lst = []                     # type: t.List[float]
        self.e_pos1_lst = []                     # type: t.List[float]
        self.e_pos2_lst = []                     # type: t.List[float]
        self.e_vel0_lst = []                     # type: t.List[float]
        self.e_vel1_lst = []                     # type: t.List[float]
        self.e_vel2_lst = []                     # type: t.List[float]

        self.electron_number_from_eloss = []     # type: t.List[int]
        self.secondaries_from_eloss = []         # type: t.List[int]
        self.tertiaries_from_eloss = []          # type: t.List[int]

        self.track_length_lst_per_event = []     # type: t.List[float]
        self.e_num_lst_per_event = []            # type: t.List[int]
        self.sec_lst_per_event = []              # type: t.List[int]
        self.ter_lst_per_event = []              # type: t.List[int]
        self.edep_per_step = []                  # type: t.List[float]
        self.total_edep_per_particle = []        # type: t.List[float]
        self.p_energy_lst_per_event = []         # type: t.List[float]
        self.alpha_lst_per_event = []            # type: t.List[float]
        self.beta_lst_per_event = []             # type: t.List[float]

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

        particle = Particle(self.detector,
                            self.simulation_mode,
                            self.particle_type,
                            self.initial_energy, self.spectrum_cdf,
                            self.position_ver, self.position_hor, self.position_z)

        self.track_length_lst_per_event += [particle.track_length]

        if self.running_mode == 'stepsize':
            # data_filename = select_stepsize_data(df=self.data_library, p_type=particle.type,
            #                                      p_energy=particle.energy, p_track_length=particle.track_length)
            data_filename = select_stepsize_data(df=self.data_library, p_type=particle.type,
                                                 p_energy=1000., p_track_length=40.)                # TODO TODO TODO
            self.set_stepsize_distribution(data_filename)
            # TODO make a stack of stepsize cdfs and do not load them more than once!!!

        while True:
            if particle.energy <= self.energy_cut:
                break

            # particle.energy is in MeV !
            # particle.deposited_energy is in keV !

            if self.running_mode == 'stepsize':
                current_step_size = sampling_distribution(self.step_cdf)        # um
                # e_kin_energy = sampling_distribution(self.kin_energy_cdf)     # keV   TODO

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

            if self.running_mode == 'stepsize':
                # the +1 is the original secondary electron
                electron_number = int(sampling_distribution(self.elec_number_cdf)) + 1
                # electron_number = int(e_kin_energy * 1e3 / ioniz_energy) + 1

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
        electron_number_per_event = 0
        secondary_per_event = 0
        tertiary_per_event = 0
        secondaries = 0
        tertiaries = 0

        particle = Particle(self.detector,
                            self.simulation_mode,
                            self.particle_type,
                            self.initial_energy, self.spectrum_cdf,
                            self.position_ver, self.position_hor, self.position_z)

        if particle.track_length < 1.:
            return True

        self.track_length_lst_per_event += [particle.track_length]
        self.p_energy_lst_per_event += [particle.energy]
        self.alpha_lst_per_event += [particle.alpha]
        self.beta_lst_per_event += [particle.beta]

        error = subprocess.call(['./pyxel/models/charge_generation/tars/data/geant4/TestEm18',
                                 'Silicon', particle.type,
                                 str(particle.energy), str(particle.track_length)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if error != 0:
            return True

        # mat = self.detector.material
        # subprocess.call(['./TestEm18', mat.xxx, particle.type,
        # str(particle.energy), str(particle.track_length)'])

        g4_data_energy_path = Path(__file__).parent.joinpath('data', 'geant4', 'tars_geant4_energy.data')
        g4energydata = read_data(g4_data_energy_path)       # MeV

        # primary_e_balance = g4energydata[0] * 1.E6
        all_e_loss = g4energydata[1] * 1.E6
        primary_e_loss = g4energydata[2] * 1.E6
        secondary_e_loss = g4energydata[3] * 1.E6
        if all_e_loss > 0.:
            self.electron_number_from_eloss += [np.floor(all_e_loss / 3.6).astype(int)]
            self.secondaries_from_eloss += [np.floor(primary_e_loss / 3.6).astype(int)]
            self.tertiaries_from_eloss += [np.floor(secondary_e_loss / 3.6).astype(int)]

        g4_data_path = Path(__file__).parent.joinpath('data', 'geant4', 'tars_geant4.data')
        g4data = read_data(g4_data_path)  # mm (!)

        if g4data.shape == (3,):    # alternative running mode, only all electron number without proton step size data
            electron_number_vector = [g4data[0].astype(int)]
            secondaries = g4data[1].astype(int)
            tertiaries = g4data[2].astype(int)
            step_size_vector = [0]
        elif g4data.shape == (0,):
            step_size_vector = []       # um
            electron_number_vector = []
        elif g4data.shape == (2,):
            step_size_vector = [g4data[0] * 1E3]       # um
            electron_number_vector = [g4data[1].astype(int)]
        else:
            step_size_vector = g4data[:, 0] * 1E3       # um
            electron_number_vector = g4data[:, 1].astype(int)

        if np.any(electron_number_vector):
            # for j in range(len(step_size_vector)):
            for j in range(len(electron_number_vector)):

                # UPDATE POSITION OF IONIZING PARTICLES
                particle.position[0] += particle.dir_ver * step_size_vector[j]    # um
                particle.position[1] += particle.dir_hor * step_size_vector[j]    # um
                particle.position[2] += particle.dir_z * step_size_vector[j]      # um

                electron_number_per_event += electron_number_vector[j]
                secondary_per_event += secondaries
                tertiary_per_event += tertiaries

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

        # print('p energy: ', particle.energy, '\ttrack length: ', particle.track_length,
        #       '\telectrons/event: ', electron_number_per_event,
        #       '\tsteps: ', len(step_size_vector), '\terror: ', error)

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
    #     if self.running_mode == 'let':
    #         let_value = sampling_distribution(self.let_cdf)  # keV/um
    #     elif self.running_mode == 'stopping':
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
