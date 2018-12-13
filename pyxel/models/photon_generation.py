"""Pyxel photon generator models."""
import os
import logging
import numpy as np
from astropy.io import fits
import esapy_config as om
import pyxel
from pyxel.detectors.detector import Detector


@om.validate
@om.argument(name='image_file', label='fits file', validate=os.path.exists)
@pyxel.register(group='photon_generation', name='load_image')
def load_image(detector: Detector,
               image_file: str,
               row0: int = 0,
               col0: int = 0,
               load_full_image: bool = False
               ) -> Detector:
    """TBW.

    :param detector:
    :param image_file:
    :param row0:
    :param col0:
    :param load_full_image:
    :return:
    """
    logging.info('')
    geo = detector.geometry

    image = fits.getdata(image_file)
    if load_full_image:
        row0, col0 = 0, 0
        geo.row, geo.col = image.shape
    image = image[row0:row0+geo.row, col0:col0+geo.col]
    detector.input_image = image

    return detector


@om.validate
@om.argument(name='level', label='number of photons', units='', validate=om.check_type_function(int))
@pyxel.register(group='photon_generation', name='photon_level')
def add_photon_level(detector: Detector,
                     level: int = -1,
                     ) -> Detector:
    """TBW.

    :param detector:
    :param level:
    :return:
    """
    logging.info('')

    geo = detector.geometry
    cht = detector.characteristics

    if level == -1:
        photon_number_list = detector.input_image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
    else:
        if type(level) is np.ndarray:
            photon_number_list = level
        elif isinstance(level, int):
            photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level
        else:
            photon_number_list = None

    photon_number_list = photon_number_list.flatten()
    photon_energy_list = [0.] * geo.row * geo.col
    detector.photons.generate_photons(photon_number_list, photon_energy_list)

    return detector


# @om.validate
# @om.argument('level', label='number of photons', units='', validate=om.check_type_function(int))
# @pyxel.register('photon_generation', name='photon_level')
# def add_photon_level(detector: Detector,
#                      level: int,
#                      random_seed: int = None) -> Detector:
#     """TBW.
#
#     :param detector:
#     :param level:
#     :param random_seed:
#     :return:
#     """
#     logging.info('')
#
#     # photon_number_list = image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
#     # photon_number_list = photon_number_list.flatten()
#     # photon_energy_list = [0.] * geo.row * geo.col
#     # detector.photons.generate_photons(photon_number_list, photon_energy_list)
#
#     if random_seed:
#         np.random.seed(random_seed)
#     if level and level > 0:
#         geo = detector.geometry
#         photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level
#         photon_energy_list = [0.] * geo.row * geo.col
#         detector.photons.generate_photons(photon_number_list, photon_energy_list)
#     return detector


@om.argument(name='seed', label='random seed', units='', validate=om.check_type_function(int))
@pyxel.register(group='photon_generation', name='shot_noise')
def add_shot_noise(detector: Detector,
                   random_seed: int = 0) -> Detector:
    """Add shot noise to number of photons.

    :param detector:
    :param random_seed:
    :return:
    """
    logging.info('')

    new_detector = detector
    if random_seed:
        np.random.seed(random_seed)
    lambda_list = new_detector.photons.get_photon_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    new_detector.photons.change_all_number(new_list)

    return new_detector
