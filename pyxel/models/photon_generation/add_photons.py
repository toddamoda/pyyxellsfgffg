"""Pyxel photon generator models."""
import logging
import numpy as np
import esapy_config as om
import pyxel
from pyxel.detectors.detector import Detector


@om.validate
@om.argument(name='level', label='number of photons', units='', validate=om.check_type_function(int))
@pyxel.register(group='photon_generation', name='add photons')
def add_photons(detector: Detector,
                level: int = -1
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
        photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level

    photon_number_list = photon_number_list.flatten()
    photon_energy_list = [0.] * geo.row * geo.col
    detector.photons.generate_with_random_pos_within_pixels(photon_number_list, photon_energy_list)

    return detector
