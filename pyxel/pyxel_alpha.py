#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""

import argparse
import shlex
from os import path
import astropy.units as u
from astropy.io import fits

import numpy as np
from math import pi

from pyxel.detectors.ccd import CCDDetector
from pyxel.models.ccd_noise import CCDNoiseGenerator
# from pyxel.pipelines.ccd_transfer_function import CCDTransferFunction

from pyxel.util.fitsfile import FitsFile
from pyxel.util import config
from pyxel.util import get_data_dir
from pyxel.models.tars.tars_v3 import TARS

BASE_DIR = path.dirname(path.abspath(__file__))
REPO_DIR = path.dirname(BASE_DIR)
DATA_DIR = path.join(REPO_DIR, 'data')
OUTPUT_FILE = path.join(DATA_DIR, 'output.data')
TARS_DIR = r'C:\dev\work\pyxel\pyxel\models\tars'
OPEN_FITS = False
NOISE_FILE = path.join(DATA_DIR, 'non_uniformity_array_normal_stdev0.03.data')


def frame_photons(num_photons, rows, cols):
    return np.ones((rows, cols)) * num_photons * u.ph   # photon average/pixel


def frame_file(fits):
    return fits.get_data(fits) * u.ADU


def run(opts):

    ccd = CCDDetector(**opts.detector)
    model = CCDNoiseGenerator(**opts.model)
    proc = CCDTransferFunction(ccd, model)
    result = proc()
    # need to do somwthing result



def process(opts):

    # photon_mean = opts.input.photons

    # objects
    # kwargs = {}
    # kwargs.update(vars(opts.ccd))
    # kwargs.update(vars(opts.input))
    ccd = CcdTransferFunction(**vars(opts.ccd))

    # MODELS:
    noise = CcdNoiseGenerator()

    # set_transfer_parameters(ccd)
    #
    # init_transfer_function(ccd, photon_mean)

    # SHOT NOISE
    if opts.model.shot_noise:
        ccd.p = noise.add_shot_noise(ccd.p)

    # calculate charges per pixel
    ccd.compute_charge()

    # FIXED PATTERN NOISE
    if opts.model.fix_pattern_noise:
        ccd.charge = noise.add_fix_pattern_noise(ccd.charge, NOISE_FILE)

    cosmics = TARS(ccd)

    # cosmics.set_initial_energy('random')      # MeV
    # cosmics.set_particle_number(1)
    # cosmics.set_incident_angles('random', 'random')
    # # z=0. -> cosmic ray events, z='random' -> snowflakes (radioactive decay inside ccd)
    # cosmics.set_starting_position('random', 'random', 0.0)
    # cosmics.set_stepping_length(1.0)   # um !

    cosmics.set_initial_energy(100)     # MeV
    cosmics.set_particle_number(1)
    cosmics.set_incident_angles(pi/10, pi/4)     # rad
    # z=0. -> cosmic ray events, z='random' -> snowflakes (radioactive decay inside ccd)
    cosmics.set_starting_position(500.0, 500.0, 0.0)      # um
    cosmics.set_stepping_length(1.0)   # um !

    stopping_file = TARS_DIR + r'\data\inputs\stopping_power_protons.txt'
    spectrum_file = TARS_DIR + r'\data\inputs\proton_L2_solarMax_11mm_Shielding.txt'
    cosmics.set_particle_spectrum(spectrum_file)
    cosmics.set_stopping_power(stopping_file)

    cosmics.run()

    ccd.charge = ccd.charge + cosmics.get_deposited_charge()

    # limiting charges per pixel due to Full Well Capacity
    ccd.charge_excess()
    # Signal with shot and fix pattern noise
    ccd.compute_signal()

    # READOUT NOISE
    if opts.model.readout_noise:
        noise.readout_sigma = 10.0
        ccd.signal = noise.add_readout_noise(ccd.signal)

    # SIGNAL MEAN AND DEVIATION, in case of uniform illumination
    n_pixel = ccd.row * ccd.col
    signal_offset = 0

    signal_mean = np.sum(ccd.signal) / n_pixel - signal_offset
    signal_variance = np.sum((ccd.signal - signal_mean) ** 2) / n_pixel
    signal_sigma = np.sqrt(signal_variance)
    # here is no differencing aka pixel non-uniformity removal
    print('\nsignal mean: ', signal_mean)
    print('signal sigma: ', signal_sigma)

    # OUTPUTS
    head = None
    # creating new fits file with new data
    if opts.output.fits:
        out_file = get_data_dir(opts.output.fits)
        new_fits_file = FitsFile(out_file)
        if OPEN_FITS:
            new_fits_file.save(ccd.signal, head)
        else:
            new_fits_file.save(ccd.signal)
            # *** BUG here: HEADER is not the same in the new file, EXTEND keyword and value are missing!
            # check bitpix of FITS image during opening and convert type of input data according to that

    # writing ascii output file
    if opts.output.data:
        out_file = get_data_dir(opts.output.data)
        with open(out_file, 'a+') as file_obj:
            data = [
                '{:6d}'.format(opts.ccd.photons),
                '{:8.2f}'.format(signal_mean),
                '{:7.2f}'.format(signal_sigma)
            ]
            out_str = '\t'.join(data) + '\n'
            file_obj.write(out_str)


def main(cmdline=None):
    """
    Main entry point

    Current features: adding readout, shot and fix pattern noise to FITS image created by a CCD detector
    Amount of charge per pixel is limited by the full well capacity

    :param: P - mean incident photon number per pixel (arg parser)
    :type: int
    """
    print("PyXel! beta")

    # ARGUMENT PARSER
    parser = argparse.ArgumentParser(description='Adding noises to CCD signal')
    # parser.add_argument('--photons', '-p', type=int,
    #                     help='average number of photons per pixel')
    parser.add_argument('--config', '-c', type=str, default='settings.ini',
                        help='the configuration file to load')

    if cmdline:
        cmdline = shlex.split(cmdline)
    opts = parser.parse_args(cmdline)

    if opts.config:
        settings = config.load(opts.config)

    # settings.ccd.photons = opts.photons

    process(settings)
    run(settings)


if __name__ == '__main__':
    CMDLINE = None
    main(CMDLINE)
