#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! photon generator functions."""
import os
import numpy as np
from astropy.io import fits

import pyxel
from pyxel.detectors.detector import Detector

import esapy_config as om
# from pyxel.util import objmod as om


@om.argument('image_file', label='Fits File', validate=os.path.exists)
@pyxel.register('photon_generation')
def load_image(detector: Detector,
               image_file: str,
               row0: int = 0,
               col0: int = 0,
               rows: int = None,
               cols: int = None) -> Detector:
    """TBW.

    :param detector:
    :param image_file:
    :param row0:
    :param col0:
    :param rows:
    :param cols:
    :return:
    """
    if image_file:
        geo = detector.geometry
        cht = detector.characteristics
        image = fits.getdata(image_file)

        geo.row, geo.col = image.shape
        if rows is not None:
            geo.row = rows
        if cols is not None:
            geo.col = cols

        image = image[row0:row0+geo.row, col0:col0+geo.col]
        # image = image[0:rows, cols:]
        # image = image[rows:, 0:cols]
        # image = image[rows:, cols:]

        photon_number_list = image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
        # photon_number_list = np.rint(photon_number_list).astype(int).flatten()
        photon_number_list = photon_number_list.flatten()
        photon_energy_list = [0.] * geo.row * geo.col
        detector.photons.generate_photons(photon_number_list, photon_energy_list)

    return detector


@om.argument('level', label='Photons', units='ADU', validate=om.check_range(0, 65535, 1))
@pyxel.register('photon_generation', name='photon_level')
def add_photon_level(detector: Detector,
                     level: int,
                     random_seed: int = None) -> Detector:
    """TBW.

    :param detector:
    :param level:
    :param random_seed:
    :return:
    """
    if random_seed:
        np.random.seed(random_seed)
    if level and level > 0:
        geo = detector.geometry
        photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level
        photon_energy_list = [0.] * geo.row * geo.col
        detector.photons.generate_photons(photon_number_list, photon_energy_list)
    return detector


@pyxel.register('photon_generation', name='shot_noise')
def add_shot_noise(detector: Detector,
                   random_seed: int = None) -> Detector:
    """Add shot noise to number of photons.

    :param detector:
    :param random_seed:
    :return:
    """
    new_detector = detector
    if random_seed:
        np.random.seed(random_seed)
    lambda_list = new_detector.photons.get_photon_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    new_detector.photons.change_all_number(new_list)

    return new_detector
