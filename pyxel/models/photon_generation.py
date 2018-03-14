#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! photon generator functions."""
import numpy as np
from astropy.io import fits
# from astropy import units as u

from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_registry import registry


@registry.decorator('photon_generation')
def load_image(detector: Detector, image_file: str) -> Detector:
    """TBW.

    :param detector:
    :param image_file:
    :return:
    """
    if image_file:
        geo = detector.geometry
        cht = detector.characteristics
        image = fits.getdata(image_file)
        geo.row, geo.col = image.shape
        photon_number_list = image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
        photon_number_list = np.rint(photon_number_list).astype(int).flatten()
        photon_energy_list = [0.] * geo.row * geo.col
        detector.photons.generate_photons(photon_number_list, photon_energy_list)

    return detector


@registry.decorator('photon_generation', name='photon_level',
                    gui={
                        'label': 'Uniform illumination',
                        'arguments': {
                            'level': {
                                'label': 'Photons',
                                'entry': registry.entry.num_uint}

                        }
                    })
def add_photon_level(detector: Detector, level: int) -> Detector:
    """TBW.

    :param detector:
    :param level:
    :return:
    """
    if level and level > 0:
        geo = detector.geometry
        photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level
        photon_energy_list = [0.] * geo.row * geo.col
        detector.photons.generate_photons(photon_number_list, photon_energy_list)

    return detector


@registry.decorator('photon_generation', name='shot_noise')
def add_shot_noise(detector: Detector) -> Detector:
    """Add shot noise to number of photons.

    :return:
    """
    new_detector = detector

    lambda_list = new_detector.photons.get_photon_numbers()
    lambda_list = [float(i) for i in lambda_list]
    new_list = np.random.poisson(lam=lambda_list)  # * u.ph
    new_detector.photons.change_all_number(new_list)

    return new_detector
