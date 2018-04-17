#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! TARS model for charge generation by ionization."""

import logging
import math

from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
import typing as t   # noqa: F401

from pyxel.detectors.detector import Detector
from pyxel.models.tars.simulation import Simulation
from pyxel.models.tars.util import read_data, interpolate_data  # , load_histogram_data
from pyxel.pipelines.model_registry import registry

from pyxel.models.tars.plotting import PlottingTARS

# from astropy import units as u


@registry.decorator('charge_generation', name='tars')
def run_tars(detector: Detector,
             particle_type: str = None,
             initial_energy: t.Union[str, float] = None,
             particle_number: int = None,
             incident_angles: tuple = None,
             starting_position: tuple = None,
             mode: str = None,
             # step_size_file: str = None,
             stopping_file: str = None,
             spectrum_file: str = None) -> Detector:
    """TBW.

    :param detector:
    :param particle_type:
    :param initial_energy:
    :param particle_number:
    :param incident_angles:
    :param starting_position:
    :param mode:
    # :param step_size_file:
    :param stopping_file:
    :param spectrum_file:
    :return:
    """
    new_detector = detector

    cosmics = TARS(new_detector)

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
        # starting_position = ('random', 'random', 0.)
        starting_position = ('random', 'random', 'random')  # -> snowflakes (radioactive decay inside detector)

    cosmics.set_particle_type(particle_type)                # MeV
    cosmics.set_initial_energy(initial_energy)              # MeV
    cosmics.set_particle_number(particle_number)            # -
    cosmics.set_incident_angles(incident_angles)            # rad
    cosmics.set_starting_position(starting_position)        # um
    cosmics.set_particle_spectrum(spectrum_file)

    if mode == 'stopping':
        raise NotImplementedError
        # cosmics.set_stopping_power(stopping_file)
        # cosmics.run()
    elif mode == 'stepsize':
        cosmics.set_stepsize()
        cosmics.run()
    elif mode == 'geant4':
        cosmics.set_geant4()
        cosmics.run()
    elif mode == 'plotting':

        plot_obj = PlottingTARS(cosmics, save_plots=True, draw_plots=True)

        # # # plot_obj.plot_flux_spectrum()
        # # # plot_obj.plot_spectrum_cdf()
        # #
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

        # plot_obj.plot_flux_spectrum()

        # plot_obj.plot_gaia_bam_vs_sm_electron_hist(normalize=True)
        # plot_obj.plot_old_tars_hist(normalize=True)
        # plot_obj.plot_gaia_vs_geant4_hist(normalize=True)

        # plot_obj.plot_track_histogram(cosmics.sim_obj.track_length_list)
        # plot_obj.plot_track_histogram(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-track_length_list.npy',
        #                               normalize=True)

        # plot_obj.plot_electron_hist(cosmics.sim_obj.e_num_lst_per_event, normalize=True)

        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-e_num_lst_per_event.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-e_num_lst_per_step.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-p_energy_lst_per_event.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-sec_lst_per_event.npy',
        # plot_obj.plot_electron_hist(r'C:\dev\work\pyxel\pyxel\models\tars\data\validation\G4_app_results_20180417\tars-ter_lst_per_event.npy',
        #                             normalize=True)

        plot_obj.polar_angle_dist(r'C:\dev\work\pyxel\tars-alpha_lst_per_event.npy')

        # todo: not implemented yet:
        # file_path = Path(__file__).parent.joinpath('data', 'inputs', 'all_elec_num_proton.ascii')
        # g4_all_e_num_hist = load_histogram_data(file_path, hist_type='electron', skip_rows=4, read_rows=1000)
        # plot_obj.plot_electron_hist(cosmics.sim_obj.e_num_lst_per_event, g4_all_e_num_hist, normalize=True)

        # plot_obj.plot_electron_hist(cosmics.sim_obj.e_num_lst_per_event,
        #                             cosmics.sim_obj.sec_lst_per_event,
        #                             cosmics.sim_obj.ter_lst_per_event, normalize=True)

        plot_obj.show()
    else:
        raise ValueError

    np.save('tars-e_num_lst_per_event.npy', cosmics.sim_obj.e_num_lst_per_event)
    np.save('tars-sec_lst_per_event.npy', cosmics.sim_obj.sec_lst_per_event)
    np.save('tars-ter_lst_per_event.npy', cosmics.sim_obj.ter_lst_per_event)
    np.save('tars-track_length_lst_per_event.npy', cosmics.sim_obj.track_length_lst_per_event)
    np.save('tars-p_energy_lst_per_event.npy', cosmics.sim_obj.p_energy_lst_per_event)
    np.save('tars-alpha_lst_per_event.npy', cosmics.sim_obj.alpha_lst_per_event)
    np.save('tars-e_num_lst_per_step.npy', cosmics.sim_obj.e_num_lst_per_step)

    # plot_obj = PlottingTARS(cosmics, save_plots=True, draw_plots=True)
    # plot_obj.polar_angle_dist('tars-alpha_lst_per_event.npy')
    # plot_obj.show()
    return new_detector


class TARS:
    """TBW."""

    def __init__(self, detector: Detector) -> None:
        """TBW.

        :param detector:
        """
        self.part_type = None
        self.init_energy = None
        self.particle_number = None
        self.angle_alpha = None
        self.angle_beta = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None

        self.sim_obj = Simulation(detector)
        self.charge_obj = detector.charges
        self.log = logging.getLogger(__name__)

    def set_particle_type(self, particle_type):
        """TBW.

        :param particle_type:
        :return:
        """
        self.part_type = particle_type

    def set_initial_energy(self, energy):
        """TBW.

        :param energy:
        :return:
        """
        self.init_energy = energy

    def set_particle_number(self, number):
        """TBW.

        :param number:
        :return:
        """
        self.particle_number = number

    def set_incident_angles(self, angles):
        """TBW.

        :param angles:
        :return:
        """
        alpha, beta = angles
        self.angle_alpha = alpha
        self.angle_beta = beta

    def set_starting_position(self, start_position):
        """TBW.

        :param start_position:
        :return:
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
        :return:
        """
        self.sim_obj.energy_loss_data = 'stopping'
        self.sim_obj.stopping_power = read_data(stopping_file)

    def set_stepsize(self):
        """TBW.

        :return:
        """
        self.sim_obj.energy_loss_data = 'stepsize'
        self.create_data_library()

    def set_geant4(self):
        """TBW.

        :return:
        """
        self.sim_obj.energy_loss_data = 'geant4'

    def create_data_library(self):
        """TBW.

        :return:
        """
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
        """TBW.

        :return:
        """
        print("TARS - simulation processing...\n")

        self.sim_obj.parameters(self.part_type,
                                self.init_energy,
                                self.position_ver, self.position_hor, self.position_z,
                                self.angle_alpha, self.angle_beta)

        # for _ in tqdm(range(0, self.particle_number)):
        for _ in range(0, self.particle_number):
            if self.sim_obj.energy_loss_data == 'stepsize':     # TODO
                self.sim_obj.event_generation()
            elif self.sim_obj.energy_loss_data == 'geant4':
                self.sim_obj.event_generation_geant4()

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
