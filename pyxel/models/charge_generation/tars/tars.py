"""Pyxel TARS model to generate charge by ionization."""
import logging
import math
from pathlib import Path
import numpy as np
import pandas as pd
import pyxel
from pyxel.detectors.detector import Detector
from pyxel.models.charge_generation.tars.simulation import Simulation
from pyxel.models.charge_generation.tars.util import read_data, interpolate_data
# from pyxel.models.charge_generation.tars.plotting import PlottingTARS
# from astropy import units as u


@pyxel.validate
@pyxel.argument(name='simulation_mode', label='', units='',
                validate=pyxel.check_choices(['cosmic_ray']))      # 'radioactive_decay'
@pyxel.argument(name='running_mode', label='', units='',
                validate=pyxel.check_choices(['stepsize']))         # 'stopping', 'geant4'
@pyxel.argument(name='particle_type', label='', units='',
                validate=pyxel.check_choices(['proton']))           # 'alpha', 'ion'
@pyxel.argument(name='initial_energy', label='', units='',
                validate=pyxel.check_type(float))
@pyxel.argument(name='particle_number', label='', units='',
                validate=pyxel.check_type(int))
@pyxel.argument(name='spectrum_file', label='', units='',
                validate=pyxel.check_path)
def tars(detector: Detector,
         running_mode: str = 'stepsize',
         simulation_mode: str = 'cosmic_ray',
         particle_type: str = 'proton',
         particle_number: int = 10,         # -
         initial_energy: float = 0.,        # MeV
         spectrum_file: str =               # MeV
         'pyxel/models/charge_generation/tars/data/inputs/proton_L2_solarMax_11mm_Shielding.txt',
         incident_angles: list = None,      # rad
         starting_position: list = None,    # um
         random_seed: int = None):
    """Simulate charge deposition by cosmic rays.

    :param detector: Pyxel detector object
    :param running_mode: mode: ``stepsize``                     # ``geant4``
    :param simulation_mode: simulation mode: ``cosmic_rays``    # ``radioactive_decay``
    :param particle_type: type of particle: ``proton``          # ``alpha``, ``ion``
    :param particle_number: Number of particles
    :param initial_energy: Kinetic energy of particle in MeV
    :param spectrum_file: path to input spectrum in MeV
    :param incident_angles: incident angles: ``[α, β]`` in rad
    :param starting_position: starting position: ``[x, y, z]`` in um
    :param random_seed: seed
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    if random_seed:
        np.random.seed(random_seed)

    spectrum = None
    if initial_energy == 0.:
        geo = detector.geometry
        area = geo.vert_dimension * geo.horz_dimension * 1.0e-8    # cm^2
        spectrum = read_particle_spectrum(spectrum_file, detector_area=area)

    tars = Simulation(detector=detector,
                      simulation_mode=simulation_mode,
                      particle_type=particle_type,
                      initial_energy=initial_energy,
                      spectrum=spectrum,
                      starting_position=starting_position,
                      incident_angles=incident_angles)

    tars.energy_loss_data = running_mode
    if running_mode == 'stepsize':
        tars.data_library = create_data_library()

    # elif running_mode == 'stopping':
    #     tars.stopping_power = read_data(stopping_file)

    # plot_obj = PlottingTARS(tars, save_plots=True, draw_plots=True)
    # plot_obj.plot_flux_spectrum()
    # plot_obj.plot_gaia_vs_gras_hist(normalize=True)
    # plot_obj.show()

    for k in range(0, particle_number):
        err = None
        if tars.energy_loss_data == 'stepsize':     # TODO
            err = tars.event_generation()
        elif tars.energy_loss_data == 'geant4':
            err = tars.event_generation_geant4()
        # if k % 10 == 0:
        #     np.save(out_path + 'tars-e_num_lst_per_event.npy', tars.e_num_lst_per_event)
        #     np.save(out_path + 'tars-sec_lst_per_event.npy', tars.sec_lst_per_event)
        #     np.save(out_path + 'tars-ter_lst_per_event.npy', tars.ter_lst_per_event)
        #     np.save(out_path + 'tars-track_length_lst_per_event.npy', tars.track_length_lst_per_event)
        #     np.save(out_path + 'tars-p_energy_lst_per_event.npy', tars.p_energy_lst_per_event)
        #     np.save(out_path + 'tars-alpha_lst_per_event.npy', tars.alpha_lst_per_event)
        #     np.save(out_path + 'tars-beta_lst_per_event.npy', tars.beta_lst_per_event)
        #
        #     np.save(out_path + 'tars-e_num_lst_per_step.npy', tars.e_num_lst_per_step)
        #     np.save(out_path + 'tars-e_pos0_lst.npy', tars.e_pos0_lst)
        #     np.save(out_path + 'tars-e_pos1_lst.npy', tars.e_pos1_lst)
        #     np.save(out_path + 'tars-e_pos2_lst.npy', tars.e_pos2_lst)
        #
        #     np.save(out_path + 'tars-all_e_from_eloss.npy', tars.electron_number_from_eloss)
        #     np.save(out_path + 'tars-sec_e_from_eloss.npy', tars.secondaries_from_eloss)
        #     np.save(out_path + 'tars-ter_e_from_eloss.npy', tars.tertiaries_from_eloss)
        if err:
            k -= 1

    size = len(tars.e_num_lst_per_step)

    tars.e_vel0_lst = [0.] * size
    tars.e_vel1_lst = [0.] * size
    tars.e_vel2_lst = [0.] * size

    detector.charge.add_charge('e',
                               tars.e_num_lst_per_step,
                               tars.e_energy_lst,
                               tars.e_pos0_lst,
                               tars.e_pos1_lst,
                               tars.e_pos2_lst,
                               tars.e_vel0_lst,
                               tars.e_vel1_lst,
                               tars.e_vel2_lst)


def read_particle_spectrum(file_name, detector_area):
    """Set up the particle specs according to a spectrum.

    :param file_name: path of the file containing the spectrum
    :param detector_area: area of detector
    """
    spectrum = read_data(file_name)                             # nuc/m2*s*sr*MeV
    spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * detector_area      # nuc/s*MeV     # TODO TODO !

    spectrum_function = interpolate_data(spectrum)

    lin_energy_range = np.arange(np.min(spectrum[:, 0]), np.max(spectrum[:, 0]), 0.01)

    cum_sum = np.cumsum(spectrum_function(lin_energy_range))
    cum_sum /= np.max(cum_sum)
    spectrum_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

    return spectrum_cdf


def create_data_library():
    """TBW."""
    data_library = pd.DataFrame(columns=['type', 'energy', 'thickness', 'path'])

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
                data_library = pd.concat([data_library, new_df], ignore_index=True)
                i += 1

    return data_library
