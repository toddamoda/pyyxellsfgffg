#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! Pixel class to store and transfer charge packets inside detector
"""
import numpy as np
# from astropy import units as u
from astropy.units import cds
import pandas as pd

cds.enable()


class Pixel:
    """
    Pixel class defining and storing information of charge packets of all pixels with their properties
    like stored charge, position, lost charge
    """

    def __init__(self,
                 detector=None):

        self.detector = detector
        self.nextid = 0
        self.frame = pd.DataFrame(columns=['id',
                                           'charge',
                                           'pixel_index_ver',
                                           'pixel_index_hor'])

    def fill_with_charge(self):
        """
        :return:
        """
        charge_per_pixel = self.detector.charges.get_numbers()

        charge_pos_ver = self.detector.charges.get_positions_ver()
        charge_pos_hor = self.detector.charges.get_positions_hor()
        pixel_index_ver = np.floor_divide(charge_pos_ver, self.detector.pix_vert_size)
        pixel_index_hor = np.floor_divide(charge_pos_hor, self.detector.pix_horz_size)

        self.create_pixel(charge_per_pixel,
                          pixel_index_ver,
                          pixel_index_hor)

    def create_pixel(self,
                     charge,
                     pixel_index_ver,
                     pixel_index_hor):
        """
        Creating new pixel charge packet which is stored in a pandas DataFrame

        :return:
        """

        if len(charge) == len(pixel_index_ver) == len(pixel_index_hor):
            elements = len(charge)
        else:
            raise ValueError('List arguments have different lengths')

        # dict
        new_pixel = {'id': range(self.nextid, self.nextid + elements),
                     'charge': charge,
                     'pixel_index_ver': pixel_index_ver,
                     'pixel_index_hor': pixel_index_hor}

        new_pixel_df = pd.DataFrame(new_pixel)
        self.nextid = self.nextid + elements

        # Adding new pixels to the DataFrame
        self.frame = pd.concat([self.frame, new_pixel_df], ignore_index=True)
