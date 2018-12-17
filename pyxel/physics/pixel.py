#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Pixel class to store and transfer charge packets inside detector."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry

cds.enable()


class Pixel:
    """Pixel class defining and storing information of charge packets.

    Pixel properties stored are: charge, position, lost charge.
    """

    def __init__(self,
                 geo: Geometry) -> None:
        """TBW.

        :param geo:
        """
        self.array = np.zeros((geo.row, geo.col), dtype=float)      # todo

    # def fill_pixels_with_charges(self):
    #     """Group charges into packets and fill pixel DataFrame."""
    #     charge_per_pixel = self.detector.charges.get_numbers()
    #
    #     charge_pos_ver = self.detector.charges.get_positions_ver()
    #     charge_pos_hor = self.detector.charges.get_positions_hor()
    #
    #     pixel_index_ver = np.floor_divide(charge_pos_ver, self.detector.geometry.pixel_vert_size).astype(int)
    #     pixel_index_hor = np.floor_divide(charge_pos_hor, self.detector.geometry.pixel_horz_size).astype(int)
    #
    #     self.array = np.zeros((self.detector.geometry.row, self.detector.geometry.col), dtype=float)
    #
    #     for i in range(len(charge_per_pixel)):
    #         self.array[pixel_index_ver[i], pixel_index_hor[i]] += charge_per_pixel[i]
