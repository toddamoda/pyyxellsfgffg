"""Pyxel photon generator models."""
import logging
import numpy as np
import pyxel
from pyxel import check_type
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='level', label='number of photons', units='', validate=check_type(int))
def add_photons(detector: Detector,
                level: int):
    """Generate photons uniformly (uniform illumination).

    :param detector: Pyxel Detector object
    :param level: number of photons per pixel, int
    """
    logging.info('')
    geo = detector.geometry
    detector.photons.array = np.ones((geo.row, geo.col), dtype=int) * level

    # if level == -1:
    #     photon_number_list = detector.input_image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
    # else:
    #     photon_number_list = np.ones(geo.row * geo.col, dtype=int) * level
    #
    # photon_number_list = photon_number_list.flatten()
    # photon_energy_list = [0.] * geo.row * geo.col
    #
    # pixel_numbers = geo.row * geo.col
    #
    # init_ver_position = np.arange(0.0, geo.row, 1.0) * geo.pixel_vert_size
    # init_hor_position = np.arange(0.0, geo.col, 1.0) * geo.pixel_horz_size
    #
    # init_ver_position = np.repeat(init_ver_position, geo.col)
    # init_hor_position = np.tile(init_hor_position, geo.row)
    #
    # init_ver_position += np.random.rand(pixel_numbers) * geo.pixel_vert_size
    # init_hor_position += np.random.rand(pixel_numbers) * geo.pixel_horz_size
    #
    # init_z_position = [0.] * pixel_numbers
    # init_ver_velocity = [0.] * pixel_numbers
    # init_hor_velocity = [0.] * pixel_numbers
    # init_z_velocity = [0.] * pixel_numbers
    #
    # detector.photons.add_photon(photon_number_list,
    #                             photon_energy_list,
    #                             init_ver_position,
    #                             init_hor_position,
    #                             init_z_position,
    #                             init_ver_velocity,
    #                             init_hor_velocity,
    #                             init_z_velocity)
