#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""

import sys
import argparse
import shlex
from os import path
import astropy.units as u
from astropy.io import fits

import numpy as np

from pyxel.detectors.ccd import CcdTransferFunction
from pyxel.models.ccd_noise import CcdNoiseGenerator
from pyxel.util.fitsfile import FitsFile
from pyxel.util import config
from pyxel.util import get_data_dir


BASE_DIR = path.dirname(path.abspath(__file__))
REPO_DIR = path.dirname(BASE_DIR)
DATA_DIR = path.join(REPO_DIR, 'data')
OUTPUT_FILE = path.join(DATA_DIR, 'output.data')
OPEN_FITS = False
NOISE_FILE = path.join(DATA_DIR, 'non_uniformity_array_normal_stdev0.03.data')


def frame_photons(num_photons, rows, cols):
    return np.ones((rows, cols)) * num_photons * u.ph   # photon average/pixel


def frame_file(fits):
    return fits.get_data(fits) * u.ADU



class Detector(object):

    def __init__(self, *args, **kwargs):
        pass


class CCDDetector(Detector):

    def __init__(self, **kwargs):
        """
        CCD parameters
        """
        self._p = None    # np int 2D array of incident photon number per pixel
        self._row = kwargs.get('row', 0)      # number of rows in image
        self._col = kwargs.get('col', 0)      # number of columns in image
        self._k = kwargs.get('k', 0.0)        # camera gain constant in digital number (DN)
        self._j = kwargs.get('j', 0.0)        # camera gain constant in photon number
        self._charge = kwargs.get('charge', 0)  # int number of electrons per pixel
        self._qe = kwargs.get('qe', 0.0)      # quantum efficiency
        self._eta = kwargs.get('eta', 0.0)    # quantum yield
        self._sv = kwargs.get('sv', 0.0)      # sensitivity of CCD amplifier [V/-e]
        self._accd = kwargs.get('accd', 0.0)  # output amplifier gain
        self._a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
        self._a2 = kwargs.get('a2', 0)        # gain of the ADC
        self._fwc = kwargs.get('fwc', 0)      # full well compacity

        self._signal = None  # np int 2D array mutable the image data plus the accumulated noise after processing
        self.init_transfer_function(kwargs.get('photons', 0), kwargs.get('fits_file', ''))

    def init_transfer_function(self, photons=0, fits_file=''):
        """
        Initialization of the transfer function: reading data from FITS
        file or generating new data array and calculating the incident
        photon array for each pixel.

        :param ccd: CCD transfer function
        :param photon_mean: incident photon mean
        :type ccd: CcdTransferFunction
        :type photon_mean: 2d numpy array
        """
        if fits_file:  # OPEN EXISTING FITS IMAGE
            if not Path(fits_file).exists():
                fits_file = get_data_dir(fits_file)
            if not Path(fits_file).exists():
                raise IOError('File not found: %s' % fits_file)

            fits_obj = fitsfile.FitsFile(fits_file)
            data = fits_obj.data
            self._row, self._col = data.shape
            self._signal = data  # DN
            self.compute_photon()  # gives ccd.p in photon/pixel
            # now we have the incident photon number per pixel (ccd.p) from the image
        else:  # GENERATE NEW DATA with uniform illumination / gradient
            self._row = 100
            self._col = 100
            # UNIFORM ILLUMINATION / DARK IMAGE:
            print('photon mean: ', photons)
            self._p = np.ones((self._row, self._col)) * photons  # photon average/pixel
            # SIGNAL GRADIENT ON ONE IMAGE:
            # ccd.p = np.arange(1, m*n+1, 1).reshape((m, n))    # photon average/pixel


class Model(object):

    def __init__(self, *args, **kwargs):
        pass


class CCDNoiseGenerator(Model):

    def __init__(self, noise):
        super(CCDNoiseGenerator, self).__init__(noise)

    # SHOT NOISE
    def add_shot_noise(self, photon_mean_array):
        """
        Adding shot noise to incident mean photon array using a Poisson random distribution
        :param photon_mean_array: mean photon number
        :type photon_mean_array: 2d numpy array
        :return: photon array with shot noise
        :rtype: 2d numpy array
        .. note:: mean photon = lambda = sigma**2
        """
        self._shot_noise_array = photon_mean_array - np.random.poisson(lam=photon_mean_array)
        photon_mean_array -= self._shot_noise_array

        return photon_mean_array

    # FIXED PATTERN NOISE (periodic)
    def add_fix_pattern_noise(self, charge_array, noise_file):
        """
        Adding fix pattern noise to charge array using the same pixel non-uniformity array loaded from a text file
        Charge unit: e-
        :param charge_array: charge
        :type charge_array: 2d numpy array
        :return: modified charge with pixel non-uniformity
        :rtype: 2d numpy array
        .. todo:: calc and save PN value, check and regenerate the pixel non-uniformity array if PN value has changed
        .. note:: pixel non-uniformity: Pn = sigma_signal(DN) / S(DN)  # percentage
        """
        m, n = charge_array.shape

        self._pixel_non_uniform_array = np.fromfile(noise_file, dtype=float, sep=' ').reshape((m, n))
        self._pixel_non_uniform_array = self._pixel_non_uniform_array.reshape((m, n))
        charge_array = charge_array * self._pixel_non_uniform_array
        charge_array = np.int16(np.rint(charge_array))

        return charge_array

    # READOUT NOISE
    def add_readout_noise(self, signal_mean_array):
        """
        Adding readout noise to signal array using normal random distribution
        Signal unit: DN
        :param signal_mean_array: signal
        :type signal_mean_array: 2d numpy array
        :return: signal with readout noise
        :rtype: 2d numpy array
        """
        m, n = signal_mean_array.shape
        sigma_readout_array = self._readout_sigma * np.ones((m, n)).reshape((m, n))

        self._readout_noise_array = np.random.normal(loc=0.0, scale=sigma_readout_array)
        signal_mean_array = signal_mean_array.astype('float64') + self._readout_noise_array
        signal_mean_array = np.int16(np.rint(signal_mean_array))

        return signal_mean_array


class Processor(object):

    def __init__(self, input_parameters_config_object, detector, models):
        pass

    def compute(self):
        return None


class CCDTransferFunction(Processor):

    def __init__(self, ccd, model):
        super(CCDTransferFunction, self).__init__()
        self.model = model
        self.ccd = ccd

    def compute(self):
        # SHOT NOISE
        if self.model.shot_noise:
            self.ccd.p = self.model.add_shot_noise(self.ccd.p)

        # calculate charges per pixel
        self.ccd.compute_charge()

        # FIXED PATTERN NOISE
        if self.model.fix_pattern_noise:
            self.ccd.charge = self.model.add_fix_pattern_noise(self.ccd.charge, NOISE_FILE)

        # limiting charges per pixel due to Full Well Capacity
        self.ccd.charge_excess()

        # Signal with shot and fix pattern noise
        self.ccd.compute_signal()

        # READOUT NOISE
        if self.model.readout_noise:
            self.model.readout_sigma = 10.0
            self.ccd.signal = self.model.add_readout_noise(self.ccd.signal)

        return self.ccd.signal

def run(opts):

    ccd = CCDDetector(opts)
    model = CCDNoiseGenerator(opts)
    proc = CCDTransferFunction(ccd, model)
    result = proc.compute()
    # need to do somwthing result


#
#
# def load_input(opts):
#
#     ccd = CcdTransferFunction(**vars(opts.ccd))
#     noise = CcdNoiseGenerator()
#     return ccd, noise
#
#
# def simulate_noise(opts, ccd, noise):
#
#     # SHOT NOISE
#     if opts.model.shot_noise:
#         ccd.p = noise.add_shot_noise(ccd.p)
#
#     # calculate charges per pixel
#     ccd.compute_charge()
#
#     # FIXED PATTERN NOISE
#     if opts.model.fix_pattern_noise:
#         ccd.charge = noise.add_fix_pattern_noise(ccd.charge, NOISE_FILE)
#
#     # limiting charges per pixel due to Full Well Capacity
#     ccd.charge_excess()
#
#     # Signal with shot and fix pattern noise
#     ccd.compute_signal()
#
#     # READOUT NOISE
#     if opts.model.readout_noise:
#         noise.readout_sigma = 10.0
#         ccd.signal = noise.add_readout_noise(ccd.signal)
#
#     return ccd
#
#
# def save_output(opts, ccd):
#
#     # SIGNAL MEAN AND DEVIATION, in case of uniform illumination
#     n_pixel = ccd.row * ccd.col
#     signal_offset = 0
#
#     signal_mean = np.sum(ccd.signal) / n_pixel - signal_offset
#     signal_variance = np.sum((ccd.signal - signal_mean) ** 2) / n_pixel
#     signal_sigma = np.sqrt(signal_variance)
#     # here is no differencing aka pixel non-uniformity removal
#     print('\nsignal mean: ', signal_mean)
#     print('signal sigma: ', signal_sigma)
#
#     # OUTPUTS
#     head = None
#     # creating new fits file with new data
#     if opts.output.fits:
#         out_file = get_data_dir(opts.output.fits)
#         new_fits_file = FitsFile(out_file)
#         if OPEN_FITS:
#             new_fits_file.save(ccd.signal, head)
#         else:
#             new_fits_file.save(ccd.signal)
#             # *** BUG here: HEADER is not the same in the new file, EXTEND keyword and value are missing!
#             # check bitpix of FITS image during opening and convert type of input data according to that
#
#     # writing ascii output file
#     if opts.output.data:
#         out_file = get_data_dir(opts.output.data)
#         with open(out_file, 'a+') as file_obj:
#             data = [
#                 '{:6d}'.format(opts.ccd.photons),
#                 '{:8.2f}'.format(signal_mean),
#                 '{:7.2f}'.format(signal_sigma)
#             ]
#             out_str = '\t'.join(data) + '\n'
#             file_obj.write(out_str)
#
#
# def run(opts):
#
#     input_obj = load_input(opts)
#     output = simulate_noise(opts, *input_obj)
#     save_output(opts, output)

#
# def process_org(opts):
#
#     # photon_mean = opts.input.photons
#
#     # objects
#     # kwargs = {}
#     # kwargs.update(vars(opts.ccd))
#     # kwargs.update(vars(opts.input))
#     ccd = CcdTransferFunction(**vars(opts.ccd))
#     noise = CcdNoiseGenerator()
#
#     # set_transfer_parameters(ccd)
#     #
#     # init_transfer_function(ccd, photon_mean)
#
#     # SHOT NOISE
#     if opts.model.shot_noise:
#         ccd.p = noise.add_shot_noise(ccd.p)
#
#     # calculate charges per pixel
#     ccd.compute_charge()
#
#     # FIXED PATTERN NOISE
#     if opts.model.fix_pattern_noise:
#         ccd.charge = noise.add_fix_pattern_noise(ccd.charge, NOISE_FILE)
#
#     # limiting charges per pixel due to Full Well Capacity
#     ccd.charge_excess()
#
#     # Signal with shot and fix pattern noise
#     ccd.compute_signal()
#
#     # READOUT NOISE
#     if opts.model.readout_noise:
#         noise.readout_sigma = 10.0
#         ccd.signal = noise.add_readout_noise(ccd.signal)
#
#     # SIGNAL MEAN AND DEVIATION, in case of uniform illumination
#     n_pixel = ccd.row * ccd.col
#     signal_offset = 0
#
#     signal_mean = np.sum(ccd.signal) / n_pixel - signal_offset
#     signal_variance = np.sum((ccd.signal - signal_mean) ** 2) / n_pixel
#     signal_sigma = np.sqrt(signal_variance)
#     # here is no differencing aka pixel non-uniformity removal
#     print('\nsignal mean: ', signal_mean)
#     print('signal sigma: ', signal_sigma)
#
#     # OUTPUTS
#     head = None
#     # creating new fits file with new data
#     if opts.output.fits:
#         out_file = get_data_dir(opts.output.fits)
#         new_fits_file = FitsFile(out_file)
#         if OPEN_FITS:
#             new_fits_file.save(ccd.signal, head)
#         else:
#             new_fits_file.save(ccd.signal)
#             # *** BUG here: HEADER is not the same in the new file, EXTEND keyword and value are missing!
#             # check bitpix of FITS image during opening and convert type of input data according to that
#
#     # writing ascii output file
#     if opts.output.data:
#         out_file = get_data_dir(opts.output.data)
#         with open(out_file, 'a+') as file_obj:
#             data = [
#                 '{:6d}'.format(opts.ccd.photons),
#                 '{:8.2f}'.format(signal_mean),
#                 '{:7.2f}'.format(signal_sigma)
#             ]
#             out_str = '\t'.join(data) + '\n'
#             file_obj.write(out_str)


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
    parser.add_argument('--config', '-c', type=str, default='settings.ini',
                        help='the configuration file to load')

    if cmdline:
        cmdline = shlex.split(cmdline)
    opts = parser.parse_args(cmdline)

    if opts.config:
        settings = config.load(opts.config)

    run(settings)


if __name__ == '__main__':
    CMDLINE = None
    main(CMDLINE)
