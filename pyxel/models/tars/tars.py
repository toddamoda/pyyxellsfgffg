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
from pyxel.models.tars.util import read_data, interpolate_data
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
        starting_position = ('random', 'random', 0.)
        # starting_position = ('random', 'random', 'random') -> snowflakes (radioactive decay inside detector)

    cosmics.set_particle_type(particle_type)                # MeV
    cosmics.set_initial_energy(initial_energy)              # MeV
    cosmics.set_particle_number(particle_number)            # -
    cosmics.set_incident_angles(incident_angles)            # rad
    cosmics.set_starting_position(starting_position)        # um
    cosmics.set_particle_spectrum(spectrum_file)

    if stopping_file is not None:
        raise NotImplementedError
        # cosmics.set_stopping_power(stopping_file)
    else:
        cosmics.set_stepsize()

    cosmics.run()

    plot_obj = PlottingTARS(cosmics, save_plots=True, show_plots=True)
    # #
    # # # plot_obj.plot_flux_spectrum()
    # # # plot_obj.plot_spectrum_cdf()
    # #
    # # plot_obj.plot_step_dist()
    # # plot_obj.plot_step_cdf()
    #
    # plot_obj.plot_step_size_histograms(normalize=True)
    # plot_obj.plot_secondary_spectra(normalize=True)
    #
    # # plot_obj.plot_charges_3d()
    # #
    # # plot_obj.plot_edep_per_step()
    # # plot_obj.plot_edep_per_particle()

    # plot_obj.plot_electron_number_histos(normalize=True)
    plot_obj.plot_electron_number_histos()

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

    def create_data_library(self):
        """TBW.

        :return:
        """
        self.sim_obj.data_library = pd.DataFrame(columns=['type', 'energy', 'thickness', 'path'])

        type_list = ['proton']          # , 'ion', 'alpha', 'beta', 'electron', 'gamma', 'x-ray']
        energy_list = [100., 1000.]            # MeV
        thick_list = [10., 50., 100., 200.]    # um

        path = Path(__file__).parent.joinpath('data', 'inputs')
        filename_list = ['stepsize_proton_100MeV_10um_1M.ascii',
                         'stepsize_proton_100MeV_50um_1M.ascii',
                         'stepsize_proton_100MeV_100um_1M.ascii',
                         'stepsize_proton_100MeV_200um_1M.ascii',
                         'stepsize_proton_1GeV_10um_1M.ascii',
                         'stepsize_proton_1GeV_50um_1M.ascii',
                         'stepsize_proton_1GeV_100um_1M.ascii',
                         'stepsize_proton_1GeV_200um_1M.ascii']

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

        for _ in tqdm(range(0, self.particle_number)):
            self.sim_obj.event_generation()

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
