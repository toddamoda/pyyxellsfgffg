"""Pyxel TARS model to generate charge by ionization."""

import logging
import math
from pathlib import Path
import typing as t   # noqa: F401
import numpy as np
import pandas as pd
from tqdm import tqdm
from pyxel.detectors.detector import Detector
from pyxel.models.charge_generation.tars.simulation import Simulation
from pyxel.models.charge_generation.tars.util import read_data, interpolate_data  # , load_histogram_data
from pyxel.models.charge_generation.tars.plotting import PlottingTARS

# from astropy import units as u


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def run_tars(detector: Detector,
             simulation_mode: str = None,
             running_mode: str = None,
             particle_type: str = None,
             initial_energy: t.Union[str, float] = None,
             particle_number: int = None,
             incident_angles: tuple = None,
             starting_position: tuple = None,
             # step_size_file: str = None,
             # stopping_file: str = None,
             spectrum_file: str = None,
             random_seed: int = None):
    """Simulate charge deposition by cosmic rays.

    :param detector: Pyxel detector object
    :param particle_type: type of particle: ``proton``, ``alpha``, ``ion``
    :param initial_energy: Kinetic energy of particle
    :param particle_number: Number of particles
    :param incident_angles: incident angles: ``(α, β)``
    :param starting_position: starting position: ``(x, y, z)``
    :param simulation_mode: simulation mode: ``cosmic_rays``, ``radioactive_decay``
    :param running_mode: mode: ``stopping``, ``stepsize``, ``geant4``, ``plotting``
    :param spectrum_file: path to input spectrum
    :param random_seed: seed
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    if random_seed:
        np.random.seed(random_seed)
    tars = TARS(detector)

    if simulation_mode is None:
        raise ValueError('TARS: Simulation mode is not defined')
    if running_mode is None:
        raise ValueError('TARS: Running mode is not defined')
    if particle_type is None:
        raise ValueError('TARS: Particle type is not defined')
    if particle_number is None:
        raise ValueError('TARS: Particle number is not defined')
    if spectrum_file is None:
        raise ValueError('TARS: Spectrum is not defined')

    if initial_energy is None:
        initial_energy = 'random'       # TODO
    if incident_angles is None:
        incident_angles = ('random', 'random')
    if starting_position is None:
        starting_position = ('random', 'random', 'random')

    tars.set_simulation_mode(simulation_mode)
    tars.set_particle_type(particle_type)                # MeV
    tars.set_initial_energy(initial_energy)              # MeV
    tars.set_particle_number(particle_number)            # -
    tars.set_incident_angles(incident_angles)            # rad
    tars.set_starting_position(starting_position)        # um
    tars.set_particle_spectrum(spectrum_file)

    if running_mode == 'stopping':
        # tars.run_mod()          ########
        raise NotImplementedError
        # tars.set_stopping_power(stopping_file)
        # tars.run()
    elif running_mode == 'stepsize':
        tars.set_stepsize()
        tars.run()
    elif running_mode == 'geant4':
        tars.set_geant4()
        tars.run()
    elif running_mode == 'plotting':

        plot_obj = PlottingTARS(tars, save_plots=True, draw_plots=True)

        # # # plot_obj.plot_flux_spectrum()

        #
        # # plot_obj.plot_step_dist()
        # # plot_obj.plot_step_cdf()

        # plot_obj.plot_tertiary_number_cdf()
        # plot_obj.plot_tertiary_number_dist()

        # plot_obj.plot_step_size_histograms(normalize=True)
        # plot_obj.plot_secondary_spectra(normalize=True)
        #
        # # plot_obj.plot_edep_per_step()
        # # plot_obj.plot_edep_per_particle()

        # plot_obj.plot_charges_3d()

        plot_obj.plot_flux_spectrum()

        # plot_obj.plot_gaia_bam_vs_sm_electron_hist(normalize=True)
        # plot_obj.plot_old_tars_hist(normalize=True)

        plot_obj.plot_gaia_vs_gras_hist(normalize=True)

        # plot_obj.plot_track_histogram(tars.sim_obj.track_length_list)
        # plot_obj.plot_track_histogram(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-track_length_lst_per_event.npy',
        #     normalize=True)

        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event, normalize=True)

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_2\tars-e_num_lst_per_step.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_2\tars-p_energy_lst_per_event.npy',

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-e_num_lst_per_event.npy',
        #                             title='all e per event', hist_bins=500, hist_range=(0, 15000))

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-sec_lst_per_event.npy',
        #                             title='secondary e per event', hist_bins=500, hist_range=(0, 15000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180425\tars-ter_lst_per_event.npy',
        #                             title='tertiary e per event', hist_bins=500, hist_range=(0, 15000))

        # plot_obj.plot_spectrum_hist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-p_energy_lst_per_event.npy')
        # plot_obj.plot_spectrum_hist(r'C:\dev\work\pyxel\tars-p_energy_lst_per_event.npy')

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-e_num_lst_per_event.npy',
        #                             title='all e per event', hist_bins=500, hist_range=(0, 15000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-sec_lst_per_event.npy',
        #                             title='secondary e per event', hist_bins=400, hist_range=(0, 2000))
        #
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-ter_lst_per_event.npy',
        #                             title='tertiary e per event', hist_bins=500, hist_range=(0, 5000))

        # plot_obj.plot_spectrum_hist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420\tars-p_energy_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-alpha_lst_per_event.npy')
        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\tars-alpha_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\G4_app_results_20180420_6\tars-beta_lst_per_event.npy')

        # plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\tars-beta_lst_per_event.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)\Raw data\beta.npy')

        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)(17-08-2016_13h51)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\All primary protons from Geant4 Gaia H He GCR(16-08-2016_11h18)(17-08-2016_13h51)\Raw data\beta.npy')

        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel/models/charge_generation/tars/data/validation/Results-20180404T121902Z-001/
        # Results/10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)\Raw data\alpha.npy')
        # plot_obj.polar_angle_dist(
        #     r'C:\dev\work\pyxel\pyxel\models\charge_generation\tars\data\validation\Results-20180404T121902Z-001\
        # Results\10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)\Raw data\beta.npy')

        # todo: not implemented yet:
        # file_path = Path(__file__).parent.joinpath('data', 'inputs', 'all_elec_num_proton.ascii')
        # g4_all_e_num_hist = load_histogram_data(file_path, hist_type='electron', skip_rows=4, read_rows=1000)
        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event, g4_all_e_num_hist, normalize=True)

        # plot_obj.plot_electron_hist(tars.sim_obj.e_num_lst_per_event,
        #                             tars.sim_obj.sec_lst_per_event,
        #                             tars.sim_obj.ter_lst_per_event, normalize=True)

        plot_obj.show()
    else:
        raise ValueError
    #
    # np.save('tars-e_num_lst_per_event.npy', tars.sim_obj.e_num_lst_per_event)
    # np.save('tars-sec_lst_per_event.npy', tars.sim_obj.sec_lst_per_event)
    # np.save('tars-ter_lst_per_event.npy', tars.sim_obj.ter_lst_per_event)
    # np.save('tars-track_length_lst_per_event.npy', tars.sim_obj.track_length_lst_per_event)
    # np.save('tars-p_energy_lst_per_event.npy', tars.sim_obj.p_energy_lst_per_event)
    # np.save('tars-alpha_lst_per_event.npy', tars.sim_obj.alpha_lst_per_event)
    # np.save('tars-beta_lst_per_event.npy', tars.sim_obj.beta_lst_per_event)
    # np.save('tars-e_num_lst_per_step.npy', tars.sim_obj.e_num_lst_per_step)

    # plot_obj = PlottingTARS(tars, save_plots=True, draw_plots=True)
    # plot_obj.plot_charges_3d()
    # plot_obj.show()


class TARS:
    """TBW."""

    def __init__(self, detector: Detector) -> None:
        """TBW.

        :param detector:
        """
        self.simulation_mode = None
        self.part_type = None
        self.init_energy = None
        self.particle_number = None
        self.angle_alpha = None
        self.angle_beta = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None

        self.sim_obj = Simulation(detector)
        self.charge_obj = detector.charge
        self.log = logging.getLogger(__name__)

    def set_simulation_mode(self, sim_mode):
        """TBW.

        :param sim_mode:
        """
        self.simulation_mode = sim_mode

    def set_particle_type(self, particle_type):
        """TBW.

        :param particle_type:
        """
        self.part_type = particle_type

    def set_initial_energy(self, energy):
        """TBW.

        :param energy:
        """
        self.init_energy = energy

    def set_particle_number(self, number):
        """TBW.

        :param number:
        """
        self.particle_number = number

    def set_incident_angles(self, angles):
        """TBW.

        :param angles:
        """
        alpha, beta = angles
        self.angle_alpha = alpha
        self.angle_beta = beta

    def set_starting_position(self, start_position):
        """TBW.

        :param start_position:
        """
        position_vertical, position_horizontal, position_z = start_position
        self.position_ver = position_vertical
        self.position_hor = position_horizontal
        self.position_z = position_z

    def set_particle_spectrum(self, file_name):
        """Set up the particle specs according to a spectrum.

        :param string file_name: path of the file containing the spectrum
        """
        spectrum = read_data(file_name)  # nuc/m2*s*sr*MeV
        geo = self.sim_obj.detector.geometry
        detector_area = geo.vert_dimension * geo.horz_dimension * 1.0e-8  # cm2

        spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * detector_area  # nuc/s*MeV

        spectrum_function = interpolate_data(spectrum)

        lin_energy_range = np.arange(np.min(spectrum[:, 0]), np.max(spectrum[:, 0]), 0.01)
        self.sim_obj.flux_dist = spectrum_function(lin_energy_range)

        cum_sum = np.cumsum(self.sim_obj.flux_dist)
        cum_sum /= np.max(cum_sum)
        self.sim_obj.spectrum_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

    def set_stopping_power(self, stopping_file):
        """TBW.

        :param stopping_file:
        """
        self.sim_obj.energy_loss_data = 'stopping'
        self.sim_obj.stopping_power = read_data(stopping_file)

    def set_stepsize(self):
        """TBW."""
        self.sim_obj.energy_loss_data = 'stepsize'
        self.create_data_library()

    def set_geant4(self):
        """TBW."""
        self.sim_obj.energy_loss_data = 'geant4'

    def create_data_library(self):
        """TBW."""
        self.sim_obj.data_library = pd.DataFrame(columns=['type', 'energy', 'thickness', 'path'])

        # mat_list = ['Si']

        type_list = ['proton']                  # , 'ion', 'alpha', 'beta', 'electron', 'gamma', 'x-ray']
        energy_list = [100.]                    # MeV
        thick_list = [40., 50., 60., 70., 100.]       # um

        path = Path(__file__).parent.joinpath('data', 'inputs')
        filename_list = [
            'stepsize_proton_100MeV_40um_Si_10k.ascii',
            'stepsize_proton_100MeV_50um_Si_10k.ascii',
            'stepsize_proton_100MeV_60um_Si_10k.ascii',
            'stepsize_proton_100MeV_70um_Si_10k.ascii',
            'stepsize_proton_100MeV_100um_Si_10k.ascii'
        ]

        i = 0
        for pt in type_list:
            for en in energy_list:
                for th in thick_list:
                    data_dict = {
                        'type': pt,
                        'energy': en,
                        'thickness': th,
                        'path': str(Path(path, filename_list[i])),
                        }
                    new_df = pd.DataFrame(data_dict, index=[0])
                    self.sim_obj.data_library = pd.concat([self.sim_obj.data_library, new_df], ignore_index=True)
                    i += 1

    def run(self):
        """TBW."""
        # print("TARS - simulation processing...\n")

        self.sim_obj.parameters(self.simulation_mode,
                                self.part_type,
                                self.init_energy,
                                self.position_ver, self.position_hor, self.position_z,
                                self.angle_alpha, self.angle_beta)
        out_path = 'data/'
        for k in tqdm(range(0, self.particle_number)):
            # for k in range(0, self.particle_number):
            err = None
            if self.sim_obj.energy_loss_data == 'stepsize':     # TODO
                err = self.sim_obj.event_generation()
            elif self.sim_obj.energy_loss_data == 'geant4':
                err = self.sim_obj.event_generation_geant4()
            if k % 10 == 0:
                np.save(out_path + 'tars-e_num_lst_per_event.npy', self.sim_obj.e_num_lst_per_event)
                np.save(out_path + 'tars-sec_lst_per_event.npy', self.sim_obj.sec_lst_per_event)
                np.save(out_path + 'tars-ter_lst_per_event.npy', self.sim_obj.ter_lst_per_event)
                np.save(out_path + 'tars-track_length_lst_per_event.npy', self.sim_obj.track_length_lst_per_event)
                np.save(out_path + 'tars-p_energy_lst_per_event.npy', self.sim_obj.p_energy_lst_per_event)
                np.save(out_path + 'tars-alpha_lst_per_event.npy', self.sim_obj.alpha_lst_per_event)
                np.save(out_path + 'tars-beta_lst_per_event.npy', self.sim_obj.beta_lst_per_event)

                np.save(out_path + 'tars-e_num_lst_per_step.npy', self.sim_obj.e_num_lst_per_step)
                np.save(out_path + 'tars-e_pos0_lst.npy', self.sim_obj.e_pos0_lst)
                np.save(out_path + 'tars-e_pos1_lst.npy', self.sim_obj.e_pos1_lst)
                np.save(out_path + 'tars-e_pos2_lst.npy', self.sim_obj.e_pos2_lst)

                np.save(out_path + 'tars-all_e_from_eloss.npy', self.sim_obj.electron_number_from_eloss)
                np.save(out_path + 'tars-sec_e_from_eloss.npy', self.sim_obj.secondaries_from_eloss)
                np.save(out_path + 'tars-ter_e_from_eloss.npy', self.sim_obj.tertiaries_from_eloss)
            if err:
                k -= 1

        size = len(self.sim_obj.e_num_lst_per_step)

        self.sim_obj.e_vel0_lst = [0.] * size
        self.sim_obj.e_vel1_lst = [0.] * size
        self.sim_obj.e_vel2_lst = [0.] * size

        self.charge_obj.add_charge('e',
                                   self.sim_obj.e_num_lst_per_step,
                                   self.sim_obj.e_energy_lst,
                                   self.sim_obj.e_pos0_lst,
                                   self.sim_obj.e_pos1_lst,
                                   self.sim_obj.e_pos2_lst,
                                   self.sim_obj.e_vel0_lst,
                                   self.sim_obj.e_vel1_lst,
                                   self.sim_obj.e_vel2_lst)

    def run_mod(self):
        """TBW."""
        print("TARS - adding previous cosmic ray signals to image ...\n")
        out_path = 'data/'
        e_num_lst_per_step = np.load(out_path + 'tars-e_num_lst_per_step.npy')
        e_pos0_lst = np.load(out_path + 'tars-e_pos0_lst.npy')
        e_pos1_lst = np.load(out_path + 'tars-e_pos1_lst.npy')
        e_pos2_lst = np.load(out_path + 'tars-e_pos2_lst.npy')

        size = len(e_num_lst_per_step)
        e_energy_lst = [0.] * size
        e_vel0_lst = [0.] * size
        e_vel1_lst = [0.] * size
        e_vel2_lst = [0.] * size

        self.charge_obj.add_charge('e',
                                   e_num_lst_per_step,
                                   e_energy_lst,
                                   e_pos0_lst,
                                   e_pos1_lst,
                                   e_pos2_lst,
                                   e_vel0_lst,
                                   e_vel1_lst,
                                   e_vel2_lst)
